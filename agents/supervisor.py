"""
Supervisor / Orchestrator — routes the investigation across specialist agents.

Bedrock AgentCore equivalent:
  - This class = Bedrock Supervisor Agent
  - Each specialist agent = Agent Collaborator
  - The run() method = InvokeAgent with multi-agent collaboration enabled
  - on_step_callback = Bedrock trace events (agent reasoning steps)

In production (Bedrock AgentCore), the supervisor would:
  1. Use bedrock-agent-runtime InvokeAgent API
  2. Each collaborator registered as AgentCollaborator with an ARN
  3. Routing decisions made by Bedrock's built-in orchestration LLM
  4. Traces captured automatically in CloudWatch
"""

import anthropic
from dataclasses import dataclass, field
from typing import Callable, Optional
from tools.risk_scorer import compute_risk_score, RiskAssessment
from tools.transaction_db import (
    get_customer_profile, detect_bust_out_pattern,
    get_peer_comparison, get_mcc_risk_profile,
)
from tools.watchlist import verify_identity, get_device_signals
import agents.transaction_risk as txn_agent_mod
import agents.entity_intel as entity_agent_mod
import agents.aml_typology as typology_agent_mod
import agents.case_writer as case_writer_mod


@dataclass
class InvestigationResult:
    account_id: str
    alert_description: str
    txn_findings: str = ""
    entity_findings: str = ""
    typology_findings: str = ""
    sar_draft: str = ""
    risk_assessment: Optional[RiskAssessment] = None
    tool_calls: list = field(default_factory=list)
    steps: list = field(default_factory=list)   # for UI trace


