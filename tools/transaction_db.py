"""
Mock Credit Card Transaction Database — Synchrony PLCC context.
Mirrors what Bedrock Action Groups would call against Synchrony's
card management system (TSYS/FIS) or data lake.

Transaction types relevant to a credit card issuer:
  PURCHASE, CASH_ADVANCE, BALANCE_TRANSFER, PAYMENT_RECEIVED,
  REFUND, DISPUTE, CREDIT_LIMIT_INCREASE
"""

import json
from datetime import datetime, timedelta

# ── Cardholder profiles ───────────────────────────────────────────────────────

CUSTOMERS = {
    "CC-4821": {
        "account_id": "CC-4821",
        "cardholder_name": "James Holloway",
        "card_product": "Synchrony Amazon Store Card",
        "partner_retailer": "Amazon",
        "account_status": "Active - Payment Past Due",
        "opened": "2025-02-10",
        "credit_limit": 8000.00,
        "current_balance": 7892.40,
        "available_credit": 107.60,
        "utilization_pct": 98.7,
        "payment_due_date": "2026-06-15",
        "last_payment_date": "2026-04-20",
        "last_payment_amount": 75.00,
        "payments_on_time": 3,
        "payments_late": 0,
        "occupation": "Software Consultant",
        "income_stated": 85000,
        "ssn_last4": "3318",
        "dob": "1989-03-12",
        "address": "1042 Maple Ridge Dr, Columbus, OH 43201",
        "email": "j.holloway89@fastmail.com",
        "phone": "614-555-0183",
        "phone_status": "DISCONNECTED",
        "email_status": "BOUNCE",
        "kyc_score": 72,
        "risk_rating": "Low",   # was low, now elevated
        "sar_count": 0,
        "initial_credit_limit": 3000.00,
        "cli_history": [
            {"date": "2025-03-15", "from": 3000, "to": 5000, "reason": "On-time payments"},
            {"date": "2025-05-01", "from": 5000, "to": 8000, "reason": "Income verification passed"},
        ],
        "ssn_match_flag": "POTENTIAL_SYNTHETIC",
        "ssn_issue_note": "SSN issued in 2019 to individual born 1989 — issuance date anomaly",
        "bureau_score": 681,
        "bureau_score_date": "2025-02-08",
        "thin_file": True,
    },
    "CC-7734": {
        "account_id": "CC-7734",
        "cardholder_name": "Maria Santos",
        "card_product": "Synchrony Lowe's Advantage Card",
        "partner_retailer": "Lowe's",
        "account_status": "Active",
        "opened": "2021-06-14",
        "credit_limit": 12000.00,
        "current_balance": 1240.00,
        "available_credit": 10760.00,
        "utilization_pct": 10.3,
        "payment_due_date": "2026-07-10",
        "last_payment_date": "2026-06-08",
        "last_payment_amount": 1850.00,
        "payments_on_time": 58,
        "payments_late": 1,
        "occupation": "Nurse Practitioner",
        "income_stated": 110000,
        "ssn_last4": "7752",
        "dob": "1985-09-23",
        "address": "88 Pinecrest Ave, Orlando, FL 32801",
        "email": "msantos.np@healthcarepros.org",
        "phone": "407-555-0294",
        "phone_status": "ACTIVE",
        "email_status": "ACTIVE",
        "kyc_score": 92,
        "risk_rating": "Low",
        "sar_count": 0,
        "initial_credit_limit": 5000.00,
        "cli_history": [
            {"date": "2022-08-10", "from": 5000, "to": 8000},
            {"date": "2023-11-05", "from": 8000, "to": 12000},
        ],
        "ssn_match_flag": "CLEAN",
        "bureau_score": 774,
        "bureau_score_date": "2025-09-10",
        "thin_file": False,
        "recent_changes": [
            {"field": "address", "old": "221 Harbor Dr, Tampa, FL 33601", "new": "88 Pinecrest Ave, Orlando, FL 32801", "date": "2026-06-20", "channel": "Online Portal"},
            {"field": "phone", "old": "813-555-0112", "new": "407-555-0294", "date": "2026-06-20", "channel": "Online Portal"},
            {"field": "email", "old": "mariesantos1985@gmail.com", "new": "msantos.np@healthcarepros.org", "date": "2026-06-21", "channel": "Online Portal"},
        ],
    },
    "CC-2291": {
        "account_id": "CC-2291",
        "cardholder_name": "Derek Okafor",
        "card_product": "Synchrony Ashley Advantage Card",
        "partner_retailer": "Ashley Furniture",
        "account_status": "Active",
        "opened": "2024-08-22",
        "credit_limit": 5000.00,
        "current_balance": 4820.00,
        "available_credit": 180.00,
        "utilization_pct": 96.4,
        "payment_due_date": "2026-07-05",
        "last_payment_date": "2026-06-01",
        "last_payment_amount": 4800.00,   # suspicious: large payment then immediate spend
        "payments_on_time": 9,
        "payments_late": 0,
        "occupation": "Logistics Coordinator",
        "income_stated": 62000,
        "ssn_last4": "4491",
        "dob": "1993-07-07",
        "address": "3312 Elm St, Atlanta, GA 30301",
        "email": "d.okafor.work@gmail.com",
        "phone": "404-555-0371",
        "phone_status": "ACTIVE",
        "email_status": "ACTIVE",
        "kyc_score": 68,
        "risk_rating": "Low",
        "sar_count": 0,
        "initial_credit_limit": 2500.00,
        "cli_history": [
            {"date": "2025-01-10", "from": 2500, "to": 5000, "reason": "On-time payments"},
        ],
        "ssn_match_flag": "CLEAN",
        "bureau_score": 643,
        "bureau_score_date": "2024-08-20",
        "thin_file": False,
        "payment_source_flag": "THIRD_PARTY_PAYMENT",
        "payment_source_note": "June 2026 payment of $4,800 originated from account not linked to cardholder",
    },
}

