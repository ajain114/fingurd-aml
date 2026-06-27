"""
Entity Intelligence Agent — Specialist Agent #2
Synchrony PLCC context: identity verification, fraud registry, watchlists, device signals.
Bedrock equivalent: Agent Collaborator with Customer 360 + Identity Verification Action Groups
"""

from .base_agent import BaseAgent
from tools.watchlist import (
    verify_identity,
    check_internal_fraud_registry,
    check_ofac_watchlist,
    check_fincen_314a,
    get_device_signals,
    check_sar_history,
    check_related_accounts,
)
from tools.transaction_db import get_customer_profile, get_contact_change_history

SYSTEM_PROMPT = """You are an Entity Intelligence Analyst at Synchrony Financial, specializing in
cardholder identity verification, fraud registry screening, and KYC/EDD evaluation for the
Private Label Credit Card (PLCC) business.

Your role:
- Build a complete risk profile of the cardholder
- Run identity verification (LexisNexis/FraudIQ equivalent)
- Screen against internal fraud registry and ACFE consortium data
- Check OFAC and FinCEN 314(a) watchlists
- Analyze device fingerprint and login velocity signals
- Review contact change history (ATO indicator)
- Check for linked accounts (fraud ring indicator)
- Review prior SAR history

Process:
1. Retrieve the cardholder profile
2. Check contact change history (critical ATO signal)
3. Run identity verification
4. Check internal fraud registry with name + SSN
5. Screen against OFAC watchlist
6. Check FinCEN 314(a) with name + SSN
7. Get device and velocity signals
8. Check for linked accounts
9. Retrieve prior SAR history
10. Synthesize findings

Output format (always follow this):
ENTITY INTELLIGENCE FINDINGS:
- Cardholder: [name, product, tenure, credit limit]
- Account Status: [current status]
- Identity Verification: [IDV score/100] — [PASS/PARTIAL/FAIL details]
- SSN Anomaly: [YES - detail / NO]
- Internal Fraud Registry: [CLEAR / HIT - detail]
- OFAC SDN: [CLEAR / HIT]
- FinCEN 314(a): [CLEAR / HIT - case ref]
- Contact Change Alert: [YES - fields changed + date / NO]
- Device Risk: [flag type + detail]
- Linked Accounts: [count + risk detail]
- Prior SARs: [count]
- Entity Risk Score: [0-100]
- Suspected Fraud Type: [Bust-Out / ATO / Synthetic Identity / Money Mule / Other]
- Risk Rationale: [2-3 specific sentences]"""


TOOLS = [
    {
        "name": "get_customer_profile",
        "description": "Retrieve cardholder profile including credit limit, utilization, payment history, and contact info.",
        "input_schema": {
            "type": "object",
            "properties": {"account_id": {"type": "string"}},
            "required": ["account_id"],
        },
    },
    {
        "name": "get_contact_change_history",
        "description": "Retrieve recent changes to address, phone, and email — a key ATO indicator.",
        "input_schema": {
            "type": "object",
            "properties": {"account_id": {"type": "string"}},
            "required": ["account_id"],
        },
    },
    {
        "name": "verify_identity",
        "description": "Run identity verification against LexisNexis/Equifax FraudIQ. Returns IDV score and field-level match results.",
        "input_schema": {
            "type": "object",
            "properties": {"account_id": {"type": "string"}},
            "required": ["account_id"],
        },
    },
    {
        "name": "check_internal_fraud_registry",
        "description": "Screen against Synchrony internal fraud watch list and ACFE retail card fraud consortium.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "ssn_last4": {"type": "string", "default": ""},
                "phone": {"type": "string", "default": ""},
            },
            "required": ["name"],
        },
    },
    {
        "name": "check_ofac_watchlist",
        "description": "Screen name against OFAC SDN, EU sanctions, and UN consolidated list.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "country": {"type": "string", "default": "US"},
            },
            "required": ["name"],
        },
    },
    {
        "name": "check_fincen_314a",
        "description": "Check FinCEN 314(a) active law enforcement request list. A hit means law enforcement is actively investigating.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "ssn_last4": {"type": "string", "default": ""},
            },
            "required": ["name"],
        },
    },
    {
        "name": "get_device_signals",
        "description": "Retrieve device fingerprint, login velocity, and IP signals from the fraud detection platform.",
        "input_schema": {
            "type": "object",
            "properties": {"account_id": {"type": "string"}},
            "required": ["account_id"],
        },
    },
    {
        "name": "check_related_accounts",
        "description": "Find other Synchrony accounts linked by SSN, device fingerprint, phone, email, or address.",
        "input_schema": {
            "type": "object",
            "properties": {"account_id": {"type": "string"}},
            "required": ["account_id"],
        },
    },
    {
        "name": "check_sar_history",
        "description": "Retrieve prior SAR filings associated with this account or cardholder.",
        "input_schema": {
            "type": "object",
            "properties": {"account_id": {"type": "string"}},
            "required": ["account_id"],
        },
    },
]

TOOL_REGISTRY = {
    "get_customer_profile": get_customer_profile,
    "get_contact_change_history": get_contact_change_history,
    "verify_identity": verify_identity,
    "check_internal_fraud_registry": check_internal_fraud_registry,
    "check_ofac_watchlist": check_ofac_watchlist,
    "check_fincen_314a": check_fincen_314a,
    "get_device_signals": get_device_signals,
    "check_related_accounts": check_related_accounts,
    "check_sar_history": check_sar_history,
}


def build(client, model, on_tool_call=None, on_tool_result=None, provider="anthropic") -> BaseAgent:
    return BaseAgent(
        client=client,
        model=model,
        name="Entity Intelligence Agent",
        system_prompt=SYSTEM_PROMPT,
        tools=TOOLS,
        tool_registry=TOOL_REGISTRY,
        provider=provider,
        on_tool_call=on_tool_call,
        on_tool_result=on_tool_result,
    )
