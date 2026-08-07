"""Sum Insured — cover calculated from observed earnings. Implements §5.4 and the benefit schedule."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from shared import page_setup, inr, lakh, section_ref, formula
from engine.config import CFG
from engine import sum_insured as si_engine

page_setup("Sum Insured")

st.title("Sum Insured")
st.caption("Cover is calculated from observed earnings, not chosen from a menu. §5.4")

st.markdown(
    "Gig workers do not have the information to choose a sum insured well, so "
    "the plan makes it formula-driven. Earnings are **observed** through the "
    "Account Aggregator framework or platform APIs rather than self-declared — "
    "which is also the control that stops the death benefit being gamed upward."
)

# ------------------------------------------------------------------ sidebar
sb = st.sidebar
sb.header("Observed inputs")
monthly = sb.slider("Monthly net earnings (₹)", 5000, 45000, 22000, 500)
sb.caption("Redseer 2026: delivery ₹22,000–23,000; ride-hailing ₹37,000–39,000")
idv = sb.slider("Vehicle IDV (₹)", 20000, 150000, 65000, 5000)
p95 = sb.slider("P95 consignment value (₹)", 300, 30000, 1800, 100)

sb.header("Platform cover offset")
sb.caption("Our income benefit reduces by any platform loss-of-pay benefit for "
           "the same period. This is a clause in our own contract, not a "
           "recovery right — fixed-benefit policies carry no contribution right.")
offset = sb.number_input("Platform loss-of-pay, per day (₹)", 0, 2000, 0, 50)

sched = si_engine.full_schedule(monthly, idv=idv, p95_order_value=p95,
                                platform_loss_of_pay_daily=offset)

annual = sched["inputs"]["annual_net_earnings"]
daily = sched["inputs"]["avg_daily_net_earnings"]

c1, c2, c3 = st.columns(3)
c1.metric("Annualised net earnings", inr(annual))
c2.metric("Average daily net earnings", inr(daily))
c3.metric("Working days assumed", "26 / month")

st.divider()

# ------------------------------------------------------------------ death
left, right = st.columns(2)

with left:
    st.subheader("Accidental death / permanent total disability")
    section_ref("§5.4 — human life value approach")
    ad = sched["accidental_death"]
    formula(ad["formula"])
    st.metric("Sum insured", lakh(ad["value"]))
    if ad["binding"] == "floor":
        st.info(f"The ₹5 lakh floor is binding. Uncalculated value would be "
                f"{lakh(ad['uncapped'])}.")
    elif ad["binding"] == "ceiling":
        st.info(f"The ₹25 lakh ceiling is binding. Uncapped value would be "
                f"{lakh(ad['uncapped'])}.")
    else:
        st.caption(f"8 × {inr(annual)} = {lakh(ad['uncapped'])}, within the "
                   "₹5–25 lakh band.")

with right:
    st.subheader("Daily income benefit")
    section_ref("§5.4 — the moral hazard control is in the formula")
    dib = sched["daily_income_benefit"]
    formula(dib["formula"])
    st.metric("Benefit per day", inr(dib["value"]),
              f"{dib['replacement_ratio']:.0%} of daily earnings")
    st.dataframe(pd.DataFrame([
        {"Step": "75% of observed daily earnings", "Amount": inr(dib["gross"])},
        {"Step": "After ₹1,200 daily cap", "Amount": inr(dib["after_cap"])},
        {"Step": "Less platform loss-of-pay offset", "Amount": inr(-dib["platform_offset"])},
        {"Step": "Benefit payable per day", "Amount": inr(dib["value"])},
        {"Step": f"Maximum annual payout ({dib['max_days']} days)",
         "Amount": inr(dib["max_annual_payout"])},
    ]), width="stretch", hide_index=True)

if dib["replacement_ratio"] >= 1.0:
    st.error("**Replacement ratio is at or above 100%.** It would be more "
             "profitable for this rider to stay off the road than to ride. "
             "The 0.75 factor and the platform offset exist to prevent exactly "
             "this — check the inputs.")
else:
    st.success(
        f"Replacement ratio **{dib['replacement_ratio']:.0%}**, plus a "
        f"{dib['waiting_days']}-day waiting period and a {dib['max_days']}-day "
        "annual maximum. It must never be more profitable to stay off the road "
        "than to ride."
    )

st.divider()

# ------------------------------------------------------------------ others
l2, r2 = st.columns(2)
with l2:
    st.subheader("On-duty vehicle benefit")
    v = sched["vehicle"]
    formula(v["formula"])
    st.dataframe(pd.DataFrame([
        {"Limit": "Sum insured", "Amount": inr(v["value"])},
        {"Limit": "Per event (40%)", "Amount": inr(v["per_event"])},
        {"Limit": "Annual aggregate", "Amount": inr(v["annual_aggregate"])},
    ]), width="stretch", hide_index=True)
    st.caption("Written as a scheduled fixed benefit, not a motor own-damage "
               "policy — which is what keeps it outside the Motor Vehicles Act "
               "commercial-use exclusion (§4.3a) and, separately, kills the "
               "garage bill inflation that makes motor OD India's most "
               "fraud-prone line.")

with r2:
    st.subheader("Consignment & deduction protection")
    cg = sched["consignment"]
    formula(cg["formula"])
    st.dataframe(pd.DataFrame([
        {"Limit": "Per event", "Amount": inr(cg["per_event"])},
        {"Limit": "Annual aggregate", "Amount": inr(cg["annual_aggregate"])},
    ]), width="stretch", hide_index=True)
    st.caption("Settled as indemnity — the loss is objectively visible as a "
               "deduction on the platform payout statement, which is third-party "
               "evidence rather than a rider-submitted claim.")

st.subheader("Fixed tiers — no calculation, no dispute, instant payment")
fx = sched["fixed"]
st.dataframe(pd.DataFrame([
    {"Benefit": "Hospital daily cash", "Amount": f"{inr(fx['hospital_daily_cash'])}/day",
     "Cap": f"{fx['hospital_cash_max_days']} days = {inr(fx['hospital_cash_max_payout'])}"},
    {"Benefit": "Fracture & OPD", "Amount": f"{inr(fx['fracture_range'][0])}–{inr(fx['fracture_range'][1])}",
     "Cap": "By injury schedule"},
    {"Benefit": "Ambulance (network)", "Amount": f"Actuals to {inr(fx['ambulance_network_cap'])}",
     "Cap": "Paid direct to network partner"},
    {"Benefit": "Ambulance (out of network)", "Amount": inr(fx["ambulance_out_of_network_fixed"]),
     "Cap": "Fixed benefit"},
]), width="stretch", hide_index=True)

st.divider()

# ------------------------------------------------------------------ basis
st.subheader("Settlement basis: fixed benefit vs indemnity")
st.markdown(
    "The split is mostly dictated by what is being covered, not chosen freely. "
    "**Where we pay a fixed sum, we verify the event objectively. Where we pay "
    "actuals, we never pay cash to the claimant — we pay the provider.** That "
    "single rule handles most Indian moral hazard."
)

bdf = pd.DataFrame(CFG["benefits"])
bdf.columns = ["Benefit", "Product", "Settlement basis", "Moral hazard control"]


def _tag(v):
    if v.startswith("Fixed"):
        return "🟩 Fixed"
    if v.startswith("Indemnity"):
        return "🟧 Indemnity"
    return "🟦 Service"


bdf.insert(2, "Basis", bdf["Settlement basis"].map(_tag))

basis_filter = st.multiselect(
    "Filter by settlement basis",
    ["🟩 Fixed", "🟧 Indemnity", "🟦 Service"],
    default=["🟩 Fixed", "🟧 Indemnity", "🟦 Service"],
)
view = bdf[bdf["Basis"].isin(basis_filter)] if basis_filter else bdf

st.dataframe(view, width="stretch", hide_index=True)

counts = bdf["Settlement basis"].str.split(",").str[0].str.strip().value_counts()
fig = go.Figure(go.Pie(labels=counts.index, values=counts.values, hole=0.55,
                       marker_colors=["#7fa87f", "#d9a066", "#8c9bb5"]))
fig.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0),
                  showlegend=True)
cA, cB = st.columns([1, 2])
with cA:
    st.plotly_chart(fig, width="stretch")
with cB:
    st.markdown(
        "**Why this ratio matters.** Roughly 80% of premium sits in fixed "
        "benefits, which is what makes sub-60-second settlement possible — no "
        "bills, no assessor, no dispute. The indemnity lines are the only ones "
        "where a recovery right against another insurer could ever exist, "
        "because subrogation and contribution apply only to contracts of "
        "indemnity.\n\n"
        "**The consequence for platform cover.** Platform group cover is "
        "predominantly fixed-benefit. That means we cannot recover from the "
        "platform's insurer when we pay — a rider may legitimately claim in "
        "full under both policies. The only place an offset is justified is the "
        "income benefit, where stacking could take a rider above 100% of what "
        "they would have earned by riding."
    )