# ── MCC codes reference ───────────────────────────────────────────────────────

MCC_RISK = {
    "6010": ("Cash Advance", "HIGH"),
    "6011": ("ATM Cash Advance", "HIGH"),
    "5094": ("Jewelry, Watches, Precious Stones", "HIGH"),
    "7995": ("Gambling / Lottery", "HIGH"),
    "6051": ("Non-Financial Institutions – Crypto/Money Orders", "HIGH"),
    "5047": ("Medical and Dental Equipment", "LOW"),
    "5411": ("Grocery Stores", "LOW"),
    "5200": ("Home Supply / Lumber Stores (e.g., Lowe's)", "LOW"),
    "5945": ("Hobby/Toy/Game Shops", "LOW"),
    "5734": ("Computer/Software Stores", "MEDIUM"),
    "5999": ("Miscellaneous Retail", "MEDIUM"),
    "4816": ("Computer Network/Information Services", "MEDIUM"),
    "5999_GIFT": ("Gift Cards / Open-Loop Prepaid Cards", "HIGH"),
}


def _days_ago(n):
    return (datetime.now() - timedelta(days=n)).strftime("%Y-%m-%d")


TRANSACTIONS = {
    # ── CC-4821: James Holloway — Bust-Out Fraud ─────────────────────────────
    "CC-4821": [
        # Months 1-3: Good behaviour (building trust for CLI)
        {"txn_id": "T-A001", "date": _days_ago(108), "type": "PURCHASE", "amount": 89.99,  "merchant": "Amazon", "mcc": "5999", "channel": "Online"},
        {"txn_id": "T-A002", "date": _days_ago(105), "type": "PAYMENT_RECEIVED", "amount": 89.99, "merchant": "PAYMENT ACH", "mcc": None, "channel": "ACH"},
        {"txn_id": "T-A003", "date": _days_ago(98),  "type": "PURCHASE", "amount": 134.50, "merchant": "Amazon", "mcc": "5999", "channel": "Online"},
        {"txn_id": "T-A004", "date": _days_ago(94),  "type": "PURCHASE", "amount": 67.20,  "merchant": "Amazon", "mcc": "5999", "channel": "Online"},
        {"txn_id": "T-A005", "date": _days_ago(90),  "type": "PAYMENT_RECEIVED", "amount": 200.00, "merchant": "PAYMENT ACH", "mcc": None, "channel": "ACH"},
        {"txn_id": "T-A006", "date": _days_ago(75),  "type": "PURCHASE", "amount": 210.00, "merchant": "Amazon Electronics", "mcc": "5734", "channel": "Online"},
        {"txn_id": "T-A007", "date": _days_ago(72),  "type": "PURCHASE", "amount": 88.40,  "merchant": "Amazon", "mcc": "5999", "channel": "Online"},
        {"txn_id": "T-A008", "date": _days_ago(68),  "type": "PAYMENT_RECEIVED", "amount": 300.00, "merchant": "PAYMENT ACH", "mcc": None, "channel": "ACH"},
        # CLI granted at 60 days: limit $3K → $5K
        {"txn_id": "T-A009", "date": _days_ago(55),  "type": "PURCHASE", "amount": 420.00, "merchant": "Amazon", "mcc": "5999", "channel": "Online"},
        {"txn_id": "T-A010", "date": _days_ago(50),  "type": "PURCHASE", "amount": 185.00, "merchant": "Amazon Electronics", "mcc": "5734", "channel": "Online"},
        {"txn_id": "T-A011", "date": _days_ago(48),  "type": "PAYMENT_RECEIVED", "amount": 605.00, "merchant": "PAYMENT ACH", "mcc": None, "channel": "ACH"},
        # CLI granted again: limit $5K → $8K
        # Bust-out begins (last 10 days) — rapid high-risk spending
        {"txn_id": "T-A012", "date": _days_ago(10), "type": "PURCHASE", "amount": 1240.00, "merchant": "Amazon Gift Cards", "mcc": "5999_GIFT", "channel": "Online", "flagged": True, "flag_reason": "Gift card purchase — high-risk MCC"},
        {"txn_id": "T-A013", "date": _days_ago(9),  "type": "PURCHASE", "amount": 980.00,  "merchant": "Amazon Gift Cards", "mcc": "5999_GIFT", "channel": "Online", "flagged": True},
        {"txn_id": "T-A014", "date": _days_ago(9),  "type": "PURCHASE", "amount": 760.00,  "merchant": "Apple Store (off-network)", "mcc": "5734", "channel": "In-Store", "flagged": True, "flag_reason": "Off-network spend surge"},
        {"txn_id": "T-A015", "date": _days_ago(8),  "type": "PURCHASE", "amount": 1480.00, "merchant": "Best Buy Electronics (off-network)", "mcc": "5734", "channel": "In-Store", "flagged": True},
        {"txn_id": "T-A016", "date": _days_ago(8),  "type": "CASH_ADVANCE", "amount": 1500.00, "merchant": "CHASE ATM - COLUMBUS OH", "mcc": "6011", "channel": "ATM", "flagged": True, "flag_reason": "Cash advance — first ever on this account"},
        {"txn_id": "T-A017", "date": _days_ago(7),  "type": "PURCHASE", "amount": 892.40,  "merchant": "Walmart (off-network)", "mcc": "5999", "channel": "In-Store", "flagged": True},
        {"txn_id": "T-A018", "date": _days_ago(7),  "type": "PURCHASE", "amount": 940.00,  "merchant": "Amazon Gift Cards", "mcc": "5999_GIFT", "channel": "Online", "flagged": True},
        # No payment received since Day -10; phone/email dead
    ],

    # ── CC-7734: Maria Santos — Account Takeover + Cash-Out ─────────────────
    "CC-7734": [
        # 5-year normal history (sample)
        {"txn_id": "T-B001", "date": _days_ago(180), "type": "PURCHASE", "amount": 1820.00, "merchant": "Lowe's", "mcc": "5200", "channel": "In-Store"},
        {"txn_id": "T-B002", "date": _days_ago(175), "type": "PAYMENT_RECEIVED", "amount": 1820.00, "merchant": "PAYMENT ACH", "mcc": None, "channel": "ACH"},
        {"txn_id": "T-B003", "date": _days_ago(120), "type": "PURCHASE", "amount": 2440.00, "merchant": "Lowe's", "mcc": "5200", "channel": "In-Store"},
        {"txn_id": "T-B004", "date": _days_ago(115), "type": "PAYMENT_RECEIVED", "amount": 2440.00, "merchant": "PAYMENT ACH", "mcc": None, "channel": "ACH"},
        {"txn_id": "T-B005", "date": _days_ago(60),  "type": "PURCHASE", "amount": 890.00,  "merchant": "Lowe's", "mcc": "5200", "channel": "In-Store"},
        {"txn_id": "T-B006", "date": _days_ago(55),  "type": "PAYMENT_RECEIVED", "amount": 890.00, "merchant": "PAYMENT ACH", "mcc": None, "channel": "ACH"},
        # ATO event: contact info changed Days -7 to -6 (see customer profile)
        # Suspicious post-ATO activity
        {"txn_id": "T-B007", "date": _days_ago(5), "type": "PURCHASE", "amount": 1900.00, "merchant": "Lowe's Gift Cards", "mcc": "5999_GIFT", "channel": "In-Store", "flagged": True, "flag_reason": "Gift cards post-contact-change"},
        {"txn_id": "T-B008", "date": _days_ago(4), "type": "CASH_ADVANCE", "amount": 3000.00, "merchant": "WELLS FARGO ATM - ORLANDO FL", "mcc": "6011", "channel": "ATM", "flagged": True, "flag_reason": "Cash advance in new city (Orlando vs Tampa)"},
        {"txn_id": "T-B009", "date": _days_ago(4), "type": "CASH_ADVANCE", "amount": 2800.00, "merchant": "BANK OF AMERICA ATM - ORLANDO FL", "mcc": "6011", "channel": "ATM", "flagged": True},
        {"txn_id": "T-B010", "date": _days_ago(3), "type": "PURCHASE", "amount": 1240.00, "merchant": "Walmart Supercenter (off-network)", "mcc": "5999", "channel": "In-Store", "flagged": True},
        {"txn_id": "T-B011", "date": _days_ago(3), "type": "PURCHASE", "amount": 980.00,  "merchant": "Amazon (off-network)", "mcc": "5999", "channel": "Online", "flagged": True},
    ],

    # ── CC-2291: Derek Okafor — Money Mule (Third-Party Payment Scheme) ──────
    "CC-2291": [
        # Normal baseline
        {"txn_id": "T-C001", "date": _days_ago(180), "type": "PURCHASE", "amount": 2400.00, "merchant": "Ashley Furniture", "mcc": "5712", "channel": "In-Store"},
        {"txn_id": "T-C002", "date": _days_ago(175), "type": "PAYMENT_RECEIVED", "amount": 250.00, "merchant": "PAYMENT ACH", "mcc": None, "channel": "ACH"},
        {"txn_id": "T-C003", "date": _days_ago(120), "type": "PURCHASE", "amount": 1100.00, "merchant": "Ashley Furniture", "mcc": "5712", "channel": "In-Store"},
        {"txn_id": "T-C004", "date": _days_ago(115), "type": "PAYMENT_RECEIVED", "amount": 150.00, "merchant": "PAYMENT ACH", "mcc": None, "channel": "ACH"},
        # Third-party payment received (suspicious — not from cardholder's bank)
        {"txn_id": "T-C005", "date": _days_ago(26), "type": "PAYMENT_RECEIVED", "amount": 4800.00, "merchant": "PAYMENT - ORIGINATOR: KEYSTONE VENTURES LLC", "mcc": None, "channel": "ACH", "flagged": True, "flag_reason": "Large payment from unlinked third-party business"},
        # Immediate post-payment spending spree (using the credit freed up)
        {"txn_id": "T-C006", "date": _days_ago(25), "type": "PURCHASE", "amount": 1800.00, "merchant": "Jewelry Exchange (off-network)", "mcc": "5094", "channel": "In-Store", "flagged": True, "flag_reason": "High-risk MCC: Jewelry"},
        {"txn_id": "T-C007", "date": _days_ago(24), "type": "PURCHASE", "amount": 1600.00, "merchant": "Coin/Bullion Dealer (off-network)", "mcc": "5094", "channel": "In-Store", "flagged": True},
        {"txn_id": "T-C008", "date": _days_ago(24), "type": "CASH_ADVANCE", "amount": 1200.00, "merchant": "ATM - ATLANTA GA", "mcc": "6011", "channel": "ATM", "flagged": True},
        {"txn_id": "T-C009", "date": _days_ago(23), "type": "PURCHASE", "amount": 220.00, "merchant": "Western Union", "mcc": "6051", "channel": "In-Store", "flagged": True, "flag_reason": "Money transfer service — high ML risk"},
    ],
}

