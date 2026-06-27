"""
Transaction Risk Agent — Specialist Agent #1
Synchrony PLCC context: credit card transaction pattern analysis.
Bedrock equivalent: Agent Collaborator with Transaction Analytics Action Group
"""

from .base_agent import BaseAgent
from tools.transaction_db import (
    get_transaction_history,
    detect_bust_out_pattern,
    get_peer_comparison,
    get_mcc_risk_profile,
    get_cli_history,
)

SYSTEM_PROMPT = """You are a Transaction Risk Analyst at Synchrony Financial, specializing in credit card
fraud detection and suspicious activity analysis for the Private Label Credit Card (PLCC) portfolio.

Synchrony is a leading consumer financial services company that partners with retailers (Amazon, Lowe's,
Ashley Furniture, BP, etc.) to offer private label and co-branded credit cards. You understand:
- Bust-out fraud: building credit then deliberately defaulting
- Account takeover (ATO): fraudster takes over legitimate cardholder's account
- Synthetic identity fraud: using fabricated or mixed identity to open accounts
- Money mule activity: card used as conduit for third-party money movement

Your role:
- Analyze credit card transaction history for suspicious patterns
- Detect bust-out indicators (gift cards, cash advances, off-network surge, payment cessation)
- Identify ATO patterns (spending inconsistent with history, new city, first-ever cash advances)
- Assess MCC risk profile (high-risk merchant category codes)
- Benchmark against peer group
- Analyze credit limit increase history in context of bust-out suspicion

Process:
1. Retrieve full 90-day transaction history
2. Run bust-out pattern detection
3. Analyze MCC risk profile for recent 30-day window
4. Get peer comparison benchmarks
5. Review credit limit increase history
6. Synthesize into a structured risk narrative

Output format (always follow this):
TRANSACTION RISK FINDINGS:
- Fraud Pattern Suspected: [Bust-Out / ATO / Synthetic Identity / Money Mule / None]
- Key Evidence:
  [Bullet points with specific amounts, dates, merchant names, MCC codes]
- Bust-Out Indicators:
  - Utilization: [X%]
  - Gift Card Purchases: [count, $total]
  - Cash Advances: [count, $total]
  - Payment Cessation: [Yes/No + detail]
  - Contact Status: [Phone/email responsive or dead]
- Spend vs Peer: [Nx above baseline]
- Credit Limit Increase Abuse: [Yes/No + CLI history]
- MCC Risk: [X% of spend in high-risk MCCs]
- Transaction Risk Score: [0-100]
- Risk Rationale: [2-3 sentences with specific evidence]

Use exact amounts, dates, merchant names, and MCC codes from the data."""


TOOLS = [
    {
        "name": "get_transaction_history",
        "description": "Retrieve the complete credit card transaction history including purchases, cash advances, payments, and refunds.",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {"type": "string"},
                "days": {"type": "integer", "default": 90},
            },
            "required": ["account_id"],
        },
    },
    {
        "name": "detect_bust_out_pattern",
        "description": "Run the bust-out fraud detection algorithm: identifies rapid utilization spike, gift card purchases, cash advances, and payment cessation.",
        "input_schema": {
            "type": "object",
            "properties": {"account_id": {"type": "string"}},
            "required": ["account_id"],
        },
    },
    {
        "name": "get_mcc_risk_profile",
        "description": "Analyze Merchant Category Code (MCC) distribution for the recent period. Flags high-risk MCCs like gift cards (5999), cash advances (6010/6011), jewelry (5094).",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {"type": "string"},
                "days": {"type": "integer", "default": 30},
            },
            "required": ["account_id"],
        },
    },
    {
        "name": "get_peer_comparison",
        "description": "Compare this cardholder's spending velocity against the peer group (same card product, similar credit limit).",
        "input_schema": {
            "type": "object",
            "properties": {"account_id": {"type": "string"}},
            "required": ["account_id"],
        },
    },
    {
        "name": "get_cli_history",
        "description": "Retrieve credit limit increase (CLI) history. Rapid CLIs followed by bust-out are a key fraud indicator.",
        "input_schema": {
            "type": "object",
            "properties": {"account_id": {"type": "string"}},
            "required": ["account_id"],
        },
    },
]

TOOL_REGISTRY = {
    "get_transaction_history": get_transaction_history,
    "detect_bust_out_pattern": detect_bust_out_pattern,
    "get_mcc_risk_profile": get_mcc_risk_profile,
    "get_peer_comparison": get_peer_comparison,
    "get_cli_history": get_cli_history,
}


def build(client, model, on_tool_call=None, on_tool_result=None, provider="anthropic") -> BaseAgent:
    return BaseAgent(
        client=client,
        model=model,
        name="Transaction Risk Agent",
        system_prompt=SYSTEM_PROMPT,
        tools=TOOLS,
        tool_registry=TOOL_REGISTRY,
        provider=provider,
        on_tool_call=on_tool_call,
        on_tool_result=on_tool_result,
    )
