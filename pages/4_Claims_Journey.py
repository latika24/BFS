"""Claims Journey — the 60-second settlement. §1.1 gap 04, §3.2, §3.3."""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from shared import (page_setup, page_header, kpi, inr, steps, note,
                    SEC, MUTED, PRIMARY, ACCENT, OK, BAD)
from engine.config import CFG
from engine import sum_insured as si_engine

page_setup("Claims Journey")

page_header(
    "Claims Journey",
    f"{SEC['gap']} · {SEC['value_prop']}",
    "Unions in Telangana and Karnataka have documented injured delivery "
    "partners waiting months for platform insurance to settle. Where the core "
    "problem is that no worker trusts an insurer to actually pay, speed of "
    "settlement is not a service metric — it is the product.")

# ------------------------------------------------------------------ compare
c1, c2, c3 = st.columns(3)
kpi(c1, "Platform cover today", "Weeks to months", "documented by worker unions")
kpi(c2, "Our Tier 1 target", "Under 60 seconds", "~55% of claims by count")
kpi(c3, "Our Tier 2 target", "24–48 hours", "income benefit, ~35% of claims")

st.write("")
st.divider()

# ------------------------------------------------------------------ simulator
st.markdown("### Run a claim")
st.markdown(
    f"<div style='color:{MUTED};max-width:88ch'>Pick what happened. The engine "
    "adjudicates it the way the product would — checking the telematics trace "
    "we already hold rather than asking the rider for documents.</div>",
    unsafe_allow_html=True)
st.write("")

sc1, sc2, sc3 = st.columns(3)
with sc1:
    incident = st.selectbox("What happened", [
        "Fracture — off the road for 6 weeks",
        "Hospital admission — 4 days",
        "Ambulance called at the scene",
        "Phone screen smashed",
        "Platform deducted for a spilled order",
        "Two-wheeler damaged on shift",
    ])
with sc2:
    earnings = st.slider("Monthly net earnings (₹)", 8000, 40000, 22000, 500)
with sc3:
    cover_live = st.toggle("Cover was live at the time", value=True)
    impact = st.toggle("Telematics shows an impact signature", value=True)

sched = si_engine.full_schedule(earnings)
dib = sched["daily_income_benefit"]["value"]

CLAIMS = {
    "Fracture — off the road for 6 weeks": dict(
        tier=2, basis="Fixed benefit",
        heads=[("Fracture benefit (schedule)", 18000),
               ("Daily income benefit, 39 days after 3-day wait", dib * 39)],
        evidence="X-ray confirming the fracture, plus a panel-doctor certificate",
        control="Objective injury evidence, not a certificate alone. The "
                "telematics contradiction check runs daily — a rider drawing "
                "income benefit while the SDK shows them riding another app is "
                "a provable, automatic denial.",
        eta="24–48 hours to first payment"),
    "Hospital admission — 4 days": dict(
        tier=1, basis="Fixed benefit",
        heads=[("Hospital daily cash, 4 days", 4000)],
        evidence="Discharge summary uploaded in the app",
        control="Minimum 24-hour admission; 30-day annual cap; the benefit is "
                "set below the true daily cost of being admitted so an "
                "unnecessary admission is never profitable.",
        eta="Under 60 seconds"),
    "Ambulance called at the scene": dict(
        tier=1, basis="Indemnity — paid to network",
        heads=[("Ambulance, network partner", 3200)],
        evidence="Automatic — dispatched through our partner network",
        control="Paid direct to the ambulance operator, never as cash to the "
                "rider. No claimant-submitted invoice means no invoice inflation.",
        eta="Under 60 seconds"),
    "Phone screen smashed": dict(
        tier=1, basis="Indemnity — paid to repair network",
        heads=[("Screen repair, network rate", 4400)],
        evidence="Photo of the device, repair booked in-app",
        control="Settled directly with the repair network. Theft, as opposed to "
                "damage, additionally requires an FIR.",
        eta="Under 60 seconds"),
    "Platform deducted for a spilled order": dict(
        tier=1, basis="Indemnity",
        heads=[("Deduction protection", 800)],
        evidence="The deduction appears on the platform payout statement",
        control="Reimburse the actual deduction shown on the statement — "
                "third-party evidence, not a rider claim form. Per-event cap "
                "plus a 10× annual aggregate, and a frequency flag on outliers.",
        eta="Under 60 seconds"),
    "Two-wheeler damaged on shift": dict(
        tier=2, basis="Fixed benefit — scheduled",
        heads=[("On-duty vehicle benefit, scheduled repair", 9500)],
        evidence="Baseline condition photos from inception, plus impact trace",
        control="A scheduled benefit rather than a motor own-damage policy — "
                "which is both what keeps it outside the Motor Vehicles Act "
                "commercial-use exclusion and what kills garage bill inflation. "
                "Paid to the network garage.",
        eta="24–48 hours"),
}

claim = CLAIMS[incident]
total = sum(v for _, v in claim["heads"])

st.write("")
go_btn = st.button("Submit claim", type="primary", width="stretch")

if go_btn:
    ph = st.empty()
    for label in ["Receiving first notice of loss…",
                  "Pulling the last five minutes of telematics…",
                  "Checking cover status and location plausibility…",
                  "Matching to the benefit schedule…",
                  "Releasing payment to UPI…"]:
        ph.info(label)
        time.sleep(0.35)
    ph.empty()

