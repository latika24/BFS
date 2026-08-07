"""
The platform's live state: riders, policies, premium ledger and claims.

This is the closest thing the prototype has to a database. Everything a rider
does — buying cover, riding a shift, raising a claim — writes here, and the
insurer console reads the same store. Buy a policy on the rider side and the
insurer's book grows; raise a claim and it lands in the claims queue.

Backed by st.session_state, so it persists while the browser tab is open and
resets on a hard refresh.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta

import streamlit as st

from .config import CFG
from . import pricing, sum_insured as si_engine, safety_score as ss

KEY = "suraksha_store"


# --------------------------------------------------------------------- models
@dataclass
class Rider:
    rider_id: str = "R-100482"
    name: str = "Ramesh Kumar"
    phone: str = "+91 98••• ••231"
    age: int = 29
    city: str = "Metro (Mumbai, Delhi, Bengaluru)"
    vehicle: str = "<=110cc petrol"
    vehicle_reg: str = "KA 05 HJ 4471"
    platform: str = "Food delivery"
    platforms_active: tuple = ("Swiggy", "Zepto")
    monthly_net_earnings: int = 22400
    joined: str = ""
    safety_score: float = 74.0
    telematics_consent: bool = True
    kyc_done: bool = True

    @property
    def daily_net_earnings(self) -> float:
        return self.monthly_net_earnings / 26.0

    @property
    def tenure_months(self) -> int:
        if not self.joined:
            return 0
        d = datetime.fromisoformat(self.joined)
        return max(0, int((datetime.now() - d).days / 30))


@dataclass
class Policy:
    policy_id: str
    rider_id: str
    tier: str
    status: str = "Active"          # Active | Lapsed | Cancelled
    started: str = ""
    addons: list = field(default_factory=list)
    hours_covered: float = 0.0
    premium_collected: float = 0.0
    wallet: float = 0.0
    claims_made: int = 0

    @property
    def sum_insured(self) -> int:
        return CFG["tiers"][self.tier]["sum_insured_reference"]

    @property
    def base_rate(self) -> float:
        return CFG["tiers"][self.tier]["price_per_hour"]


@dataclass
class Claim:
    claim_id: str
    policy_id: str
    rider_id: str
    rider_name: str
    incident: str
    head: str
    basis: str                       # Fixed benefit | Indemnity
    tier: int                        # settlement tier 1/2/3
    amount_claimed: float
    amount_approved: float = 0.0
    status: str = "Submitted"        # Submitted|Verifying|Approved|Paid|Declined|Investigating
    submitted: str = ""
    settled: str = ""
    cover_live: bool = True
    telematics_impact: bool = True
    flags: list = field(default_factory=list)
    decline_reason: str = ""

    @property
    def turnaround_hours(self) -> float | None:
        if not self.settled:
            return None
        a = datetime.fromisoformat(self.submitted)
        b = datetime.fromisoformat(self.settled)
        return (b - a).total_seconds() / 3600.0


# ------------------------------------------------------------------ incidents
INCIDENTS = {
    "Fracture — cannot ride": dict(
        head="Fracture benefit + daily income benefit", basis="Fixed benefit",
        tier=2, base=18000, income_days=39,
        evidence="X-ray and panel-doctor certificate",
        control="Objective injury evidence plus a daily telematics check that "
                "the rider is not working another app"),
    "Hospital admission": dict(
        head="Hospital daily cash", basis="Fixed benefit", tier=1, base=4000,
        evidence="Discharge summary photo",
        control="Minimum 24-hour admission; 30-day annual cap"),
    "Ambulance at the scene": dict(
        head="Ambulance", basis="Indemnity", tier=1, base=3200,
        evidence="Automatic — dispatched via partner network",
        control="Paid direct to the operator, never cash to the rider"),
    "Phone screen smashed": dict(
        head="Phone screen", basis="Indemnity", tier=1, base=4400,
        evidence="Photo of the device",
        control="Settled with the repair network; theft needs an FIR"),
    "Platform deducted for a spoiled order": dict(
        head="Deduction protection", basis="Indemnity", tier=1, base=800,
        evidence="Platform payout statement",
        control="Reimburse the actual deduction shown; frequency flag on outliers"),
    "Two-wheeler damaged on shift": dict(
        head="On-duty vehicle benefit", basis="Fixed benefit (scheduled)",
        tier=2, base=9500,
        evidence="Baseline photos from inception plus impact trace",
        control="Scheduled benefit paid to the network garage — no bill inflation"),
}


# ------------------------------------------------------------------ the store
def _new():
    now = datetime.now()
    rider = Rider(joined=(now - timedelta(days=247)).isoformat())

    pol = Policy(
        policy_id="SUR-2026-004821", rider_id=rider.rider_id,
        tier="Suraksha Plus", started=(now - timedelta(days=247)).isoformat(),
        addons=["Phone screen"], hours_covered=1642.0,
        premium_collected=4180.0, wallet=386.0, claims_made=2)

    hist = [
        Claim(claim_id="CLM-88214", policy_id=pol.policy_id,
              rider_id=rider.rider_id, rider_name=rider.name,
              incident="Ambulance at the scene", head="Ambulance",
              basis="Indemnity", tier=1, amount_claimed=2800,
              amount_approved=2800, status="Paid",
              submitted=(now - timedelta(days=96)).isoformat(),
              settled=(now - timedelta(days=96, seconds=-41)).isoformat()),
        Claim(claim_id="CLM-91077", policy_id=pol.policy_id,
              rider_id=rider.rider_id, rider_name=rider.name,
              incident="Phone screen smashed", head="Phone screen",
              basis="Indemnity", tier=1, amount_claimed=4400,
              amount_approved=4400, status="Paid",
              submitted=(now - timedelta(days=34)).isoformat(),
              settled=(now - timedelta(days=34, seconds=-55)).isoformat()),
    ]

    # 30 days of daily debits, so the ledger looks lived-in
    rng = random.Random(7)
    ledger = []
    for i in range(30, 0, -1):
        d = now - timedelta(days=i)
        hrs = 0.0 if d.weekday() == 6 and rng.random() < 0.5 else round(rng.uniform(5.5, 10.5), 1)
        rate = round(rng.uniform(2.1, 4.4), 2)
        ledger.append({"date": d.date().isoformat(), "hours": hrs,
                       "rate": rate, "amount": round(hrs * rate, 2)})

    return {
        "rider": rider,
        "policies": [pol],
        "claims": hist,
        "ledger": ledger,
        "on_duty": True,
        "hours_today": 5.5,
        "counter": 91078,
        "pol_counter": 4822,
        "events": [],
    }


def store() -> dict:
    if KEY not in st.session_state:
        st.session_state[KEY] = _new()
    return st.session_state[KEY]


def reset():
    st.session_state[KEY] = _new()


def log(msg: str):
    store()["events"].insert(0, {
        "at": datetime.now().strftime("%H:%M:%S"), "msg": msg})


# ------------------------------------------------------------------ rider ops
def rider() -> Rider:
    return store()["rider"]


def active_policies() -> list[Policy]:
    return [p for p in store()["policies"] if p.status == "Active"]


def buy_policy(tier: str, addons: list[str]) -> Policy:
    s = store()
    s["pol_counter"] += 1
    p = Policy(policy_id=f"SUR-2026-{s['pol_counter']:06d}",
               rider_id=s["rider"].rider_id, tier=tier,
               started=datetime.now().isoformat(), addons=list(addons))
    s["policies"].append(p)
    log(f"Policy {p.policy_id} issued — {tier}")
    return p


def cancel_policy(policy_id: str):
    for p in store()["policies"]:
        if p.policy_id == policy_id:
            p.status = "Cancelled"
            log(f"Policy {policy_id} cancelled")


def current_rate(hours: float | None = None, time_band: str = "19:00-23:00",
                 weather: str = "Clear") -> dict:
    """Price the rider's current hour under live conditions."""
    r = rider()
    pols = active_policies()
    tier = pols[0].tier if pols else "Suraksha Plus"
    si = CFG["tiers"][tier]["sum_insured_reference"]
    prof = pricing.RiderProfile(
        age=r.age, city=r.city, vehicle=r.vehicle, platform=r.platform,
        tenure_months=r.tenure_months,
        safety_score=r.safety_score if r.telematics_consent else 78.0,
        sum_insured=si, tier=tier)
    shift = pricing.ShiftContext(
        hours=hours if hours else max(store()["hours_today"], 0.5),
        time_band=time_band, weather=weather, days_per_month=26)
    return pricing.quote(prof, shift)