# ── Tool functions (Bedrock Action Group equivalents) ─────────────────────────

def get_transaction_history(account_id: str, days: int = 90) -> dict:
    """Retrieve credit card transaction history."""
    txns = TRANSACTIONS.get(account_id, [])
    cutoff = datetime.now() - timedelta(days=days)
    recent = [t for t in txns if datetime.strptime(t["date"], "%Y-%m-%d") >= cutoff]

    total_purchases = sum(t["amount"] for t in recent if t["type"] == "PURCHASE")
    total_payments = sum(t["amount"] for t in recent if t["type"] == "PAYMENT_RECEIVED")
    total_cash_advances = sum(t["amount"] for t in recent if t["type"] == "CASH_ADVANCE")
    flagged = [t for t in recent if t.get("flagged")]

    return {
        "account_id": account_id,
        "period_days": days,
        "total_transactions": len(recent),
        "total_purchases": round(total_purchases, 2),
        "total_payments": round(total_payments, 2),
        "total_cash_advances": round(total_cash_advances, 2),
        "flagged_transactions": len(flagged),
        "transactions": recent,
        "unique_merchants": list(set(t.get("merchant", "") for t in recent)),
        "mcc_codes_used": list(set(t.get("mcc") for t in recent if t.get("mcc"))),
    }


