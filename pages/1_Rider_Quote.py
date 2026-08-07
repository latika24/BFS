"""Rider Quote — price one rider under one set of conditions. Implements §5.1, §5.3."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from shared import page_setup, inr, section_ref, formula
from engine.config import CFG
from engine import pricing, safety_score as ss

page_setup("Rider Quote")

st.title("Rider Quote")
st.caption("Price one rider, one shift. §5.1 (Effective Exposure Unit) and "
           "§5.3 (the premium function)")

# ------------------------------------------------------------------ sidebar
sb = st.sidebar
sb.header("Rider")

age = sb.slider("Age", 18, 58, 27)
city = sb.selectbox("City", list(CFG["city"].keys()), index=1)
vehicle = sb.selectbox("Vehicle", list(CFG["vehicle"].keys()), index=1)
platform = sb.selectbox("Platform", list(CFG["platform"].keys()), index=0)
tenure = sb.slider("Tenure with us (months)", 0, 40, 0)
tier = sb.selectbox("Tier", list(CFG["tiers"].keys()), index=1)
si = CFG["tiers"][tier]["sum_insured_reference"]
sb.caption(f"Reference sum insured for {tier}: {inr(si)}")

sb.header("Shift conditions")
hours = sb.slider("Hours in the shift", 1.0, 14.0, 8.0, 0.5)
time_band = sb.selectbox("Time of day", list(CFG["time_of_day"].keys()), index=1)
weather = sb.selectbox("Weather", list(CFG["weather"].keys()), index=0)
fatigue = sb.selectbox("Continuous riding", list(CFG["fatigue"].keys()), index=0)
days = sb.slider("Days worked per month", 1, 30, 26)

sb.header("Riding behaviour")
preset = sb.radio("Telematics profile", ["safe", "average", "risky"], index=1,
                  horizontal=True)
tel = ss.default_inputs(preset)
with sb.expander("Adjust individual inputs"):
    for k in ss.SCALES:
        worst, best = ss.SCALES[k]
        hi = max(worst, best)
        tel[k] = st.slider(ss.LABELS[k], 0.0, float(hi), float(tel[k]), 0.1,
                           key=f"tel_{k}")

score_out = ss.compute(tel)

# ------------------------------------------------------------------ quote
rider = pricing.RiderProfile(age=age, city=city, vehicle=vehicle,
                             platform=platform, tenure_months=tenure,
                             safety_score=score_out["score"], sum_insured=si,
                             tier=tier)
shift = pricing.ShiftContext(hours=hours, time_band=time_band, weather=weather,
                             continuous_hours=fatigue, days_per_month=days)
q = pricing.quote(rider, shift)

# ------------------------------------------------------------------ headline
c1, c2, c3, c4 = st.columns(4)
c1.metric("Per active hour", f"₹{q['premium_per_hour']:.2f}")
c2.metric("This shift", f"₹{q['premium_shift']:.2f}", f"{hours:.1f} hours")
c3.metric("Per month", inr(q["premium_month"]), f"{days} days")
c4.metric("Per year", inr(q["premium_year"]))

daily = q["premium_shift"]
if daily <= 30:
    st.success(f"**₹{daily:.0f} a day** — the affordability test in §3.1 is "
               "'less than one cup of chai a day'. This quote passes it.")
else:
    st.warning(f"**₹{daily:.0f} a day.** Above the ₹15–30 daily debit band the "
               "plan targets in §3.1. High exposure or a poor safety score is "
               "pushing this rider out of the affordable range.")

st.divider()

# ------------------------------------------------------------------ exposure
left, right = st.columns([1, 1])

with left:
    st.subheader("Step 1 — Effective Exposure Unit")
    section_ref("§5.1")
    formula("EEU = (active_minutes / 60) × M_time × M_weather × M_geo")

    exp = q["exposure"]
    st.dataframe(pd.DataFrame([
        {"Component": "Raw hours ridden", "Value": f"{exp['raw_hours']:.1f}"},
        {"Component": f"Time of day — {time_band}", "Value": f"× {exp['m_time']:.2f}"},
        {"Component": f"Weather — {weather}", "Value": f"× {exp['m_weather']:.2f}"},
        {"Component": f"City — {city}", "Value": f"× {exp['m_geo']:.2f}"},
        {"Component": "Effective Exposure Units", "Value": f"{exp['eeu']:.2f} EEU"},
    ]), width="stretch", hide_index=True)

    ratio = exp["eeu"] / exp["raw_hours"] if exp["raw_hours"] else 0
    st.markdown(
        f"This rider's hour is worth **{ratio:.2f} EEU**. One EEU is one hour of "
        "ordinary daytime riding in fair weather on a tier-1 city road — so "
        f"{'these conditions are riskier than the reference' if ratio > 1.05 else 'these conditions are at or below the reference' }."
    )

with right:
    st.subheader("Step 2 — Rider Safety Score")
    section_ref("§5.2, Layer B")
    st.metric("Score", f"{score_out['score']:.0f} / 100",
              f"band {score_out['band']} → × {score_out['multiplier']:.2f}")

    contrib = pd.DataFrame([
        {"Input": c["label"], "Value": c["raw"],
         "Points lost": round(c["points_lost"], 1)}
        for c in score_out["contributions"].values()
    ]).sort_values("Points lost", ascending=False)

    fig = go.Figure(go.Bar(x=contrib["Points lost"], y=contrib["Input"],
                           orientation="h", marker_color="#c0392b"))
    fig.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0),
                      xaxis_title="Score points lost", yaxis_title=None,
                      yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, width="stretch")
    st.caption(f"Biggest improvement opportunity: **{score_out['biggest_opportunity']}**. "
               "This is what the worker sees in the app, and what the plan means "
               "by pricing behaviour and changing it at the same time.")

st.divider()

# ------------------------------------------------------------------ waterfall
st.subheader("Step 3 — Building the premium")
section_ref("§5.3")
formula("P_day = BaseRate × (SI / 100,000) × EEU_day × M_behaviour × M_age × "
        "M_vehicle × M_platform × M_fatigue × (1 − D_loyalty) × "
        "(1 + Load_expense) × (1 + Load_margin)")

steps = pricing.waterfall(q)
wf = go.Figure(go.Waterfall(
    orientation="v",
    measure=["absolute"] + ["relative"] * (len(steps) - 1),
    x=[s["label"] for s in steps],
    y=[steps[0]["value"]] + [steps[i]["value"] - steps[i - 1]["value"]
                             for i in range(1, len(steps))],
    connector={"line": {"color": "#bbb"}},
    increasing={"marker": {"color": "#c0392b"}},
    decreasing={"marker": {"color": "#27ae60"}},
    totals={"marker": {"color": "#34495e"}},
))
wf.update_layout(height=420, margin=dict(l=0, r=0, t=20, b=0),
                 yaxis_title="Premium for this shift (₹)", xaxis_tickangle=-35)
st.plotly_chart(wf, width="stretch")

m1, m2, m3 = st.columns(3)
m1.metric("Rating multiplier product", f"× {q['raw_multiplier_product']:.2f}")
m2.metric("After governance cap", f"× {q['capped_multiplier_product']:.2f}",
          "capped" if q["was_capped"] else "within band")
m3.metric("Loyalty discount", f"−{q['loyalty_discount']:.0%}",
          f"{tenure} months tenure")

if q["was_capped"]:
    st.error(
        f"**Governance cap has bound.** The raw multiplier of "
        f"{q['raw_multiplier_product']:.2f}× exceeds the "
        f"{CFG['multiplier_cap']['ceiling']}× ceiling set in §5.3. Beyond that "
        "band the price becomes unaffordable exactly for the workers who need "
        "cover most, and the regulator will not accept it. Above the cap the "
        "plan declines the risk or mandates a safety intervention rather than "
        "pricing the worker out."
    )

with st.expander("The multipliers applied"):
    st.dataframe(pd.DataFrame([
        {"Factor": k.replace("M_", "").title(), "Level": v["band"],
         "Multiplier": f"× {v['value']:.2f}"}
        for k, v in q["multipliers"].items()
    ]), width="stretch", hide_index=True)

st.divider()

# ------------------------------------------------------------------ comparison
st.subheader("Why this beats a flat annual premium")
section_ref("§3.2")

scenarios = [
    ("Occasional rider — 40 hrs/month", 40),
    ("Part-time rider — 120 hrs/month", 120),
    ("Full-time rider — 208 hrs/month", 208),
    ("Heavy rider — 260 hrs/month", 260),
]
flat_annual = CFG["portfolio"]["gwp_per_worker"]
rows = []
for label, monthly_hours in scenarios:
    sh = pricing.ShiftContext(hours=hours, time_band=time_band, weather=weather,
                              continuous_hours=fatigue, days_per_month=days)
    qq = pricing.quote(rider, sh)
    annual = qq["premium_per_hour"] * monthly_hours * 12
    rows.append({
        "Rider": label,
        "Usage-based annual premium": inr(annual),
        "Flat annual premium": inr(flat_annual),
        "Difference": inr(annual - flat_annual),
        "Verdict": ("Overcharged by a flat premium" if annual < flat_annual
                    else "Undercharged by a flat premium"),
    })
st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
st.caption(
    "A single flat premium is wrong for both ends of this population at once. "
    "Price it for the heavy rider and the occasional rider will not buy; price "
    "it for the occasional rider and the book loses money on the heavy one. "
    "That is the adverse selection problem exposure-based pricing dissolves "
    "rather than manages."
)
