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


def get_api_key(provider: str = "anthropic") -> str:
    key_map = {
        "groq": "GROQ_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
    }
    env_key = key_map.get(provider, "ANTHROPIC_API_KEY")
    try:
        return st.secrets[env_key]
    except Exception:
        return os.getenv(env_key, "")


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

    provider = st.radio(
        "LLM Provider",
        ["Gemini (Free — 1M tokens/day)", "Groq (Free — 100K tokens/day)", "Anthropic (Claude)"],
        help="Gemini = best free option. Groq = faster but 100K daily cap. Anthropic = same as Bedrock.",
    )

    if provider.startswith("Gemini"):
        st.session_state.provider = "gemini"
        st.info("Google Gemini — **1M tokens/day free**, no credit card. Get key at **aistudio.google.com**", icon="✨")
        api_key = st.text_input(
            "Gemini API Key", value=get_api_key("gemini"), type="password",
            help="aistudio.google.com → Get API Key (sign in with Google)"
        )
        model = st.selectbox("Model", [
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
        ], help="gemini-2.0-flash = fastest + smartest | 1.5-pro = highest quality")
        st.caption("In production: swap client to Bedrock Claude — same tool schemas")

    elif provider.startswith("Groq"):
        st.session_state.provider = "groq"
        st.warning("Groq free tier: 100K tokens/day. Switch to Gemini if you hit the limit.", icon="⚠️")
        api_key = st.text_input(
            "Groq API Key", value=get_api_key("groq"), type="password",
            help="console.groq.com → API Keys → Create"
        )
        model = st.selectbox("Model", [
            "llama-3.3-70b-versatile",
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "llama-3.1-8b-instant",
        ], help="llama-3.3-70b = best quality | llama-4-scout = fast")

    else:
        st.session_state.provider = "anthropic"
        st.info("Claude = same model that runs on **Amazon Bedrock**", icon="☁️")
        api_key = st.text_input(
            "Anthropic API Key", value=get_api_key(), type="password",
            help="console.anthropic.com → API Keys"
        )
        model = st.selectbox("Model", [
            "claude-3-5-sonnet-20241022",
            "claude-3-haiku-20240307",
        ], help="3-5-sonnet = production quality | haiku = faster demo")

    st.session_state.api_key = api_key
    st.session_state.model = model

    st.divider()
    st.caption("**Architecture**: Multi-Agent Orchestration")
    st.caption("**RAG**: ChromaDB (AML Typologies)")
    st.caption("**HITL**: Human-in-the-Loop approval")
    st.caption("**Mirrors**: Amazon Bedrock AgentCore")