def get_customer_profile(account_id: str) -> dict:
    """Retrieve cardholder profile and KYC information."""
    profile = CUSTOMERS.get(account_id)
    if not profile:
        return {"error": f"Account {account_id} not found"}
    return profile


def detect_bust_out_pattern(account_id: str) -> dict:
    """Detect bust-out fraud: rapid credit utilization spike followed by payment cessation."""
    txns = TRANSACTIONS.get(account_id, [])
    customer = CUSTOMERS.get(account_id, {})

    cutoff_30 = datetime.now() - timedelta(days=30)
    recent_purchases = [
        t for t in txns
        if t["type"] in ("PURCHASE", "CASH_ADVANCE")
        and datetime.strptime(t["date"], "%Y-%m-%d") >= cutoff_30
    ]
    recent_payments = [
        t for t in txns
        if t["type"] == "PAYMENT_RECEIVED"
        and datetime.strptime(t["date"], "%Y-%m-%d") >= cutoff_30
    ]

    total_new_charges = sum(t["amount"] for t in recent_purchases)
    total_new_payments = sum(t["amount"] for t in recent_payments)
    credit_limit = customer.get("credit_limit", 1)
    utilization = customer.get("utilization_pct", 0)

    # Count high-risk MCCs
    high_risk_txns = [t for t in recent_purchases if MCC_RISK.get(t.get("mcc",""), ("","LOW"))[1] == "HIGH"]
    gift_card_txns = [t for t in recent_purchases if t.get("mcc") == "5999_GIFT"]
    cash_advance_txns = [t for t in recent_purchases if t["type"] == "CASH_ADVANCE"]

    bust_out_score = 0
    indicators = []

    if utilization > 90:
        bust_out_score += 30
        indicators.append(f"Utilization at {utilization}% (>90% threshold)")
    if total_new_payments < total_new_charges * 0.1:
        bust_out_score += 25
        indicators.append(f"Payment coverage only {round(total_new_payments/max(total_new_charges,1)*100,1)}% of new charges")
    if len(gift_card_txns) >= 2:
        bust_out_score += 20
        indicators.append(f"{len(gift_card_txns)} gift card transactions (${sum(t['amount'] for t in gift_card_txns):,.2f})")
    if len(cash_advance_txns) > 0:
        bust_out_score += 15
        indicators.append(f"{len(cash_advance_txns)} cash advance(s) totaling ${sum(t['amount'] for t in cash_advance_txns):,.2f}")
    if customer.get("phone_status") == "DISCONNECTED" or customer.get("email_status") == "BOUNCE":
        bust_out_score += 25
        indicators.append("Primary contact channels unresponsive (phone disconnected, email bouncing)")

    return {
        "bust_out_detected": bust_out_score >= 50,
        "bust_out_score": min(bust_out_score, 100),
        "total_new_charges_30d": round(total_new_charges, 2),
        "total_payments_30d": round(total_new_payments, 2),
        "current_utilization_pct": utilization,
        "high_risk_mcc_transactions": len(high_risk_txns),
        "gift_card_transactions": len(gift_card_txns),
        "cash_advances": len(cash_advance_txns),
        "indicators": indicators,
        "credit_limit": credit_limit,
    }


