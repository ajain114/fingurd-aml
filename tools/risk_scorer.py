"""
Rule-based Risk Scoring Engine — Synchrony PLCC context.
Explainable, auditable risk scores (MRM-compliant, SR 11-7 aligned).
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class RiskFactor:
    name: str
    score: int       # 0-100
    weight: float
    detail: str
    evidence: str


@dataclass
class RiskAssessment:
    overall_score: int
    risk_level: str  # LOW / MEDIUM / HIGH / CRITICAL
    factors: List[RiskFactor] = field(default_factory=list)
    recommendation: str = ""
    sar_recommended: bool = False
    fraud_type: str = ""


def compute_risk_score(
    txn_data: dict,
    customer_data: dict,
    bust_out_data: dict,
    peer_data: dict,
    identity_data: dict,
    device_data: dict,
    mcc_data: dict,
) -> RiskAssessment:
    """
    Compute explainable risk score for Synchrony PLCC transaction monitoring.
    Each factor is independently auditable — meets Federal Reserve SR 11-7 Model Risk requirements.
    """
    factors = []

    # ── Factor 1: Bust-Out Signals (weight: 0.30) ────────────────────────────
    bust_score = bust_out_data.get("bust_out_score", 0)
    utilization = customer_data.get("utilization_pct", 0)
    phone_dead = customer_data.get("phone_status") == "DISCONNECTED"
    email_dead = customer_data.get("email_status") == "BOUNCE"

    bust_detail = f"Bust-out score: {bust_score}/100 | Utilization: {utilization}%"
    if phone_dead:
        bust_detail += " | Phone DISCONNECTED"
    if email_dead:
        bust_detail += " | Email BOUNCING"

    factors.append(RiskFactor(
        name="Bust-Out Pattern",
        score=min(bust_score, 100),
        weight=0.30,
        detail=bust_detail,
        evidence=f"Indicators: {'; '.join(bust_out_data.get('indicators', ['None']))}",
    ))

    # ── Factor 2: Identity Risk (weight: 0.25) ───────────────────────────────
    idv_score = identity_data.get("idv_score", 80)
    id_risk_score = max(0, 100 - idv_score)
    ssn_anomaly = identity_data.get("ssn_issuance_anomaly", False)
    if ssn_anomaly:
        id_risk_score = min(id_risk_score + 20, 100)

    factors.append(RiskFactor(
        name="Identity Verification",
        score=id_risk_score,
        weight=0.25,
        detail=identity_data.get("overall", "Identity not verified"),
        evidence=f"IDV score: {idv_score}/100 | SSN anomaly: {'YES' if ssn_anomaly else 'NO'} | {identity_data.get('ssn_detail', '')}",
    ))

    # ── Factor 3: MCC Risk Profile (weight: 0.20) ────────────────────────────
    high_risk_pct = mcc_data.get("high_risk_pct", 0)
    if high_risk_pct >= 60:
        mcc_score = 95
    elif high_risk_pct >= 40:
        mcc_score = 75
    elif high_risk_pct >= 20:
        mcc_score = 45
    else:
        mcc_score = 15

    factors.append(RiskFactor(
        name="MCC Risk Profile",
        score=mcc_score,
        weight=0.20,
        detail=f"{high_risk_pct}% of recent spend in high-risk MCC categories",
        evidence=f"High-risk volume: ${mcc_data.get('high_risk_mcc_volume', 0):,.2f} / Total: ${mcc_data.get('total_volume', 0):,.2f}",
    ))

    # ── Factor 4: Device & Velocity Signals (weight: 0.15) ──────────────────
    device_flag = device_data.get("device_flag", "CLEAN")
    if device_flag == "MULTIPLE_DEVICE_SWITCH":
        dev_score = 85
    elif device_flag == "NEW_DEVICE_POST_CONTACT_CHANGE":
        dev_score = 70
    else:
        dev_score = 10

    if device_data.get("ip_flag"):
        dev_score = min(dev_score + 15, 100)
    if device_data.get("velocity_flag"):
        dev_score = min(dev_score + 20, 100)

    factors.append(RiskFactor(
        name="Device & Velocity Signals",
        score=dev_score,
        weight=0.15,
        detail=f"Device flag: {device_flag}",
        evidence=f"IP flag: {device_data.get('ip_flag', 'None')} | Velocity: {device_data.get('velocity_flag', 'None')}",
    ))

    # ── Factor 5: Spend vs Peer Anomaly (weight: 0.10) ──────────────────────
    spend_ratio = peer_data.get("spend_ratio_vs_peer", 1)
    if spend_ratio >= 10:
        peer_score = 95
    elif spend_ratio >= 5:
        peer_score = 75
    elif spend_ratio >= 3:
        peer_score = 50
    else:
        peer_score = 15

    factors.append(RiskFactor(
        name="Spend Velocity vs Peer",
        score=peer_score,
        weight=0.10,
        detail=f"Spending {spend_ratio}x above peer group average",
        evidence=f"Account: ${peer_data.get('account_monthly_spend', 0):,.2f} | Peer avg: ${peer_data.get('peer_avg_monthly_spend', 0):,.2f}/month",
    ))

    # ── Weighted overall score ────────────────────────────────────────────────
    overall = round(sum(f.score * f.weight for f in factors))

    # Determine fraud type
    if bust_out_data.get("bust_out_detected"):
        fraud_type = "Bust-Out Fraud"
    elif device_flag == "NEW_DEVICE_POST_CONTACT_CHANGE":
        fraud_type = "Account Takeover (ATO)"
    elif identity_data.get("ssn_issuance_anomaly"):
        fraud_type = "Synthetic Identity Fraud"
    else:
        fraud_type = "Suspicious Activity"

    if overall >= 80:
        risk_level = "CRITICAL"
        recommendation = f"Suspected {fraud_type}. Freeze account immediately. File SAR within 30 days. Escalate to BSA Officer and Fraud Operations."
        sar_recommended = True
    elif overall >= 60:
        risk_level = "HIGH"
        recommendation = f"Strong {fraud_type} indicators. Recommend SAR filing. Initiate outbound contact verification. Place account on enhanced monitoring."
        sar_recommended = True
    elif overall >= 40:
        risk_level = "MEDIUM"
        recommendation = "Enhanced monitoring warranted. Request cardholder contact. Re-evaluate in 15 days."
        sar_recommended = False
    else:
        risk_level = "LOW"
        recommendation = "No immediate action required. Continue standard monitoring."
        sar_recommended = False

    return RiskAssessment(
        overall_score=overall,
        risk_level=risk_level,
        factors=factors,
        recommendation=recommendation,
        sar_recommended=sar_recommended,
        fraud_type=fraud_type,
    )
