"""
FinGuard — Synchrony Transaction Monitoring Intelligence Platform
Autonomous multi-agent AML/Fraud investigation powered by Agentic AI.

Demo architecture mirrors Amazon Bedrock AgentCore:
  Supervisor Agent → [Transaction Risk | Entity Intel | AML Typology | Case Writer]
"""

import os
import time
import streamlit as st
from streamlit_extras.colored_header import colored_header  # type: ignore

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinGuard | Synchrony",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .stApp { background-color: #0f1117; }

    /* Alert card */
    .alert-card {
        background: linear-gradient(135deg, #1a1f2e 0%, #1e2538 100%);
        border: 1px solid #dc3545;
        border-left: 4px solid #dc3545;
        border-radius: 8px;
        padding: 18px 20px;
        margin-bottom: 16px;
    }
    .alert-card h4 { color: #dc3545; margin: 0 0 8px 0; font-size: 13px; letter-spacing: 1px; }
    .alert-card h2 { color: #ffffff; margin: 0 0 12px 0; font-size: 18px; }
    .alert-meta { color: #9aa3b0; font-size: 13px; line-height: 1.8; }
    .alert-meta span { color: #e0e6f0; font-weight: 600; }

    /* Risk score gauge */
    .risk-badge-CRITICAL { background: #dc3545; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; }
    .risk-badge-HIGH { background: #fd7e14; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; }
    .risk-badge-MEDIUM { background: #ffc107; color: #1a1f2e; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; }
    .risk-badge-LOW { background: #28a745; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; }

    /* Agent step cards */
    .step-card {
        background: #1a1f2e;
        border: 1px solid #2d3748;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 6px 0;
        font-size: 13px;
    }
    .step-tool {
        background: #162032;
        border: 1px solid #1e4470;
        border-radius: 4px;
        padding: 8px 12px;
        margin: 4px 0 4px 24px;
        font-size: 12px;
        font-family: monospace;
        color: #7ab3e0;
    }

    /* Metric cards */
    .metric-row {
        display: flex;
        gap: 12px;
        margin: 12px 0;
    }
    .metric-card {
        flex: 1;
        background: #1a1f2e;
        border: 1px solid #2d3748;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .metric-value { font-size: 28px; font-weight: 700; color: #7ab3e0; }
    .metric-label { font-size: 11px; color: #9aa3b0; margin-top: 4px; letter-spacing: 0.5px; }

    /* SAR section */
    .sar-box {
        background: #12181f;
        border: 1px solid #2d3748;
        border-radius: 8px;
        padding: 20px;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        line-height: 1.7;
        color: #c8d6e5;
        white-space: pre-wrap;
    }

    /* HITL panel */
    .hitl-panel {
        background: linear-gradient(135deg, #1a1f2e, #1e2538);
        border: 2px solid #ffc107;
        border-radius: 10px;
        padding: 24px;
        margin-top: 20px;
    }
    .hitl-title { color: #ffc107; font-size: 16px; font-weight: 700; margin-bottom: 8px; }

    /* Bedrock mapping table */
    .bedrock-table { width: 100%; border-collapse: collapse; font-size: 13px; }
    .bedrock-table th { background: #1a1f2e; color: #7ab3e0; padding: 10px 14px; text-align: left; border-bottom: 1px solid #2d3748; }
    .bedrock-table td { padding: 9px 14px; border-bottom: 1px solid #1e2538; color: #c8d6e5; vertical-align: top; }
    .bedrock-table tr:hover td { background: #1e2538; }

    /* Stacked factor bars */
    .factor-bar-bg { background: #2d3748; border-radius: 4px; height: 8px; margin: 4px 0; }
    .factor-bar-fill { height: 8px; border-radius: 4px; }

    div[data-testid="stButton"] button {
        border-radius: 6px;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
</style>
""", unsafe_allow_html=True)

# ── Alert definitions (Synchrony PLCC scenarios) ─────────────────────────────
ALERTS = {
    "CC-4821": {
        "label": "🚨 CC-4821 — Bust-Out Fraud Suspected",
        "account_id": "CC-4821",
        "cardholder": "James Holloway",
        "product": "Synchrony Amazon Store Card",
        "alert_id": "ALT-2026-0441",
        "priority": "HIGH",
        "description": (
            "Account CC-4821 (James Holloway, Synchrony Amazon Store Card, $8,000 limit) shows a "
            "bust-out fraud pattern. In the past 10 days: 3 gift card purchases ($3,162), "
            "1 cash advance ($1,500), 4 off-network purchases ($3,230) — total new charges $7,892 "
            "(98.7% utilization). Primary phone is disconnected; email bouncing. "
            "Account received 2 CLIs within 60 days of opening. SSN issuance date anomaly flagged at onboarding."
        ),
        "triggered_rules": ["RULE-BUF-001: Bust-out utilization spike", "RULE-GFT-002: Gift card velocity", "RULE-CNT-003: Contact unreachable"],
        "exposure": "$7,892",
        "days_open": 137,
    },
    "CC-7734": {
        "label": "⚠️ CC-7734 — Account Takeover Suspected",
        "account_id": "CC-7734",
        "cardholder": "Maria Santos",
        "product": "Synchrony Lowe's Advantage Card",
        "alert_id": "ALT-2026-0447",
        "priority": "HIGH",
        "description": (
            "Account CC-7734 (Maria Santos, Synchrony Lowe's Card, $12,000 limit) — 5-year excellent history — "
            "shows account takeover indicators. 3 contact fields changed in 24 hours (address: Tampa→Orlando, "
            "phone, email). Within 5 days: $1,900 gift card purchase, two cash advances totaling $5,800 at "
            "Orlando ATMs (inconsistent with cardholder's Tampa profile), $2,220 off-network purchases. "
            "New device + new city login detected post-contact-change."
        ),
        "triggered_rules": ["RULE-ATO-001: Multi-field contact change", "RULE-ATO-002: New device post-change", "RULE-CA-001: Cash advance surge"],
        "exposure": "$9,920",
        "days_open": 1107,
    },
    "CC-2291": {
        "label": "🔶 CC-2291 — Money Mule Activity",
        "account_id": "CC-2291",
        "cardholder": "Derek Okafor",
        "product": "Synchrony Ashley Advantage Card",
        "alert_id": "ALT-2026-0452",
        "priority": "MEDIUM",
        "description": (
            "Account CC-2291 (Derek Okafor, Synchrony Ashley Card, $5,000 limit) received an "
            "anomalous $4,800 payment from 'Keystone Ventures LLC' — a third-party business entity "
            "with no link to the cardholder. Within 4 days: $1,800 jewelry purchase (MCC 5094), "
            "$1,600 precious metals, $1,200 cash advance, $220 Western Union transfer. "
            "Classic money mule: third-party pays off card, cardholder converts freed credit to liquid assets."
        ),
        "triggered_rules": ["RULE-MUL-001: Third-party payment", "RULE-MCC-001: High-risk MCC cluster", "RULE-WU-001: Money transfer service"],
        "exposure": "$5,000",
        "days_open": 309,
    },
}


def get_api_key() -> str:
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return os.getenv("ANTHROPIC_API_KEY", "")


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ FinGuard")
    st.markdown("**Synchrony Transaction Monitoring**")
    st.markdown("*Agentic AI Investigation Platform*")
    st.divider()

    st.markdown("### Alert Queue")
    for aid, alert in ALERTS.items():
        priority_color = {"HIGH": "🔴", "MEDIUM": "🟡"}.get(alert["priority"], "⚪")
        if st.button(f"{priority_color} {alert['label']}", key=f"btn_{aid}", use_container_width=True):
            st.session_state.selected_alert = aid
            st.session_state.investigation_result = None
            st.session_state.hitl_decision = None
            st.session_state.step_log = []

    st.divider()
    st.markdown("### Configuration")
    api_key = st.text_input("Anthropic API Key", value=get_api_key(), type="password",
                             help="Get a free key at console.anthropic.com")
    model = st.selectbox("Model", [
        "claude-3-5-sonnet-20241022",
        "claude-3-haiku-20240307",
    ], help="claude-3-5-sonnet = production quality | haiku = faster demo")
    st.session_state.api_key = api_key
    st.session_state.model = model

    st.divider()
    st.caption("**Architecture**: Multi-Agent Orchestration")
    st.caption("**RAG**: ChromaDB (AML Typologies)")
    st.caption("**HITL**: Human-in-the-Loop approval")
    st.caption("**Mirrors**: Amazon Bedrock AgentCore")


# ── Main content tabs ─────────────────────────────────────────────────────────
tab_investigate, tab_arch, tab_bedrock = st.tabs([
    "🔍 Investigate", "🏗️ Architecture", "☁️ Bedrock Production Code"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: INVESTIGATE
# ══════════════════════════════════════════════════════════════════════════════
with tab_investigate:
    if "selected_alert" not in st.session_state:
        st.session_state.selected_alert = "CC-4821"
    if "investigation_result" not in st.session_state:
        st.session_state.investigation_result = None
    if "hitl_decision" not in st.session_state:
        st.session_state.hitl_decision = None
    if "step_log" not in st.session_state:
        st.session_state.step_log = []

    alert = ALERTS[st.session_state.selected_alert]

    col_left, col_right = st.columns([1, 2], gap="large")

    # ── Left: Alert Details ───────────────────────────────────────────────────
    with col_left:
        st.markdown(f"""
        <div class="alert-card">
            <h4>⚠️ ACTIVE ALERT — {alert['priority']} PRIORITY</h4>
            <h2>{alert['cardholder']}</h2>
            <div class="alert-meta">
                <b>Account:</b> <span>{alert['account_id']}</span><br>
                <b>Product:</b> <span>{alert['product']}</span><br>
                <b>Alert ID:</b> <span>{alert['alert_id']}</span><br>
                <b>Exposure:</b> <span>{alert['exposure']}</span><br>
                <b>Days Open:</b> <span>{alert['days_open']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Alert Description**")
        st.markdown(f"<div style='background:#1a1f2e;border:1px solid #2d3748;border-radius:6px;padding:14px;font-size:13px;color:#c8d6e5;line-height:1.6'>{alert['description']}</div>", unsafe_allow_html=True)

        st.markdown("**Triggered Rules**")
        for rule in alert["triggered_rules"]:
            st.markdown(f"- `{rule}`")

        st.markdown("")
        if not st.session_state.api_key:
            st.error("Add your Anthropic API key in the sidebar to run the investigation.")
        else:
            investigate_clicked = st.button(
                "🤖 Launch Agent Investigation",
                type="primary",
                use_container_width=True,
                disabled=not bool(st.session_state.api_key),
            )

    # ── Right: Investigation Output ───────────────────────────────────────────
    with col_right:
        if "investigate_clicked" in dir() and investigate_clicked:
            st.session_state.investigation_result = None
            st.session_state.hitl_decision = None
            st.session_state.step_log = []

            from agents.supervisor import Supervisor

            # Live step log container
            step_container = st.container()
            with step_container:
                st.markdown("### 🤖 Agent Investigation")
                progress_box = st.empty()
                steps_box = st.empty()

            step_log_display = []

            def on_step(event_type, data):
                agent = data.get("agent", "")
                if event_type == "agent_start":
                    step_log_display.append({
                        "type": "agent_start", "agent": agent,
                        "message": data.get("message", "")
                    })
                elif event_type == "tool_call":
                    step_log_display.append({
                        "type": "tool_call", "agent": agent,
                        "tool": data.get("tool", ""), "input": data.get("input", {})
                    })
                elif event_type == "tool_result":
                    step_log_display.append({"type": "tool_result", "agent": agent, "tool": data.get("tool", "")})
                elif event_type == "agent_complete":
                    step_log_display.append({"type": "agent_complete", "agent": agent})

                # Render current steps
                html = ""
                for s in step_log_display[-20:]:
                    if s["type"] == "agent_start":
                        html += f'<div class="step-card">▶ <b style="color:#7ab3e0">{s["agent"]}</b> &nbsp;— {s["message"]}</div>'
                    elif s["type"] == "tool_call":
                        inp_preview = str(s.get("input", ""))[:80]
                        html += f'<div class="step-tool">🔧 <b>{s["tool"]}</b>({inp_preview})</div>'
                    elif s["type"] == "tool_result":
                        html += f'<div class="step-tool" style="color:#68d391">✓ {s["tool"]} → result received</div>'
                    elif s["type"] == "agent_complete":
                        html += f'<div class="step-card" style="border-color:#28a745">✅ <b style="color:#68d391">{s["agent"]}</b> complete</div>'

                steps_box.markdown(html, unsafe_allow_html=True)

            progress_box.info("Initialising multi-agent investigation pipeline...")

            try:
                supervisor = Supervisor(
                    api_key=st.session_state.api_key,
                    model=st.session_state.model,
                    on_step=on_step,
                )
                result = supervisor.investigate(alert["account_id"], alert["description"])
                st.session_state.investigation_result = result
                st.session_state.step_log = step_log_display
                progress_box.success("✅ Investigation complete — review findings below")
            except Exception as e:
                progress_box.error(f"Investigation failed: {e}")
                st.stop()

        # ── Show results if available ─────────────────────────────────────────
        if st.session_state.investigation_result:
            result = st.session_state.investigation_result

            # Risk score banner
            if result.risk_assessment:
                ra = result.risk_assessment
                score_color = {"CRITICAL": "#dc3545", "HIGH": "#fd7e14", "MEDIUM": "#ffc107", "LOW": "#28a745"}.get(ra.risk_level, "#7ab3e0")
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#1a1f2e,#1e2538);border:1px solid {score_color};border-radius:10px;padding:20px;margin:16px 0">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <div>
                            <div style="font-size:12px;color:#9aa3b0;letter-spacing:1px;margin-bottom:4px">OVERALL RISK SCORE</div>
                            <div style="font-size:48px;font-weight:800;color:{score_color};line-height:1">{ra.overall_score}</div>
                            <div style="font-size:11px;color:#9aa3b0">/100</div>
                        </div>
                        <div style="text-align:right">
                            <div class="risk-badge-{ra.risk_level}" style="margin-bottom:8px">{ra.risk_level}</div>
                            <div style="font-size:13px;color:#e0e6f0;margin-top:8px"><b>Fraud Type:</b> {ra.fraud_type}</div>
                            <div style="font-size:13px;color:{'#dc3545' if ra.sar_recommended else '#28a745'};margin-top:4px">
                                {'⚡ SAR FILING RECOMMENDED' if ra.sar_recommended else '✓ SAR Not Required'}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Risk factor breakdown
                with st.expander("📊 Risk Factor Breakdown (Explainable AI)", expanded=False):
                    for f in ra.factors:
                        bar_color = "#dc3545" if f.score >= 70 else "#fd7e14" if f.score >= 40 else "#28a745"
                        st.markdown(f"""
                        <div style="margin:10px 0">
                            <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px">
                                <span style="color:#e0e6f0"><b>{f.name}</b> (weight: {int(f.weight*100)}%)</span>
                                <span style="color:{bar_color};font-weight:700">{f.score}/100</span>
                            </div>
                            <div class="factor-bar-bg">
                                <div class="factor-bar-fill" style="width:{f.score}%;background:{bar_color}"></div>
                            </div>
                            <div style="font-size:11px;color:#9aa3b0;margin-top:3px">{f.detail}</div>
                        </div>
                        """, unsafe_allow_html=True)

            # Agent findings tabs
            f_tab1, f_tab2, f_tab3 = st.tabs([
                "📊 Transaction Risk", "👤 Entity Intelligence", "📚 AML Typology"
            ])
            with f_tab1:
                st.markdown(f"<div class='sar-box'>{result.txn_findings}</div>", unsafe_allow_html=True)
            with f_tab2:
                st.markdown(f"<div class='sar-box'>{result.entity_findings}</div>", unsafe_allow_html=True)
            with f_tab3:
                st.markdown(f"<div class='sar-box'>{result.typology_findings}</div>", unsafe_allow_html=True)

            # SAR Draft
            st.markdown("### 📄 SAR Draft")
            sar_text = st.text_area(
                "SAR Narrative (editable before filing)",
                value=result.sar_draft,
                height=350,
                key="sar_text",
            )

            # ── HUMAN-IN-THE-LOOP PANEL ───────────────────────────────────────
            if st.session_state.hitl_decision is None and result.risk_assessment and result.risk_assessment.sar_recommended:
                st.markdown("""
                <div class="hitl-panel">
                    <div class="hitl-title">⚠️ HUMAN REVIEW REQUIRED — SAR Filing Authorization</div>
                    <div style="color:#c8d6e5;font-size:13px;line-height:1.7;margin-bottom:16px">
                        The automated investigation recommends SAR filing. Per Synchrony's Human-in-the-Loop
                        (HITL) policy for regulated banking decisions, a qualified BSA Analyst must review
                        and authorize filing. Please review the SAR draft above and approve or dismiss.
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col_a, col_b, col_c = st.columns([1, 1, 2])
                with col_a:
                    if st.button("✅ APPROVE SAR", type="primary", use_container_width=True):
                        st.session_state.hitl_decision = "APPROVED"
                        st.rerun()
                with col_b:
                    if st.button("❌ DISMISS", use_container_width=True):
                        st.session_state.hitl_decision = "DISMISSED"
                        st.rerun()

            elif st.session_state.hitl_decision == "APPROVED":
                st.success(
                    f"✅ **SAR Approved** — Alert {alert['alert_id']} filed to FinCEN. "
                    f"Case reference: SAR-2026-{alert['account_id'][-4:]}. "
                    "Account frozen pending investigation. BSA Officer notified."
                )
                st.markdown(f"""
                | Field | Value |
                |---|---|
                | SAR ID | SAR-2026-{alert['account_id'][-4:]} |
                | Filing Deadline | 2026-07-27 |
                | Amount Involved | {alert['exposure']} |
                | Analyst Decision | Approved |
                | Timestamp | {time.strftime('%Y-%m-%d %H:%M:%S')} |
                | Account Action | Frozen — collections referral initiated |
                """)

            elif st.session_state.hitl_decision == "DISMISSED":
                st.warning(
                    "Investigation dismissed. Case closed with no SAR filing. "
                    "Reason will be logged for audit trail (SR 11-7 compliance)."
                )

            elif result.risk_assessment and not result.risk_assessment.sar_recommended:
                st.info(
                    f"Risk score {result.risk_assessment.overall_score}/100 ({result.risk_assessment.risk_level}) — "
                    "SAR filing not recommended at this time. Account placed on enhanced monitoring."
                )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: ARCHITECTURE
# ══════════════════════════════════════════════════════════════════════════════
with tab_arch:
    st.markdown("## FinGuard Architecture — Multi-Agent Orchestration")
    st.markdown("""
    <div style="background:#1a1f2e;border:1px solid #2d3748;border-radius:10px;padding:24px;font-family:monospace;font-size:13px;line-height:2;color:#c8d6e5">

    <div style="color:#7ab3e0;font-size:15px;font-weight:700;margin-bottom:12px">AGENT GRAPH</div>

                    ┌────────────────────────────────────────┐
                    │   Synchrony Analyst (Streamlit UI)     │
                    │   [Alert] → [Investigate] → [HITL]     │
                    └─────────────────┬──────────────────────┘
                                      │
                    ┌─────────────────▼──────────────────────┐
                    │        SUPERVISOR AGENT                │
                    │   Orchestrates investigation flow      │
                    │   Routes context between specialists   │
                    │   ≡ Bedrock Supervisor Agent           │
                    └──────┬─────────┬────────┬─────────────┘
                           │         │        │         │
             ┌─────────────▼─┐  ┌────▼───┐ ┌─▼──────┐ ┌▼──────────┐
             │  TRANSACTION  │  │ ENTITY │ │  AML   │ │   CASE    │
             │   RISK AGENT  │  │ INTEL  │ │TYPOLOGY│ │  WRITER   │
             │               │  │ AGENT  │ │ AGENT  │ │  AGENT    │
             │ ≡ Agent       │  │        │ │  RAG   │ │           │
             │   Collaborator│  │        │ │        │ │           │
             └──────┬────────┘  └───┬────┘ └───┬────┘ └───────────┘
                    │               │          │
             ┌──────▼──────┐ ┌─────▼──────┐ ┌─▼────────────────┐
             │ Action      │ │ Action     │ │ Knowledge Base   │
             │ Group Tools │ │ Group Tools│ │ (ChromaDB)       │
             │             │ │            │ │ ≡ Bedrock KB     │
             │ get_txn_    │ │ verify_    │ │                  │
             │ history     │ │ identity   │ │ FATF Typologies  │
             │ detect_bust │ │ check_ofac │ │ FinCEN Advisories│
             │ get_peer_   │ │ check_314a │ │ Bust-Out Fraud   │
             │ comparison  │ │ get_device │ │ ATO Patterns     │
             │ get_mcc_    │ │ get_linked │ │                  │
             │ risk_profile│ │ accounts   │ │                  │
             └─────────────┘ └────────────┘ └──────────────────┘

              ┌──────────────────────────────────────────────────┐
              │               GUARDRAILS                        │
              │  • Max 8 tool-call iterations per agent         │
              │  • PII masked in logs (SSN, DOB, card number)  │
              │  • SAR filing requires human approval (HITL)    │
              │  • ≡ Bedrock Guardrails + Human Loop            │
              └──────────────────────────────────────────────────┘
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## Bedrock AgentCore Mapping")
    st.markdown("""
    <table class="bedrock-table">
        <tr>
            <th>FinGuard Component</th>
            <th>Amazon Bedrock AgentCore Equivalent</th>
            <th>Key API / Resource</th>
        </tr>
        <tr>
            <td><b>Supervisor class</b><br><small>Orchestrates investigation flow</small></td>
            <td>Bedrock Supervisor Agent</td>
            <td><code>bedrock-agent:CreateAgent</code> (SUPERVISOR mode)</td>
        </tr>
        <tr>
            <td><b>BaseAgent class</b><br><small>Tool-use agentic loop</small></td>
            <td>Bedrock Agent Collaborator</td>
            <td><code>bedrock-agent:AssociateAgentCollaborator</code></td>
        </tr>
        <tr>
            <td><b>Tool functions</b><br><small>get_transaction_history, detect_bust_out, etc.</small></td>
            <td>Action Group + Lambda Function</td>
            <td><code>bedrock-agent:CreateAgentActionGroup</code> → Lambda ARN</td>
        </tr>
        <tr>
            <td><b>ChromaDB + typology .txt files</b><br><small>RAG knowledge base</small></td>
            <td>Bedrock Knowledge Base</td>
            <td><code>bedrock-agent:CreateKnowledgeBase</code> (S3 → Titan Embeddings → OpenSearch)</td>
        </tr>
        <tr>
            <td><b>search_typologies() tool</b><br><small>Semantic search in agent</small></td>
            <td>KnowledgeBase Action Group</td>
            <td><code>bedrock-agent-runtime:RetrieveAndGenerate</code></td>
        </tr>
        <tr>
            <td><b>on_step callback</b><br><small>Streaming agent trace to UI</small></td>
            <td>Bedrock Agent Trace</td>
            <td><code>InvokeAgentRequest.enableTrace=True</code></td>
        </tr>
        <tr>
            <td><b>HITL Streamlit buttons</b><br><small>Approve/Dismiss SAR</small></td>
            <td>Bedrock Human Loop</td>
            <td><code>sagemaker-a2i-runtime:StartHumanLoop</code></td>
        </tr>
        <tr>
            <td><b>max_iterations guard</b><br><small>Loop limit in BaseAgent</small></td>
            <td>Bedrock Guardrails</td>
            <td><code>bedrock:CreateGuardrail</code> (denied topics + length limits)</td>
        </tr>
        <tr>
            <td><b>Anthropic Claude API</b><br><small>LLM backend for all agents</small></td>
            <td>Bedrock Model</td>
            <td><code>anthropic.claude-3-5-sonnet-20241022-v2:0</code> on Bedrock</td>
        </tr>
        <tr>
            <td><b>session_state context chaining</b><br><small>Agent-to-agent context passing</small></td>
            <td>Bedrock Memory / Agent Context</td>
            <td><code>bedrock-agent:CreateAgentMemory</code> (session-level)</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)

    st.markdown("## Why Multi-Agent for Transaction Monitoring?")
    cols = st.columns(3)
    with cols[0]:
        st.info("**Separation of Concerns**\n\nEach agent is independently auditable (SR 11-7). Transaction Risk uses only card data tools; Entity Intel uses only identity tools. Clear provenance for model risk review.")
    with cols[1]:
        st.info("**Specialised Expertise**\n\nTransaction patterns, watchlist screening, and SAR writing require fundamentally different context windows. Monolithic LLM calls get confused and lose focus.")
    with cols[2]:
        st.info("**Scalability**\n\nSynchrony processes millions of alerts. With Bedrock, Transaction Risk and Entity Intel agents can run in parallel, reducing total investigation latency by ~50%.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: BEDROCK PRODUCTION CODE
# ══════════════════════════════════════════════════════════════════════════════
with tab_bedrock:
    st.markdown("## Production Code — Amazon Bedrock AgentCore")
    st.markdown("""
    > The code below is exactly how this demo would be deployed in production at Synchrony using
    > Amazon Bedrock AgentCore. The demo uses `anthropic` Python SDK directly (free);
    > switching to Bedrock requires only changing the client — same Claude model, same tool schemas.
    """)

    with st.expander("1️⃣ Create the Supervisor Agent (Bedrock)", expanded=True):
        st.code("""
import boto3

bedrock_agent = boto3.client("bedrock-agent", region_name="us-east-1")

# Create supervisor agent
supervisor = bedrock_agent.create_agent(
    agentName="fingurd-supervisor",
    agentResourceRoleArn="arn:aws:iam::ACCOUNT:role/BedrockAgentRole",
    foundationModel="anthropic.claude-3-5-sonnet-20241022-v2:0",
    instruction=\"\"\"
        You are the FinGuard investigation supervisor at Synchrony Financial.
        Coordinate transaction risk analysis, entity intelligence, AML typology matching,
        and SAR drafting by delegating to specialist agent collaborators.
        Synthesize their findings and route the final case for human review.
    \"\"\",
    agentCollaboration="SUPERVISOR",  # ← enables multi-agent mode
)

supervisor_id = supervisor["agent"]["agentId"]
""", language="python")

    with st.expander("2️⃣ Register Transaction Risk Agent as Collaborator"):
        st.code("""
# Create Transaction Risk sub-agent (with Action Group)
txn_agent = bedrock_agent.create_agent(
    agentName="fingurd-txn-risk",
    foundationModel="anthropic.claude-3-5-sonnet-20241022-v2:0",
    instruction="You are a Transaction Risk Analyst. Detect bust-out fraud patterns...",
)

# Create Action Group (backed by Lambda)
bedrock_agent.create_agent_action_group(
    agentId=txn_agent["agent"]["agentId"],
    agentVersion="DRAFT",
    actionGroupName="TransactionAnalyticsActions",
    actionGroupExecutor={"lambda": "arn:aws:lambda:us-east-1:ACCOUNT:function:fingurd-txn-tools"},
    functionSchema={
        "functions": [
            {
                "name": "get_transaction_history",
                "description": "Retrieve credit card transaction history",
                "parameters": {
                    "account_id": {"type": "string", "required": True},
                    "days": {"type": "integer", "required": False},
                },
            },
            {
                "name": "detect_bust_out_pattern",
                "description": "Run bust-out fraud detection algorithm",
                "parameters": {
                    "account_id": {"type": "string", "required": True},
                },
            },
        ]
    },
)

# Associate as collaborator with supervisor
bedrock_agent.associate_agent_collaborator(
    agentId=supervisor_id,
    agentVersion="DRAFT",
    agentDescriptor={"aliasArn": f"arn:aws:bedrock:us-east-1:ACCOUNT:agent-alias/{txn_agent['agent']['agentId']}/TSTALIASID"},
    collaboratorName="TransactionRiskAgent",
    collaborationInstruction="Analyze transaction patterns for bust-out fraud, ATO, and suspicious activity.",
)
""", language="python")

    with st.expander("3️⃣ Create Bedrock Knowledge Base (AML Typologies)"):
        st.code("""
# Knowledge Base = ChromaDB in this demo
# In production: S3 + Titan Embeddings + OpenSearch Serverless

bedrock_agent.create_knowledge_base(
    name="fingurd-aml-typologies",
    description="FATF typologies, FinCEN advisories, Synchrony fraud patterns",
    roleArn="arn:aws:iam::ACCOUNT:role/BedrockKBRole",
    knowledgeBaseConfiguration={
        "type": "VECTOR",
        "vectorKnowledgeBaseConfiguration": {
            "embeddingModelArn": "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0"
        },
    },
    storageConfiguration={
        "type": "OPENSEARCH_SERVERLESS",
        "opensearchServerlessConfiguration": {
            "collectionArn": "arn:aws:aoss:us-east-1:ACCOUNT:collection/fingurd-vectors",
            "vectorIndexName": "aml-typologies-index",
            "fieldMapping": {
                "vectorField": "embedding",
                "textField": "content",
                "metadataField": "metadata",
            },
        },
    },
)

# Sync typology documents from S3
bedrock_agent.start_ingestion_job(
    knowledgeBaseId="KB-ID",
    dataSourceId="DS-ID",
)
""", language="python")

    with st.expander("4️⃣ Invoke the Supervisor Agent (runtime)"):
        st.code("""
import boto3
import json

runtime = boto3.client("bedrock-agent-runtime", region_name="us-east-1")

# Invoke with trace enabled (mirrors our on_step callback)
response = runtime.invoke_agent(
    agentId=supervisor_id,
    agentAliasId="TSTALIASID",
    sessionId="investigation-CC-4821-2026-06-27",
    inputText=\"\"\"
        Investigate account CC-4821 (James Holloway, Synchrony Amazon Store Card).
        Alert: Bust-out fraud suspected. Utilization 98.7%. Phone disconnected.
        7 high-risk transactions in 10 days totaling $7,892.
    \"\"\",
    enableTrace=True,  # ← streams agent reasoning steps (our on_step equivalent)
)

# Stream the response + trace events
for event in response["completion"]:
    if "chunk" in event:
        print(event["chunk"]["bytes"].decode())
    elif "trace" in event:
        trace = event["trace"]["trace"]
        if "orchestrationTrace" in trace:
            step = trace["orchestrationTrace"]
            if "rationale" in step:
                print(f"Reasoning: {step['rationale']['text']}")
            if "invocationInput" in step:
                print(f"Tool call: {step['invocationInput']}")
""", language="python")

    with st.expander("5️⃣ Guardrails (PII protection + compliance)"):
        st.code("""
bedrock.create_guardrail(
    name="fingurd-compliance-guardrail",
    description="Protect PII, prevent hallucination in SAR narratives",
    sensitiveInformationPolicyConfig={
        "piiEntitiesConfig": [
            {"type": "SSN", "action": "ANONYMIZE"},
            {"type": "CREDIT_DEBIT_CARD_NUMBER", "action": "ANONYMIZE"},
            {"type": "EMAIL", "action": "ANONYMIZE"},
            {"type": "PHONE", "action": "ANONYMIZE"},
        ]
    },
    topicPolicyConfig={
        "topicsConfig": [
            {
                "name": "investment-advice",
                "definition": "Do not provide investment or financial advice",
                "type": "DENY",
            }
        ]
    },
    contentPolicyConfig={
        "filtersConfig": [{"type": "HATE", "inputStrength": "HIGH", "outputStrength": "HIGH"}]
    },
)
""", language="python")

    st.markdown("""
    ---
    ### Cost Estimate for Production (Bedrock)
    | Component | Bedrock Resource | Estimated Monthly Cost |
    |---|---|---|
    | Supervisor + 3 Collaborators | Claude 3.5 Sonnet (~2K tokens/investigation) | ~$0.05/investigation |
    | AML Knowledge Base | Titan Embeddings v2 + OpenSearch Serverless | ~$150/month (fixed) |
    | Storage | S3 (typology docs) | ~$1/month |
    | Lambda (Action Groups) | ~100ms per tool call | ~$5/month for 1M alerts |
    | **Total for 50K investigations/month** | | **~$2,650/month** |

    > Compared to: manual analyst cost = ~$45-90/investigation → **Agentic AI ROI: 95%+ cost reduction on Tier-1 triage**
    """)