if not cover_live:
    st.error("**Declined — cover was not live.** The shift window had not been "
             "declared and the route-shape classifier does not identify "
             "on-duty riding. This is the anti-selection control: cover attaches "
             "to a declared shift, not a toggle the rider can flip when they "
             "expect trouble.")
elif not impact and claim["tier"] != 1:
    st.warning("**Referred for investigation.** Cover was live, but the "
               "accelerometer shows no impact signature — a genuine crash reads "
               "as a deceleration spike followed by device stillness. Routed to "
               "Tier 3 and a human reviews it. This is the exception, not the norm.")
else:
    st.success(f"**Approved — {inr(total)} released.** {claim['eta']}")

    r1, r2, r3 = st.columns(3)
    kpi(r1, "Amount", inr(total), claim["basis"])
    kpi(r2, "Settlement tier", f"Tier {claim['tier']}",
        "instant" if claim["tier"] == 1 else "fast-track")
    kpi(r3, "Time to money", claim["eta"], "vs months on platform cover")

    st.write("")
    for head, amt in claim["heads"]:
        st.markdown(f"- **{head}** — {inr(amt)}")

st.write("")
b1, b2 = st.columns(2)
with b1:
    st.markdown("**Evidence required from the rider**")
    st.markdown(f"<div style='color:{MUTED};font-size:.9rem'>{claim['evidence']}"
                "</div>", unsafe_allow_html=True)
with b2:
    st.markdown("**The moral hazard control on this benefit**")
    st.markdown(f"<div style='color:{MUTED};font-size:.9rem'>{claim['control']}"
                "</div>", unsafe_allow_html=True)

st.divider()

# ------------------------------------------------------------------ the flow
st.markdown("### Why it can be this fast")
st.markdown(
    f"<div style='color:{MUTED};max-width:88ch'>Because the product is "
    "usage-based, we already know whether cover was live, where the rider was, "
    "and whether the device registered an impact. The claim can be adjudicated "
    "before the rider finishes describing it. An annual-premium insurer with no "
    "telematics has to begin by establishing the facts.</div>",
    unsafe_allow_html=True)
st.write("")

steps([
    ("Rider taps one button",
     "No form. The app captures a 30-second video, GPS, timestamp and the "
     "preceding five minutes of telematics automatically.", "0 sec"),
    ("Machine check against data we already hold",
     "Was cover live? Was the device in motion? Is the location plausible "
     "against the route? Does the accelerometer show an impact?", "2 sec"),
    ("Fixed benefits auto-paid to UPI",
     "Ambulance, hospital cash, fracture, phone, small deductions — machine "
     "verified, no human in the loop. About 55% of claims by count.", "under 60 sec"),
    ("A Claim Saathi calls, in the rider's language",
     "Within 15 minutes of a crash. Evaluated on worker satisfaction rather "
     "than claims saved, and briefed to represent the worker's interest — "
     "including when a claim must be declined.", "15 min"),
    ("Income benefit released after the 3-day wait",
     "Panel-doctor certificate plus objective injury evidence. A human reviews "
     "the exception, not the norm.", "24–48 hrs"),
])

st.divider()

# ------------------------------------------------------------------ mix
st.markdown("### The settlement mix, and why the ratio matters")

m1, m2 = st.columns([1, 1.3])
with m1:
    fig = go.Figure(go.Pie(
        labels=["Tier 1 — instant", "Tier 2 — fast-track", "Tier 3 — investigated"],
        values=[55, 35, 10], hole=0.58,
        marker_colors=[OK, PRIMARY, "#93A5A3"],
        textinfo="label+percent"))
    fig.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0),
                      showlegend=False)
    st.plotly_chart(fig, width="stretch")

with m2:
    st.markdown(
        f"<div style='color:{MUTED};line-height:1.65;font-size:.93rem'>"
        "Roughly <b>80% of premium sits in fixed benefits</b> — a set sum on a "
        "defined event, with no assessment of actual loss. That is what makes "
        "sub-60-second settlement possible: there is nothing to assess, only an "
        "event to verify.<br><br>"
        "The remaining lines settle as indemnity, where the amount varies and "
        "has to be measured. There the rule inverts: <b>we never pay cash to "
        "the claimant, we pay the provider</b> — the ambulance operator, the "
        "repair network, the garage. A rider-submitted invoice is the thing "
        "that invites inflation.<br><br>"
        "One consequence worth being precise about: subrogation and contribution "
        "apply only to contracts of indemnity. Platform group cover is "
        "predominantly fixed-benefit, so we <b>cannot</b> recover from the "
        "platform's insurer when we pay. A rider may legitimately claim in full "
        "under both policies. The only place an offset is justified is the "
        "income benefit, where stacking could take a rider above 100% of what "
        "they would have earned by riding.</div>",
        unsafe_allow_html=True)

st.write("")
note("<b>Published claims data is the trust instrument.</b> Monthly settlement "
     "ratio, median turnaround and the reasons for every rejection, in "
     "aggregate. In a market whose core problem is that nobody trusts an "
     "insurer to pay, this is not a marketing gesture — it is the moat. The "
     "corresponding discipline: never let the repudiation rate creep above 5%, "
     "and resolve genuinely marginal claims in the worker's favour.")
