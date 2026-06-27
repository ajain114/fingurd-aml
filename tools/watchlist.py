"""
Watchlist & Identity Verification — Synchrony PLCC context.
Mirrors Bedrock Action Group calls to:
  - OFAC SDN / OFAC Consolidated Sanctions
  - FinCEN 314(a) law enforcement request list
  - LexisNexis / Equifax FraudIQ identity verification
  - Social media / device fingerprint (fraud consortium)
  - Internal do-not-book / declined account registry
"""

# ── Internal fraud consortium / do-not-book registry ────────────────────────

INTERNAL_FRAUD_REGISTRY = [
    {"ssn_last4": "3318", "dob": "1989-03-12", "name": "JAMES HOLLOWAY",
     "flag": "SYNTHETIC_IDENTITY_SUSPECTED", "source": "ACFE Fraud Consortium 2025-Q2",
     "detail": "SSN 3318 pattern matches confirmed synthetic identity ring targeting retail card issuers"},
    {"phone": "555-0183", "name": "JAMES HOLLOWAY",
     "flag": "MULE_NETWORK", "source": "Internal Fraud Watch 2026-03",
     "detail": "Phone number appears in 4 separate Synchrony card applications"},
]

# ── OFAC SDN ─────────────────────────────────────────────────────────────────

OFAC_SDN = [
    {"name": "KEYSTONE VENTURES OFFSHORE LLC", "country": "KY", "type": "Entity", "program": "NARCOTICS",
     "detail": "Designated 2024-11-12 for facilitating drug cartel financial flows"},
]

# ── FinCEN 314(a) ─────────────────────────────────────────────────────────────

FINCEN_314A = [
    {"name": "JAMES HOLLOWAY", "dob": "1989-03-12", "ssn_last4": "3318",
     "case_ref": "314A-2026-1140", "requesting_agency": "FBI - Financial Crimes Unit Columbus OH"},
]

# ── Device / velocity fraud signals ──────────────────────────────────────────

DEVICE_SIGNALS = {
    "CC-4821": {
        "device_count": 4,
        "application_device": "Device-A9F2 (iPhone 14)",
        "last_login_device": "Device-X7K1 (Unknown Android)",
        "device_flag": "MULTIPLE_DEVICE_SWITCH",
        "velocity_flag": "Same device (Device-A9F2) used in 3 other Synchrony card applications (2025-Q4)",
        "ip_flag": "Last login IP geolocated to VPN exit node (NordVPN)",
    },
    "CC-7734": {
        "device_count": 1,
        "application_device": "Device-M3R8 (MacBook Pro)",
        "last_login_device": "Device-Z9P2 (Unknown — new device)",
        "device_flag": "NEW_DEVICE_POST_CONTACT_CHANGE",
        "velocity_flag": None,
        "ip_flag": "Login from Orlando FL IP — account historically accessed from Tampa FL",
    },
    "CC-2291": {
        "device_count": 1,
        "application_device": "Device-B2L5 (Samsung Galaxy)",
        "last_login_device": "Device-B2L5 (Samsung Galaxy)",
        "device_flag": "CLEAN",
        "velocity_flag": None,
        "ip_flag": None,
    },
}

# ── Identity verification results ─────────────────────────────────────────────

IDENTITY_VERIFICATION = {
    "CC-4821": {
        "name_match": "PASS",
        "address_match": "FAIL - Address does not match USPS records",
        "ssn_match": "PASS",
        "ssn_issuance_anomaly": True,
        "ssn_detail": "SSN issued 2019; DOB indicates individual born 1989 — 30yr issuance gap (synthetic identity pattern)",
        "dob_match": "PASS",
        "phone_match": "FAIL - Phone not verified; currently disconnected",
        "email_match": "FAIL - Email domain registered 6 weeks before card application",
        "overall": "HIGH RISK — Multiple identity verification failures",
        "idv_score": 41,  # out of 100
    },
    "CC-7734": {
        "name_match": "PASS",
        "address_match": "CHANGED - Original address verified; new address not yet verified",
        "ssn_match": "PASS",
        "ssn_issuance_anomaly": False,
        "dob_match": "PASS",
        "phone_match": "CHANGED - New phone active; old phone still associated with another account",
        "email_match": "CHANGED - New email domain not matching prior email history",
        "overall": "MEDIUM-HIGH RISK — Recent multi-field contact change pattern (ATO indicator)",
        "idv_score": 62,
    },
    "CC-2291": {
        "name_match": "PASS",
        "address_match": "PASS",
        "ssn_match": "PASS",
        "ssn_issuance_anomaly": False,
        "dob_match": "PASS",
        "phone_match": "PASS",
        "email_match": "PASS",
        "overall": "LOW RISK — Identity verified; risk is behavioral (payment source)",
        "idv_score": 78,
    },
}

