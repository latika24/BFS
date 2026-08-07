"""Cover & Benefits — sums insured derived from observed earnings. §1.2."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from shared import (page_setup, page_header, kpi, inr, lakh, formula, note,
                    SEC, MUTED, PRIMARY, ACCENT, OK, BAD)
from engine.config import CFG
from engine import sum_insured as si_engine

page_setup("Cover & Benefits")

page_header(
    "Cover & Benefits",
    SEC["what_we_sell"],
    "Benefit amounts are dynamic, not flat, and this is deliberate. Because "
    "both the death benefit and the income benefit are derived from earnings we "
    "observe through the Account Aggregator framework rather than from a figure "
    "the worker declares, they cannot be inflated at the point of claim — "
    "precisely the moral hazard a flat benefit invites.")

# ------------------------------------------------------------------ sidebar
sb = st.sidebar
sb.header("Observed inputs")
monthly = sb.slider("Monthly net earnings (₹)", 5000, 45000, 22000, 500)
sb.caption("Redseer 2026 — delivery ₹22,000–23,000, ride-hailing ₹37,000–39,000")
idv = sb.slider("Vehicle IDV (₹)", 20000, 150000, 65000, 5000)
p95 = sb.slider("P95 consignment value (₹)", 300, 30000, 1800, 100)

sb.header("Platform cover offset")
sb.caption("Our income benefit reduces by any platform loss-of-pay benefit for "
           "the same period. This is a clause in our own contract, not a "
           "recovery right — fixed-benefit policies carry no contribution right.")
offset = sb.number_input("Platform loss-of-pay per day (₹)", 0, 2000, 0, 50)

sched = si_engine.full_schedule(monthly, idv=idv, p95_order_value=p95,
                                platform_loss_of_pay_daily=offset)
annual = sched["inputs"]["annual_net_earnings"]
daily = sched["inputs"]["avg_daily_net_earnings"]
ad = sched["accidental_death"]
dib = sched["daily_income_benefit"]

k1, k2, k3, k4 = st.columns(4)
kpi(k1, "Observed annual earnings", inr(annual), "via Account Aggregator")
kpi(k2, "Death / PTD benefit", lakh(ad["value"]), "8× annualised earnings")
kpi(k3, "Income benefit", f"{inr(dib['value'])}/day",
    f"{dib['replacement_ratio']:.0%} replacement")
kpi(k4, "Max income payout", inr(dib["max_annual_payout"]),
    f"{dib['max_days']} days a year")

st.write("")
st.divider()

# ------------------------------------------------------------------ scaling
st.markdown("### Benefits scale with what the rider actually earns")
st.markdown(f"<div class='ref'>{SEC['what_we_sell']}</div>", unsafe_allow_html=True)

s1, s2 = st.columns([1.3, 1])
with s1:
    xs = list(range(6000, 45001, 1000))
    ad_line = [si_engine.accidental_death(x * 12)["value"] / 1e5 for x in xs]
    dib_line = [si_engine.daily_income_benefit(x / 26.0)["value"] for x in xs]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ad_line, name="Death benefit (₹ lakh)",
                             line=dict(color=PRIMARY, width=3)))
    fig.add_trace(go.Scatter(x=xs, y=dib_line, name="Income benefit (₹/day)",
                             line=dict(color=ACCENT, width=3), yaxis="y2"))
    fig.add_vline(x=monthly, line_dash="dot", line_color="#666",
                  annotation_text="this rider")
    fig.update_layout(
        height=360, margin=dict(l=0, r=0, t=26, b=0),
        xaxis_title="Monthly net earnings (₹)",
        yaxis=dict(title="Death benefit (₹ lakh)"),
        yaxis2=dict(title="Income benefit (₹/day)", overlaying="y", side="right",
                    showgrid=False),
        legend=dict(orientation="h", y=1.16))
    st.plotly_chart(fig, width="stretch")
    st.caption("Both curves flatten where the caps bind — ₹25 lakh on the death "
               "benefit and ₹1,200 a day on the income benefit. The floors and "
               "ceilings are what keep the book insurable at both ends.")

with s2:
    st.markdown("**Death / permanent total disability**")
    formula(ad["formula"])
    if ad["binding"] == "floor":
        st.info(f"The ₹5 lakh floor binds. Uncapped: {lakh(ad['uncapped'])}.")
    elif ad["binding"] == "ceiling":
        st.info(f"The ₹25 lakh ceiling binds. Uncapped: {lakh(ad['uncapped'])}.")
    else:
        st.caption(f"8 × {inr(annual)} = {lakh(ad['uncapped'])}, inside the band.")

    st.markdown("**Daily income benefit**")
    formula(dib["formula"])
    st.dataframe(pd.DataFrame([
        {"Step": "75% of observed daily earnings", "Amount": inr(dib["gross"])},
        {"Step": "After the ₹1,200 daily cap", "Amount": inr(dib["after_cap"])},
        {"Step": "Less platform loss-of-pay offset",
         "Amount": inr(-dib["platform_offset"])},
        {"Step": "Payable per day", "Amount": inr(dib["value"])},
    ]), width="stretch", hide_index=True)

if dib["replacement_ratio"] >= 1.0:
    st.error("**Replacement ratio at or above 100%.** It would be more "
             "profitable for this rider to stay off the road than to ride. The "
             "0.75 factor and the platform offset exist to prevent exactly this.")
else:
    st.success(
        f"Replacement ratio **{dib['replacement_ratio']:.0%}**, a "
        f"{dib['waiting_days']}-day wait and a {dib['max_days']}-day annual "
        "maximum. The 0.75 factor is the control: it must never be more "
        "profitable to stay off the road than to ride.")

st.divider()

# ------------------------------------------------------------------ two covers
st.markdown("### Two covers on a single policy")

t1, t2 = st.columns(2)
with t1:
    st.markdown(f"#### Rider Shield")
    st.markdown(f"<div style='color:{MUTED};font-size:.9rem'>The person — "
                "accident, disability, and the loss that actually happens.</div>",
                unsafe_allow_html=True)
    st.dataframe(pd.DataFrame([
        {"Benefit": "Accidental death", "Amount": lakh(ad["value"])},
        {"Benefit": "Permanent total disability", "Amount": "100% of SI"},
        {"Benefit": "Permanent partial disability", "Amount": "Scaled schedule"},
        {"Benefit": "Daily income benefit", "Amount": f"{inr(dib['value'])}/day"},
        {"Benefit": "Hospital daily cash",
         "Amount": f"{inr(sched['fixed']['hospital_daily_cash'])}/day"},
        {"Benefit": "Fracture & OPD",
         "Amount": f"{inr(sched['fixed']['fracture_range'][0])}–"
                   f"{inr(sched['fixed']['fracture_range'][1])}"},
        {"Benefit": "Ambulance",
         "Amount": f"To {inr(sched['fixed']['ambulance_network_cap'])}"},
        {"Benefit": "Legal assistance", "Amount": "Panel lawyer"},
    ]), width="stretch", hide_index=True)

with t2:
    st.markdown(f"#### Ride Shield")
    st.markdown(f"<div style='color:{MUTED};font-size:.9rem'>The vehicle, the "
                "consignment and the tools of the trade.</div>",
                unsafe_allow_html=True)
    v, cg = sched["vehicle"], sched["consignment"]
    st.dataframe(pd.DataFrame([
        {"Benefit": "On-duty vehicle damage", "Amount": inr(v["value"])},
        {"Benefit": "— per event (40%)", "Amount": inr(v["per_event"])},
        {"Benefit": "— annual aggregate", "Amount": inr(v["annual_aggregate"])},
        {"Benefit": "Consignment, per event", "Amount": inr(cg["per_event"])},
        {"Benefit": "— annual aggregate", "Amount": inr(cg["annual_aggregate"])},
        {"Benefit": "Platform deduction protection", "Amount": "Actual deduction"},
        {"Benefit": "EV battery", "Amount": "To OEM/network"},
        {"Benefit": "Phone screen & theft", "Amount": "To repair network"},
    ]), width="stretch", hide_index=True)

note("<b>The vehicle benefit is written as a scheduled fixed benefit, not a "
     "motor own-damage policy.</b> Most riders use a privately-registered "
     "two-wheeler commercially, and every private policy in India excludes "
     "commercial use — so a motor OD policy covering it would be "
     "unenforceable. A first-party scheduled benefit sidesteps the exclusion, "
     "and separately kills the garage bill inflation that makes motor OD "
     "India's most fraud-prone line.")

st.divider()

# ------------------------------------------------------------------ basis
st.markdown("### Settlement basis, and the control on each benefit")
st.markdown(
    f"<div style='color:{MUTED};max-width:92ch'>The split is mostly dictated by "
    "what is being covered, not chosen freely. <b>Where we pay a fixed sum we "
    "verify the event objectively; where we pay actuals we never pay cash to "
    "the claimant, we pay the provider.</b> That single rule handles most "
    "Indian moral hazard.</div>", unsafe_allow_html=True)
st.write("")

bdf = pd.DataFrame(CFG["benefits"])
bdf.columns = ["Benefit", "Product", "Settlement basis", "Moral hazard control"]


def tag(v):
    if v.startswith("Fixed"):
        return "🟢 Fixed"
    if v.startswith("Indemnity"):
        return "🟠 Indemnity"
    return "🔵 Service"


bdf.insert(2, "Basis", bdf["Settlement basis"].map(tag))

f1, f2 = st.columns([1, 2.6])
with f1:
    counts = bdf["Basis"].value_counts()
    figp = go.Figure(go.Pie(labels=counts.index, values=counts.values, hole=0.58,
                            marker_colors=[OK, ACCENT, "#8FA1AE"],
                            textinfo="percent"))
    figp.update_layout(height=250, margin=dict(l=0, r=0, t=6, b=0),
                       legend=dict(orientation="h", y=-0.1))
    st.plotly_chart(figp, width="stretch")
    st.caption("Roughly 80% of premium sits in fixed benefits — which is what "
               "makes sub-60-second settlement possible.")

with f2:
    picked = st.multiselect("Filter", ["🟢 Fixed", "🟠 Indemnity", "🔵 Service"],
                            default=["🟢 Fixed", "🟠 Indemnity", "🔵 Service"])
    view = bdf[bdf["Basis"].isin(picked)] if picked else bdf
    st.dataframe(view[["Benefit", "Product", "Basis", "Moral hazard control"]],
                 width="stretch", hide_index=True, height=430)

note("<b>Why the platform offset is a contract clause, not a recovery right.</b> "
     "Subrogation and contribution apply only to contracts of indemnity — "
     "policies reimbursing a measured loss. Fixed-benefit policies pay a set "
     "sum on a defined event, and carry no contribution right between insurers. "
     "Platform group cover is predominantly fixed-benefit, so we cannot recover "
     "from the platform's insurer when we pay: a rider may legitimately claim "
     "in full under both. The one place an offset is justified is the income "
     "benefit, where stacking could take a rider above 100% of what they would "
     "have earned by riding — which is an over-insurance argument a regulator "
     "will accept.")