# ── Main content tabs ─────────────────────────────────────────────────────────
tab_investigate, tab_custom, tab_rules, tab_arch, tab_bedrock = st.tabs([
    "🔍 Investigate", "🧪 Custom Case", "📋 Risk Rules", "🏗️ Architecture", "☁️ Bedrock Production Code"
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
                    provider=st.session_state.get("provider", "anthropic"),
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
# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: CUSTOM CASE
# ══════════════════════════════════════════════════════════════════════════════
with tab_custom:
    st.markdown("### 🧪 Custom Case — Enter Your Own Client Data")
    st.markdown(
        "Fill in the fields below to test the risk scoring engine on any scenario. "
        "The same 5-factor rule engine used on the demo cases will run on your inputs."
    )

    with st.form("custom_case_form"):
        st.markdown("#### Account Basics")
        c1, c2, c3 = st.columns(3)
        with c1:
            cc_name       = st.text_input("Cardholder Name", value="John Doe")
            cc_product    = st.text_input("Card Product", value="Synchrony Amazon Store Card")
        with c2:
            cc_limit      = st.number_input("Credit Limit ($)", min_value=500, max_value=50000, value=8000, step=500)
            cc_utilization= st.slider("Current Utilization (%)", 0, 100, 30)
        with c3:
            cc_days_open  = st.number_input("Account Age (days)", min_value=1, max_value=3650, value=120)
            cc_cli_count  = st.number_input("Credit Limit Increases (CLIs) in last 90 days", min_value=0, max_value=10, value=0)

        st.divider()
        st.markdown("#### Bust-Out Signals")
        b1, b2, b3 = st.columns(3)
        with b1:
            bo_score      = st.slider("Bust-Out Score (0–100)", 0, 100, 0,
                                      help="Overall bust-out pattern score from transaction analysis")
            bo_detected   = st.checkbox("Bust-Out Pattern Detected", value=False)
        with b2:
            gift_cards    = st.number_input("Gift Card Purchases (last 10 days, $)", min_value=0, max_value=30000, value=0, step=100)
            cash_advance  = st.number_input("Cash Advances (last 10 days, $)", min_value=0, max_value=20000, value=0, step=100)
        with b3:
            phone_status  = st.selectbox("Phone Status", ["ACTIVE", "DISCONNECTED", "UNKNOWN"])
            email_status  = st.selectbox("Email Status", ["ACTIVE", "BOUNCE", "UNKNOWN"])

        st.divider()
        st.markdown("#### Identity Verification")
        i1, i2 = st.columns(2)
        with i1:
            idv_score     = st.slider("IDV Score (LexisNexis/FraudIQ, 0–100)", 0, 100, 85,
                                      help="Higher = more verified. Below 60 triggers high identity risk.")
            ssn_anomaly   = st.checkbox("SSN Issuance Anomaly", value=False,
                                        help="SSN issued after cardholder's stated birthdate, or in wrong state")
        with i2:
            ofac_hit      = st.checkbox("OFAC SDN Watchlist Hit", value=False)
            fincen_hit    = st.checkbox("FinCEN 314(a) Hit", value=False)

        st.divider()
        st.markdown("#### MCC (Merchant Category Code) Risk")
        m1, m2 = st.columns(2)
        with m1:
            high_risk_pct = st.slider("% of Recent Spend in HIGH-Risk MCCs", 0, 100, 0,
                                      help="High-risk MCCs: Gift cards (5999_GIFT), ATM (6011), Jewelry (5094), Western Union (6051)")
            high_risk_vol = st.number_input("High-Risk MCC Total Volume ($)", min_value=0, max_value=50000, value=0, step=100)
        with m2:
            total_vol     = st.number_input("Total Recent Spend ($)", min_value=0, max_value=50000, value=1000, step=100)
            st.markdown("""
            **HIGH-risk MCCs:**
            `6011` ATM Cash Advance
            `5999_GIFT` Gift Cards
            `5094` Jewelry / Precious Metals
            `6051` Western Union / Crypto
            `7995` Gambling
            """)

        st.divider()
        st.markdown("#### Device & Login Signals")
        d1, d2 = st.columns(2)
        with d1:
            device_flag   = st.selectbox("Device Flag", [
                "CLEAN",
                "NEW_DEVICE_POST_CONTACT_CHANGE",
                "MULTIPLE_DEVICE_SWITCH",
            ], help="NEW_DEVICE_POST_CONTACT_CHANGE is the primary ATO signal")
        with d2:
            ip_flag       = st.selectbox("IP Anomaly Flag", ["None", "TOR_EXIT_NODE", "VPN_DETECTED", "GEO_MISMATCH"])
            velocity_flag = st.selectbox("Login Velocity Flag", ["None", "HIGH_VELOCITY", "BRUTE_FORCE_ATTEMPT"])

        st.divider()
        st.markdown("#### Peer Comparison")
        p1, p2 = st.columns(2)
        with p1:
            peer_ratio    = st.number_input("Spend Ratio vs Peer Group (e.g. 3.5 = 3.5x above average)",
                                            min_value=0.1, max_value=50.0, value=1.0, step=0.5)
        with p2:
            account_spend = st.number_input("Account Monthly Spend ($)", min_value=0, max_value=50000, value=500, step=100)
            peer_avg      = st.number_input("Peer Group Avg Monthly Spend ($)", min_value=1, max_value=10000, value=500, step=50)

        submitted = st.form_submit_button("▶ Run Risk Rules", type="primary", use_container_width=True)

    if submitted:
        from tools.risk_scorer import compute_risk_score

        bust_indicators = []
        if bo_detected:
            bust_indicators.append("Bust-out pattern detected")
        if gift_cards > 0:
            bust_indicators.append(f"Gift card purchases: ${gift_cards:,.0f}")
        if cash_advance > 0:
            bust_indicators.append(f"Cash advances: ${cash_advance:,.0f}")
        if phone_status == "DISCONNECTED":
            bust_indicators.append("Phone disconnected")
        if email_status == "BOUNCE":
            bust_indicators.append("Email bouncing")

        custom_bust  = {"bust_out_score": bo_score, "bust_out_detected": bo_detected, "indicators": bust_indicators or ["None"]}
        custom_cust  = {"utilization_pct": cc_utilization, "phone_status": phone_status, "email_status": email_status}
        custom_peer  = {"spend_ratio_vs_peer": peer_ratio, "account_monthly_spend": account_spend, "peer_avg_monthly_spend": peer_avg}
        custom_idv   = {
            "idv_score": idv_score, "overall": f"IDV {'PASS' if idv_score >= 70 else 'PARTIAL' if idv_score >= 50 else 'FAIL'}",
            "ssn_issuance_anomaly": ssn_anomaly, "ssn_detail": "SSN issued post-DOB in mismatched state" if ssn_anomaly else "",
        }
        custom_dev   = {
            "device_flag": device_flag,
            "ip_flag": None if ip_flag == "None" else ip_flag,
            "velocity_flag": None if velocity_flag == "None" else velocity_flag,
        }
        custom_mcc   = {"high_risk_pct": high_risk_pct, "high_risk_mcc_volume": high_risk_vol, "total_volume": total_vol}

        ra = compute_risk_score(
            txn_data={}, customer_data=custom_cust, bust_out_data=custom_bust,
            peer_data=custom_peer, identity_data=custom_idv, device_data=custom_dev, mcc_data=custom_mcc
        )

        # ── Result display ────────────────────────────────────────────────────
        score_color = {"CRITICAL": "#dc3545", "HIGH": "#fd7e14", "MEDIUM": "#ffc107", "LOW": "#28a745"}.get(ra.risk_level, "#7ab3e0")
        st.markdown(f"""
        <div style="background:#1a1f2e;border:2px solid {score_color};border-radius:10px;padding:24px;margin:16px 0">
            <div style="display:flex;align-items:center;gap:24px">
                <div style="text-align:center">
                    <div style="font-size:52px;font-weight:900;color:{score_color};line-height:1">{ra.overall_score}</div>
                    <div style="font-size:11px;color:#9aa3b0;margin-top:4px">RISK SCORE / 100</div>
                </div>
                <div>
                    <div class="risk-badge-{ra.risk_level}" style="margin-bottom:8px">{ra.risk_level}</div>
                    <div style="color:#c8d6e5;font-size:14px;font-weight:600">{ra.fraud_type}</div>
                    <div style="color:{'#dc3545' if ra.sar_recommended else '#28a745'};font-size:13px;margin-top:4px">
                        {'⚡ SAR FILING RECOMMENDED' if ra.sar_recommended else '✓ SAR Not Required'}
                    </div>
                </div>
            </div>
            <div style="color:#9aa3b0;font-size:13px;margin-top:16px">{ra.recommendation}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Factor Breakdown")
        for f in ra.factors:
            bar_color = "#dc3545" if f.score >= 80 else "#fd7e14" if f.score >= 60 else "#ffc107" if f.score >= 40 else "#28a745"
            pct = f.score
            weighted = round(f.score * f.weight)
            with st.expander(f"**{f.name}** — score {f.score}/100 × weight {int(f.weight*100)}% = **{weighted} pts**"):
                st.markdown(f"""
                <div style="background:#111827;border-radius:6px;height:8px;margin:4px 0 12px 0;overflow:hidden">
                    <div style="width:{pct}%;height:100%;background:{bar_color};border-radius:6px"></div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"**Detail:** {f.detail}")
                st.markdown(f"**Evidence:** {f.evidence}")

        st.markdown("---")
        st.markdown("##### Rule Engine Trace (what triggered each factor)")
        if ofac_hit:
            st.error("OFAC SDN HIT — immediate account freeze required regardless of score")
        if fincen_hit:
            st.warning("FinCEN 314(a) HIT — mandatory 10-day hold, law enforcement notification required")
        if ssn_anomaly:
            st.warning("SSN Issuance Anomaly — +20 points added to Identity Risk factor")
        if bo_detected:
            st.warning("Bust-Out pattern detected — Factor 1 score anchored to bust-out score input")
        if device_flag == "NEW_DEVICE_POST_CONTACT_CHANGE":
            st.warning("ATO signal: New device after contact change — Factor 4 score set to 70+")
        if device_flag == "MULTIPLE_DEVICE_SWITCH":
            st.warning("Multiple device switches — Factor 4 score set to 85+")
        if ip_flag and ip_flag != "None":
            st.warning(f"IP anomaly flag: {ip_flag} — +15 added to Device factor")
        if velocity_flag and velocity_flag != "None":
            st.warning(f"Velocity flag: {velocity_flag} — +20 added to Device factor")
        if high_risk_pct >= 60:
            st.warning(f"MCC risk: {high_risk_pct}% of spend in HIGH-risk MCCs → MCC factor score = 95")
        elif high_risk_pct >= 40:
            st.info(f"MCC risk: {high_risk_pct}% of spend in HIGH-risk MCCs → MCC factor score = 75")
        if peer_ratio >= 10:
            st.warning(f"Peer anomaly: {peer_ratio}x above peer group → Peer factor score = 95")
        elif peer_ratio >= 5:
            st.info(f"Peer anomaly: {peer_ratio}x above peer group → Peer factor score = 75")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: RISK RULES
# ══════════════════════════════════════════════════════════════════════════════
with tab_rules:
    st.markdown("### 📋 Risk Rules Reference")
    st.markdown("All rules used by the FinGuard scoring engine. Every rule is independently auditable — meets **Federal Reserve SR 11-7** Model Risk Management requirements.")

    # ── Decision Thresholds ────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### Decision Thresholds")
    st.markdown("""
    | Score Range | Risk Level | SAR Required | Action |
    |---|---|---|---|
    | **80 – 100** | 🔴 CRITICAL | Yes — mandatory | Freeze account immediately. File SAR within 30 days. Escalate to BSA Officer + Fraud Ops. |
    | **60 – 79** | 🟠 HIGH | Yes — recommended | Strong fraud indicators. Recommend SAR filing. Initiate contact verification. Enhanced monitoring. |
    | **40 – 59** | 🟡 MEDIUM | No | Enhanced monitoring. Request cardholder contact. Re-evaluate in 15 days. |
    | **0 – 39** | 🟢 LOW | No | No immediate action. Continue standard monitoring. |
    """)

    # ── 5-Factor Model ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 5-Factor Scoring Model (Weighted)")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Factor 1 — Bust-Out Pattern (Weight: 30%)**

        | Condition | Points Added |
        |---|---|
        | Bust-out score from transaction engine | 0–100 (direct input) |
        | Phone DISCONNECTED | +shown in detail |
        | Email BOUNCE | +shown in detail |

        *Highest weight — bust-out is the primary fraud type in Synchrony PLCC portfolio.*
        """)

        st.markdown("""
        **Factor 3 — MCC Risk Profile (Weight: 20%)**

        | % of Spend in HIGH-Risk MCCs | Score |
        |---|---|
        | ≥ 60% | 95 |
        | 40% – 59% | 75 |
        | 20% – 39% | 45 |
        | < 20% | 15 |
        """)

        st.markdown("""
        **Factor 5 — Spend Velocity vs Peer (Weight: 10%)**

        | Spend vs Peer Group Average | Score |
        |---|---|
        | ≥ 10x above average | 95 |
        | 5x – 9.9x | 75 |
        | 3x – 4.9x | 50 |
        | < 3x | 15 |
        """)

    with col2:
        st.markdown("""
        **Factor 2 — Identity Verification (Weight: 25%)**

        | Condition | Score |
        |---|---|
        | Base score = 100 – IDV score | 0–100 |
        | SSN issuance anomaly detected | +20 (capped at 100) |

        *IDV score comes from LexisNexis/FraudIQ equivalent.*
        *IDV 85 → identity risk score = 15 (low)*
        *IDV 40 → identity risk score = 60 (high)*
        """)

        st.markdown("""
        **Factor 4 — Device & Velocity (Weight: 15%)**

        | Condition | Base Score |
        |---|---|
        | `CLEAN` — no device flag | 10 |
        | `NEW_DEVICE_POST_CONTACT_CHANGE` | 70 ← ATO signal |
        | `MULTIPLE_DEVICE_SWITCH` | 85 |

        | Add-on Flag | Additional Points |
        |---|---|
        | IP anomaly (TOR, VPN, Geo mismatch) | +15 |
        | Login velocity flag | +20 |
        | Combined max | 100 |
        """)

        st.markdown("""
        **Weighted Formula:**
        ```
        Overall = (F1 × 0.30) + (F2 × 0.25) + (F3 × 0.20)
                + (F4 × 0.15) + (F5 × 0.10)
        ```
        """)

    # ── Fraud Type Classification ──────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### Fraud Type Classification Rules")
    st.markdown("""
    The engine classifies fraud type in this priority order:

    | Priority | Fraud Type | Trigger Condition |
    |---|---|---|
    | 1st | **Bust-Out Fraud** | `bust_out_detected = True` |
    | 2nd | **Account Takeover (ATO)** | `device_flag = NEW_DEVICE_POST_CONTACT_CHANGE` |
    | 3rd | **Synthetic Identity Fraud** | `ssn_issuance_anomaly = True` |
    | Default | **Suspicious Activity** | None of the above |
    """)

    # ── MCC Risk Reference ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### MCC Code Risk Classification")
    st.markdown("""
    | MCC Code | Merchant Type | Risk Level | Why HIGH risk |
    |---|---|---|---|
    | `6011` | ATM Cash Advance | 🔴 HIGH | Cash = untraceable, instant liquidity for fraudster |
    | `6010` | Manual Cash Advance | 🔴 HIGH | Same as ATM |
    | `5999_GIFT` | Gift Cards / Prepaid | 🔴 HIGH | #1 bust-out tool — resold instantly at 80-90 cents on dollar |
    | `5094` | Jewelry / Precious Metals | 🔴 HIGH | High value, untraceable, easy resale |
    | `6051` | Western Union / Money Orders / Crypto | 🔴 HIGH | Classic layering vehicle in AML typologies |
    | `7995` | Gambling / Lottery | 🔴 HIGH | Regulated activity, often co-occurs with structuring |
    | `5734` | Computer / Electronics | 🟡 MEDIUM | Resaleable goods, elevated in bust-out exits |
    | `5999` | Miscellaneous Retail | 🟡 MEDIUM | Catch-all; elevated when off-network |
    | `4816` | Online Services | 🟡 MEDIUM | Subscription fraud vector |
    | `5200` | Home Supply (Lowe's) | 🟢 LOW | Expected spend for Lowe's card product |
    | `5411` | Grocery Stores | 🟢 LOW | Normal everyday spend |
    | `5712` | Furniture (Ashley) | 🟢 LOW | Expected spend for Ashley card product |
    | `5945` | Hobby / Toy Shops | 🟢 LOW | Normal retail |
    """)

    # ── Alert Trigger Rules ────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### Alert Trigger Rules (Transaction Monitoring)")
    st.markdown("""
    | Rule ID | Rule Name | Trigger Condition | Fraud Type |
    |---|---|---|---|
    | RULE-BUF-001 | Bust-Out Utilization Spike | Utilization jumps > 80% within 10 days on account < 180 days old | Bust-Out |
    | RULE-GFT-002 | Gift Card Velocity | Gift card purchases > $500 within 7 days | Bust-Out |
    | RULE-CNT-003 | Contact Unreachable | Phone DISCONNECTED **and** email BOUNCE simultaneously | Bust-Out |
    | RULE-ATO-001 | Multi-Field Contact Change | 3+ contact fields (address, phone, email) changed within 24 hours | ATO |
    | RULE-ATO-002 | New Device Post Change | Login from new device within 7 days of contact change | ATO |
    | RULE-CA-001 | Cash Advance Surge | Cash advance ≥ $2,000 on account with no prior cash advance history | ATO / Bust-Out |
    | RULE-MUL-001 | Third-Party Payment | Payment received from business entity not linked to cardholder | Money Mule |
    | RULE-MCC-001 | High-Risk MCC Cluster | ≥ 3 high-risk MCC types within 30 days | Money Mule / AML |
    | RULE-WU-001 | Money Transfer Service | Any transaction at MCC 6051 (Western Union, MoneyGram) | AML |
    | RULE-CLI-001 | Rapid CLI Abuse | 2+ credit limit increases within 90 days of account opening | Bust-Out |
    | RULE-SSN-001 | SSN Issuance Anomaly | SSN issued after stated birthdate or in mismatched state | Synthetic Identity |
    """)

    # ── Mandatory Override Rules ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### Mandatory Override Rules (Score-Independent)")
    st.warning(
        "These rules trigger mandatory action regardless of the overall risk score. "
        "They cannot be overridden by a low score."
    )
    st.markdown("""
    | Rule | Condition | Mandatory Action |
    |---|---|---|
    | OFAC SDN Hit | Cardholder name/SSN matches OFAC Specially Designated Nationals list | Immediate account freeze. Report to OFAC within 10 business days. |
    | FinCEN 314(a) | Subject of active FinCEN law enforcement request | 10-day information hold. Cannot tip off subject. Law enforcement notification. |
    | SAR Deadline | Score ≥ 60 investigation completed | SAR must be filed within **30 calendar days** of detection (FinCEN rule). |
    """)

    # ── Regulatory Basis ──────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### Regulatory Basis")
    st.markdown("""
    | Regulation | Applies To | What it requires |
    |---|---|---|
    | **Bank Secrecy Act (BSA)** | All US banks | SAR filing for suspicious activity ≥ $5,000 |
    | **FinCEN SAR Rule (31 CFR 1020.320)** | Banks incl. Synchrony | 30-day filing deadline, 5-year record retention |
    | **Federal Reserve SR 11-7** | Model Risk Management | All scoring models must be explainable, validated, documented |
    | **OFAC Regulations (31 CFR 501)** | All US persons & entities | Freeze assets of SDN-listed individuals |
    | **FinCEN 314(a)** | BSA-regulated institutions | Respond to law enforcement information requests within 14 days |
    | **FATF 40 Recommendations** | International standard | Typology-based risk assessment, enhanced due diligence |
    """)

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