# ── Tool functions ────────────────────────────────────────────────────────────

def verify_identity(account_id: str) -> dict:
    """Run identity verification against LexisNexis / Equifax FraudIQ."""
    return IDENTITY_VERIFICATION.get(account_id, {"error": "Account not found"})


def check_internal_fraud_registry(name: str, ssn_last4: str = "", phone: str = "") -> dict:
    """Check Synchrony's internal fraud watch list and ACFE consortium data."""
    name_upper = name.upper()
    hits = [
        r for r in INTERNAL_FRAUD_REGISTRY
        if name_upper in r.get("name","").upper()
        or (ssn_last4 and r.get("ssn_last4","") == ssn_last4)
        or (phone and phone in r.get("phone",""))
    ]
    return {
        "searched": {"name": name, "ssn_last4": ssn_last4},
        "registry_hit": len(hits) > 0,
        "hits": hits,
        "source": "Synchrony Internal Fraud Watch + ACFE Retail Card Fraud Consortium",
    }


def check_ofac_watchlist(name: str, country: str = "") -> dict:
    """Screen against OFAC SDN and consolidated sanctions list."""
    name_upper = name.upper()
    hits = [e for e in OFAC_SDN if name_upper in e["name"] or e["name"] in name_upper]
    return {
        "searched_name": name,
        "ofac_hit": len(hits) > 0,
        "hits": hits,
        "lists_checked": ["OFAC SDN", "OFAC Consolidated", "EU Sanctions", "UN Security Council"],
        "screening_date": "2026-06-27",
    }


def check_fincen_314a(name: str, ssn_last4: str = "") -> dict:
    """Check FinCEN 314(a) active law enforcement request list."""
    name_upper = name.upper()
    hits = [
        e for e in FINCEN_314A
        if name_upper in e["name"].upper()
        and (not ssn_last4 or e["ssn_last4"] == ssn_last4)
    ]
    return {
        "searched_name": name,
        "fincen_314a_hit": len(hits) > 0,
        "hits": hits,
        "note": "314(a) hit indicates active law enforcement investigation — contact BSA Officer immediately",
    }


def get_device_signals(account_id: str) -> dict:
    """Retrieve device fingerprint and velocity signals from fraud platform."""
    return DEVICE_SIGNALS.get(account_id, {
        "account_id": account_id, "device_flag": "CLEAN", "velocity_flag": None, "ip_flag": None
    })


def check_sar_history(account_id: str) -> dict:
    """Retrieve prior SAR filings for this cardholder."""
    SAR_HISTORY = {
        "CC-2291": {
            "prior_sars": 0,
            "notes": "No prior SARs; however, payment source (Keystone Ventures LLC) has OFAC designation",
        }
    }
    return SAR_HISTORY.get(account_id, {"prior_sars": 0, "notes": "No prior SARs on file"})


def check_related_accounts(account_id: str) -> dict:
    """Find Synchrony accounts linked by SSN, phone, email, address, or device."""
    LINKED = {
        "CC-4821": [
            {"account": "CC-5918", "link": "Same device fingerprint (Device-A9F2)", "name": "Robert Kim",
             "status": "Closed - Charge-off 2025-12", "reason": "Suspected bust-out"},
            {"account": "CC-6342", "link": "Same device fingerprint (Device-A9F2)", "name": "Amanda Torres",
             "status": "Active", "current_utilization": "94%"},
        ],
        "CC-7734": [
            {"account": "CC-4408", "link": "Old phone number now associated", "name": "Unknown",
             "status": "Pending investigation"},
        ],
    }
    return {
        "account_id": account_id,
        "linked_accounts": LINKED.get(account_id, []),
        "link_count": len(LINKED.get(account_id, [])),
        "note": "Linked accounts may indicate organized fraud ring activity",
    }