def get_cli_history(account_id: str) -> dict:
    """Retrieve credit limit increase history — key for bust-out pattern."""
    customer = CUSTOMERS.get(account_id, {})
    cli_history = customer.get("cli_history", [])
    initial_limit = customer.get("initial_credit_limit", customer.get("credit_limit", 0))
    current_limit = customer.get("credit_limit", 0)

    return {
        "account_id": account_id,
        "initial_credit_limit": initial_limit,
        "current_credit_limit": current_limit,
        "total_limit_increase": round(current_limit - initial_limit, 2),
        "increase_pct": round((current_limit - initial_limit) / max(initial_limit, 1) * 100, 1),
        "cli_events": cli_history,
        "days_since_opening": (datetime.now() - datetime.strptime(customer.get("opened","2025-01-01"), "%Y-%m-%d")).days,
    }


def get_mcc_risk_profile(account_id: str, days: int = 30) -> dict:
    """Analyze Merchant Category Code (MCC) distribution for risk assessment."""
    txns = TRANSACTIONS.get(account_id, [])
    cutoff = datetime.now() - timedelta(days=days)
    recent = [t for t in txns if t["type"] == "PURCHASE" and datetime.strptime(t["date"], "%Y-%m-%d") >= cutoff]

    mcc_breakdown = {}
    for t in recent:
        mcc = t.get("mcc", "UNKNOWN")
        mcc_name, risk = MCC_RISK.get(mcc, ("Other", "LOW"))
        if mcc not in mcc_breakdown:
            mcc_breakdown[mcc] = {"name": mcc_name, "risk": risk, "count": 0, "total": 0}
        mcc_breakdown[mcc]["count"] += 1
        mcc_breakdown[mcc]["total"] = round(mcc_breakdown[mcc]["total"] + t["amount"], 2)

    high_risk_volume = sum(v["total"] for v in mcc_breakdown.values() if v["risk"] == "HIGH")
    total_volume = sum(v["total"] for v in mcc_breakdown.values())

    return {
        "account_id": account_id,
        "period_days": days,
        "mcc_breakdown": mcc_breakdown,
        "high_risk_mcc_volume": round(high_risk_volume, 2),
        "total_volume": round(total_volume, 2),
        "high_risk_pct": round(high_risk_volume / max(total_volume, 1) * 100, 1),
        "alert": high_risk_volume / max(total_volume, 1) > 0.4,
    }