class Supervisor:
    """
    Orchestrates the multi-agent investigation pipeline.

    Routing strategy: Sequential with context chaining
      Txn Risk Agent → Entity Intel Agent → AML Typology Agent → Case Writer Agent
      (each agent receives the cumulative context from all prior agents)

    Alternative (parallel): Txn + Entity run in parallel, then Typology + Case Writer.
    Sequential chosen here for demo clarity — shows the reasoning chain.
    """

    def __init__(self, api_key: str, model: str, provider: str = "anthropic", on_step: Optional[Callable] = None):
        self.provider = provider
        if provider == "groq":
            from groq import Groq
            self.client = Groq(api_key=api_key)
        else:
            self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.on_step = on_step or (lambda step, detail: None)

    def _make_step_callback(self, result: InvestigationResult, agent_name: str):
        """Returns tool-call callbacks that stream updates to the UI."""
        def on_tool_call(tool_name, tool_input):
            step = {
                "type": "tool_call",
                "agent": agent_name,
                "tool": tool_name,
                "input": tool_input,
            }
            result.steps.append(step)
            result.tool_calls.append(step)
            self.on_step("tool_call", {"agent": agent_name, "tool": tool_name, "input": tool_input})

        def on_tool_result(tool_name, tool_output):
            step = {"type": "tool_result", "agent": agent_name, "tool": tool_name}
            result.steps.append(step)
            self.on_step("tool_result", {"agent": agent_name, "tool": tool_name})

        return on_tool_call, on_tool_result

    def investigate(self, account_id: str, alert_description: str) -> InvestigationResult:
        result = InvestigationResult(account_id=account_id, alert_description=alert_description)

        # ── Step 1: Transaction Risk Agent ────────────────────────────────────
        self.on_step("agent_start", {"agent": "Transaction Risk Agent",
                                     "message": "Retrieving transaction history and detecting fraud patterns..."})
        on_call, on_result = self._make_step_callback(result, "Transaction Risk Agent")
        txn_agent = txn_agent_mod.build(self.client, self.model, on_call, on_result, self.provider)

        txn_output = txn_agent.run(
            user_message=f"Investigate account {account_id}. Alert: {alert_description}. "
                         f"Retrieve the transaction history, detect bust-out patterns, analyze MCC risk, "
                         f"compare to peer group, and review CLI history.",
        )
        result.txn_findings = txn_output["findings"]
        self.on_step("agent_complete", {"agent": "Transaction Risk Agent", "summary": result.txn_findings[:200]})

        # ── Step 2: Entity Intelligence Agent ─────────────────────────────────
        self.on_step("agent_start", {"agent": "Entity Intelligence Agent",
                                     "message": "Profiling cardholder, screening watchlists, checking device signals..."})
        on_call, on_result = self._make_step_callback(result, "Entity Intelligence Agent")
        entity_agent = entity_agent_mod.build(self.client, self.model, on_call, on_result, self.provider)

        entity_output = entity_agent.run(
            user_message=f"Investigate the cardholder for account {account_id}. "
                         f"Check identity verification, fraud registry, OFAC, FinCEN 314(a), device signals, and related accounts.",
            context=f"Transaction Risk Findings:\n{result.txn_findings}",
        )
        result.entity_findings = entity_output["findings"]
        self.on_step("agent_complete", {"agent": "Entity Intelligence Agent", "summary": result.entity_findings[:200]})

        # ── Step 3: AML Typology Agent (RAG) ──────────────────────────────────
        self.on_step("agent_start", {"agent": "AML Typology Agent",
                                     "message": "Searching AML knowledge base for pattern matches..."})
        on_call, on_result = self._make_step_callback(result, "AML Typology Agent")
        typology_agent = typology_agent_mod.build(self.client, self.model, on_call, on_result, self.provider)

        typology_output = typology_agent.run(
            user_message=f"Based on the transaction and entity findings below, search the AML typology "
                         f"knowledge base to identify the best-matching fraud patterns. "
                         f"Run at least 2 targeted searches.",
            context=f"Transaction Risk Findings:\n{result.txn_findings}\n\n"
                    f"Entity Intelligence Findings:\n{result.entity_findings}",
        )
        result.typology_findings = typology_output["findings"]
        self.on_step("agent_complete", {"agent": "AML Typology Agent", "summary": result.typology_findings[:200]})

        # ── Step 4: Compute risk score (rule-based engine) ────────────────────
        self.on_step("agent_start", {"agent": "Risk Scoring Engine",
                                     "message": "Computing explainable risk score across all dimensions..."})
        try:
            customer = get_customer_profile(account_id)
            bust = detect_bust_out_pattern(account_id)
            peer = get_peer_comparison(account_id)
            mcc = get_mcc_risk_profile(account_id)
            identity = verify_identity(account_id)
            device = get_device_signals(account_id)

            result.risk_assessment = compute_risk_score(
                txn_data={},
                customer_data=customer,
                bust_out_data=bust,
                peer_data=peer,
                identity_data=identity,
                device_data=device,
                mcc_data=mcc,
            )
        except Exception:
            pass
        self.on_step("agent_complete", {"agent": "Risk Scoring Engine",
                                        "summary": f"Score: {result.risk_assessment.overall_score if result.risk_assessment else 'N/A'}"})

        # ── Step 5: Case Writer Agent ──────────────────────────────────────────
        self.on_step("agent_start", {"agent": "Case Writer Agent",
                                     "message": "Drafting SAR narrative and investigation summary..."})
        on_call, on_result = self._make_step_callback(result, "Case Writer Agent")
        writer_agent = case_writer_mod.build(self.client, self.model, on_call, on_result, self.provider)

        risk_summary = ""
        if result.risk_assessment:
            ra = result.risk_assessment
            risk_summary = (
                f"\nRisk Score: {ra.overall_score}/100 ({ra.risk_level})\n"
                f"Fraud Type: {ra.fraud_type}\n"
                f"SAR Recommended: {'Yes' if ra.sar_recommended else 'No'}\n"
            )

        writer_output = writer_agent.run(
            user_message=f"Write the SAR narrative and investigation summary for account {account_id}.\n"
                         f"Alert: {alert_description}\n{risk_summary}",
            context=f"Transaction Risk Findings:\n{result.txn_findings}\n\n"
                    f"Entity Intelligence Findings:\n{result.entity_findings}\n\n"
                    f"AML Typology Analysis:\n{result.typology_findings}",
        )
        result.sar_draft = writer_output["findings"]
        self.on_step("agent_complete", {"agent": "Case Writer Agent", "summary": "SAR narrative complete"})

        self.on_step("investigation_complete", {"account_id": account_id})
        return result