def benefits() -> dict:
    return si_engine.full_schedule(rider().monthly_net_earnings)


# ------------------------------------------------------------------ claims
def raise_claim(incident: str, cover_live: bool = True,
                telematics_impact: bool = True) -> Claim:
    s = store()
    s["counter"] += 1
    spec = INCIDENTS[incident]
    r = s["rider"]
    pols = active_policies()

    amount = float(spec["base"])
    if spec.get("income_days"):
        dib = si_engine.daily_income_benefit(r.daily_net_earnings)["value"]
        amount += dib * spec["income_days"]

    c = Claim(claim_id=f"CLM-{s['counter']}",
              policy_id=pols[0].policy_id if pols else "—",
              rider_id=r.rider_id, rider_name=r.name,
              incident=incident, head=spec["head"], basis=spec["basis"],
              tier=spec["tier"], amount_claimed=round(amount),
              submitted=datetime.now().isoformat(),
              cover_live=cover_live, telematics_impact=telematics_impact)

    if not cover_live:
        c.flags.append("Cover not live at reported time")
    if not telematics_impact:
        c.flags.append("No impact signature in accelerometer trace")
    if amount > 40000:
        c.flags.append("High value — Tier 3 review")

    s["claims"].insert(0, c)
    log(f"Claim {c.claim_id} submitted — {incident}")
    return c