def get_peer_comparison(account_id: str) -> dict:
    """Compare card activity to peer group (same product, similar credit limit, similar tenure)."""
    customer = CUSTOMERS.get(account_id, {})
    product = customer.get("card_product", "")

    if "Amazon" in product:
        peer = {"avg_monthly_spend": 380, "avg_utilization": 28, "avg_monthly_payments": 1.8, "gift_card_pct": 3}
    elif "Lowe" in product:
        peer = {"avg_monthly_spend": 520, "avg_utilization": 22, "avg_monthly_payments": 1.3, "cash_advance_rate": 1.2}
    else:
        peer = {"avg_monthly_spend": 310, "avg_utilization": 25, "avg_monthly_payments": 1.5, "gift_card_pct": 2}

    txns = TRANSACTIONS.get(account_id, [])
    cutoff = datetime.now() - timedelta(days=30)
    recent_purchases = [t for t in txns if t["type"] == "PURCHASE" and datetime.strptime(t["date"], "%Y-%m-%d") >= cutoff]
    monthly_spend = sum(t["amount"] for t in recent_purchases)

    return {
        "account_id": account_id,
        "peer_group": f"{product} holders, similar credit limit",
        "peer_avg_monthly_spend": peer["avg_monthly_spend"],
        "account_monthly_spend": round(monthly_spend, 2),
        "spend_ratio_vs_peer": round(monthly_spend / max(peer["avg_monthly_spend"], 1), 1),
        "peer_avg_utilization_pct": peer["avg_utilization"],
        "account_utilization_pct": customer.get("utilization_pct", 0),
        "anomaly_flag": monthly_spend > peer["avg_monthly_spend"] * 4,
    }


def get_contact_change_history(account_id: str) -> dict:
    """Check for recent changes to contact information — ATO indicator."""
    customer = CUSTOMERS.get(account_id, {})
    changes = customer.get("recent_changes", [])
    return {
        "account_id": account_id,
        "recent_contact_changes": changes,
        "change_count_last_7d": len(changes),
        "ato_indicator": len(changes) >= 2,
        "note": "Multiple contact changes in short window is a primary ATO indicator",
    }