def adjudicate(claim: Claim) -> Claim:
    """Machine decision, exactly as the product would run it."""
    if not claim.cover_live:
        claim.status = "Declined"
        claim.decline_reason = (
            "Cover was not live. No shift was declared and the route-shape "
            "classifier does not identify on-duty riding at the reported time.")
        claim.settled = datetime.now().isoformat()
    elif not claim.telematics_impact and claim.tier != 1:
        claim.status = "Investigating"
        claim.flags.append("Routed to Tier 3 — human review")
    elif claim.tier == 1:
        claim.status = "Paid"
        claim.amount_approved = claim.amount_claimed
        claim.settled = datetime.now().isoformat()
    else:
        claim.status = "Approved"
        claim.amount_approved = claim.amount_claimed
        claim.settled = datetime.now().isoformat()

    if claim.status in ("Paid", "Approved"):
        for p in store()["policies"]:
            if p.policy_id == claim.policy_id:
                p.claims_made += 1
    log(f"Claim {claim.claim_id} → {claim.status}")
    return claim


def settle(claim: Claim, approved_amount: float | None = None):
    claim.status = "Paid"
    claim.amount_approved = (approved_amount if approved_amount is not None
                             else claim.amount_claimed)
    claim.settled = datetime.now().isoformat()
    log(f"Claim {claim.claim_id} settled — {claim.amount_approved:,.0f}")


def decline(claim: Claim, reason: str):
    claim.status = "Declined"
    claim.decline_reason = reason
    claim.amount_approved = 0.0
    claim.settled = datetime.now().isoformat()
    log(f"Claim {claim.claim_id} declined")


def claims(status: str | None = None) -> list[Claim]:
    cs = store()["claims"]
    return [c for c in cs if c.status == status] if status else cs


def open_claims() -> list[Claim]:
    return [c for c in store()["claims"]
            if c.status in ("Submitted", "Verifying", "Approved", "Investigating")]


# ------------------------------------------------------------------ metrics
def claim_metrics() -> dict:
    cs = store()["claims"]
    settled = [c for c in cs if c.settled]
    paid = [c for c in cs if c.status == "Paid"]
    declined = [c for c in cs if c.status == "Declined"]
    tats = [c.turnaround_hours for c in settled if c.turnaround_hours is not None]
    instant = [t for t in tats if t is not None and t < 0.05]
    return {
        "total": len(cs),
        "open": len(open_claims()),
        "paid": len(paid),
        "declined": len(declined),
        "settlement_ratio": (len(paid) / len(settled)) if settled else 0.0,
        "repudiation_rate": (len(declined) / len(settled)) if settled else 0.0,
        "median_tat_hours": (sorted(tats)[len(tats) // 2] if tats else 0.0),
        "instant_share": (len(instant) / len(tats)) if tats else 0.0,
        "paid_amount": sum(c.amount_approved for c in paid),
    }


def ledger_df():
    import pandas as pd
    return pd.DataFrame(store()["ledger"])
