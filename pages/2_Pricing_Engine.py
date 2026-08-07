"""Pricing Engine — price one rider, one hour. §1.2, §3.3."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from shared import (page_setup, page_header, kpi, inr, formula, note,
                    SEC, MUTED, PRIMARY, ACCENT, OK, BAD, LINE)
from engine.config import CFG
from engine import pricing, safety_score as ss

page_setup("Pricing Engine")

page_header(
    "Pricing Engine",
    f"{SEC['what_we_sell']} · {SEC['marketing_mix']}",
    "Premium follows exposure rather than the calendar. Each fifteen-minute "
    "block of riding becomes an Effective Exposure Unit — minutes ridden, "
    "weighted for time of day, weather, traffic and location — multiplied by a "
    "behaviour score from the phone's accelerometer.")

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
sb.caption(f"{tier}: base ₹{CFG['tiers'][tier]['price_per_hour']:.2f}/hr · "
           f"SI {inr(si)}")

sb.header("This shift")
hours = sb.slider("Hours", 1.0, 14.0, 8.0, 0.5)
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
        hi = max(ss.SCALES[k])
        tel[k] = st.slider(ss.LABELS[k], 0.0, float(hi), float(tel[k]), 0.1,
                           key=f"tel_{k}")

score = ss.compute(tel)
rider = pricing.RiderProfile(age=age, city=city, vehicle=vehicle,
                             platform=platform, tenure_months=tenure,
                             safety_score=score["score"], sum_insured=si, tier=tier)
shift = pricing.ShiftContext(hours=hours, time_band=time_band, weather=weather,
                             continuous_hours=fatigue, days_per_month=days)
q = pricing.quote(rider, shift)
band = q["band"]

# ------------------------------------------------------------------ headline
k1, k2, k3, k4 = st.columns(4)
kpi(k1, "Per active hour", f"₹{q['premium_per_hour']:.2f}",
    f"base ₹{band['base_per_hour']:.2f}")
kpi(k2, "This shift", f"₹{q['premium_shift']:.0f}", f"{hours:.1f} hours")
kpi(k3, "Per month", inr(q["premium_month"]), f"{days} days")
kpi(k4, "Per year", inr(q["premium_year"]), "if worked at this rate")

daily = q["premium_shift"]
if daily <= 30:
    st.success(f"**₹{daily:.0f} a day.** Inside the ₹15–30 daily debit band the "
               "plan targets. ₹5,400 asked for once is unpayable on ₹22,000 a "
               "month; the same sum at ₹20 a day is not.")
else:
    st.warning(f"**₹{daily:.0f} a day** — above the ₹15–30 band. Long hours or "
               "high-risk conditions are pushing this rider toward the edge of "
               "affordability, even with the governance cap applied.")

st.write("")
st.divider()

# ------------------------------------------------------------------ the band
st.markdown("### The governance band")
st.markdown(f"<div class='ref'>{SEC['marketing_mix']}</div>", unsafe_allow_html=True)
st.markdown(
    f"<div style='color:{MUTED};max-width:90ch'>Nobody pays the base rate. What "
    "a worker pays is the base multiplied by the risk of that particular hour — "
    "time of day, weather, traffic, city and behaviour score — but the total is "
    f"held inside a band of ×{band['cap_floor']} to ×{band['cap_ceiling']}. "
    "Beyond the band the plan declines the risk or mandates a safety "
    "intervention rather than pricing out the workers who most need cover.</div>",
    unsafe_allow_html=True)
st.write("")

gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=q["premium_per_hour"],
    number={"prefix": "₹", "suffix": " /hr", "font": {"size": 40}},
    gauge={
        "axis": {"range": [0, band["ceiling_per_hour"] * 1.12],
                 "tickprefix": "₹"},
        "bar": {"color": PRIMARY, "thickness": 0.7},
        "steps": [
            {"range": [0, band["floor_per_hour"]], "color": "#EDF2F1"},
            {"range": [band["floor_per_hour"], band["base_per_hour"]],
             "color": "#DCEBE8"},
            {"range": [band["base_per_hour"], band["ceiling_per_hour"]],
             "color": "#FBE7DC"},
            {"range": [band["ceiling_per_hour"], band["ceiling_per_hour"] * 1.12],
             "color": "#F3D7D1"},
        ],
        "threshold": {"line": {"color": BAD, "width": 3}, "thickness": 0.85,
                      "value": band["ceiling_per_hour"]},
    }))
gauge.update_layout(height=280, margin=dict(l=30, r=30, t=20, b=10))

bg1, bg2 = st.columns([1, 1])
with bg1:
    st.plotly_chart(gauge, width="stretch")
with bg2:
    st.write("")
    b1, b2, b3 = st.columns(3)
    kpi(b1, "Floor", f"₹{band['floor_per_hour']:.2f}",
        f"×{band['cap_floor']} — safest hour")
    kpi(b2, "Base", f"₹{band['base_per_hour']:.2f}", "×1.00 — reference hour")
    kpi(b3, "Ceiling", f"₹{band['ceiling_per_hour']:.2f}",
        f"×{band['cap_ceiling']} — worst hour")
    st.write("")
    if q["was_capped"] and q["capped_total_multiplier"] >= band["cap_ceiling"]:
        st.error(
            f"**Cap has bound at the ceiling.** Raw conditions give "
            f"×{q['raw_multiplier_product']:.2f} — this rider would otherwise "
            f"pay ₹{band['base_per_hour'] * q['raw_multiplier_product']:.2f} an "
            f"hour. The band holds it at ₹{q['premium_per_hour']:.2f}. The "
            "difference is a deliberate cross-subsidy: unaffordable pricing for "
            "the highest-risk workers is both commercially self-defeating and "
            "something the regulator would not accept.")
    elif q["was_capped"]:
        st.info(f"**Cap has bound at the floor.** Conditions give "
                f"×{q['raw_multiplier_product']:.2f}, below the ×{band['cap_floor']} "
                "minimum. The floor exists so that a very low-exposure rider "
                "still contributes to the fixed cost base.")
    else:
        st.success(f"Total multiplier ×{q['raw_multiplier_product']:.2f} — "
                   "inside the band, no intervention needed.")

st.divider()

# ------------------------------------------------------------------ derivation
st.markdown("### How this price was built")
formula("Premium = BaseRate × (SI / 100,000) × hours × [ M_time × M_weather × "
        "M_geo × M_behaviour × M_age × M_vehicle × M_platform × M_fatigue ]"
        "<sub>capped 0.6–2.2</sub> × (1 − D_loyalty) × (1 + Load_expense) × "
        "(1 + Load_margin)")

w1, w2 = st.columns([1.45, 1])
with w1:
    steps_data = pricing.waterfall(q)
    wf = go.Figure(go.Waterfall(
        orientation="v",
        measure=["absolute"] + ["relative"] * (len(steps_data) - 1),
        x=[s["label"] for s in steps_data],
        y=[steps_data[0]["value"]] + [steps_data[i]["value"] - steps_data[i-1]["value"]
                                      for i in range(1, len(steps_data))],
        connector={"line": {"color": "#CCD5D4"}},
        increasing={"marker": {"color": ACCENT}},
        decreasing={"marker": {"color": OK}},
        totals={"marker": {"color": PRIMARY}}))
    wf.update_layout(height=420, margin=dict(l=0, r=0, t=20, b=0),
                     yaxis_title="Premium for this shift (₹)",
                     xaxis_tickangle=-35)
    st.plotly_chart(wf, width="stretch")

with w2:
    exp = q["exposure"]
    st.markdown("**Exposure factors**")
    st.dataframe(pd.DataFrame([
        {"Factor": f"Time of day — {time_band}", "×": f"{exp['m_time']:.2f}"},
        {"Factor": f"Weather — {weather}", "×": f"{exp['m_weather']:.2f}"},
        {"Factor": f"City — {city.split(' (')[0]}", "×": f"{exp['m_geo']:.2f}"},
        {"Factor": "Exposure subtotal", "×": f"{q['exposure_product']:.2f}"},
    ]), width="stretch", hide_index=True)

    st.markdown("**Rating factors**")
    st.dataframe(pd.DataFrame(
        [{"Factor": k.replace("M_", "").title(), "Level": v["band"],
          "×": f"{v['value']:.2f}"} for k, v in q["multipliers"].items()]
        + [{"Factor": "Rating subtotal", "Level": "",
            "×": f"{q['rating_product']:.2f}"}]
    ), width="stretch", hide_index=True)

    st.metric("Total, before the cap", f"×{q['raw_multiplier_product']:.2f}")
    st.metric("After the governance band", f"×{q['capped_total_multiplier']:.2f}")

st.caption(f"One EEU is an hour of ordinary daytime riding in fair weather on a "
           f"tier-1 road. This shift is **{q['eeu_for_pricing']:.2f} EEU** across "
           f"{hours:.1f} clock hours — an hour at 10pm in heavy Bengaluru rain "
           "is about 2.2 units.")

st.divider()

# ------------------------------------------------------------------ vs flat
st.markdown("### Why this beats a flat annual premium")
st.markdown(f"<div class='ref'>{SEC['marketing_mix']}</div>", unsafe_allow_html=True)

flat_annual = CFG["portfolio"]["gwp_per_worker"]
scenarios = [("Occasional — 40 hrs/month", 40), ("Part-time — 120 hrs/month", 120),
             ("Full-time — 208 hrs/month", 208), ("Heavy — 260 hrs/month", 260)]
rows, usage_vals, flat_vals, labels = [], [], [], []
for label, mh in scenarios:
    annual = q["premium_per_hour"] * mh * 12
    labels.append(label)
    usage_vals.append(annual)
    flat_vals.append(flat_annual)
    rows.append({
        "Rider": label,
        "Usage-based": inr(annual),
        "Flat premium": inr(flat_annual),
        "Difference": inr(annual - flat_annual),
        "Under a flat premium": ("Overcharged — would not buy"
                                 if annual < flat_annual
                                 else "Undercharged — book loses money"),
    })

cmp1, cmp2 = st.columns([1.2, 1])
with cmp1:
    figc = go.Figure()
    figc.add_trace(go.Bar(x=labels, y=usage_vals, name="Usage-based",
                          marker_color=PRIMARY))
    figc.add_trace(go.Bar(x=labels, y=flat_vals, name="Flat annual premium",
                          marker_color="#C9D6D4"))
    figc.update_layout(height=340, margin=dict(l=0, r=0, t=24, b=0),
                       barmode="group", yaxis_title="Annual premium (₹)",
                       legend=dict(orientation="h", y=1.15), xaxis_tickangle=-15)
    st.plotly_chart(figc, width="stretch")
with cmp2:
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

note("A single flat premium is wrong for both ends of this population at once. "
     "Price it for the heavy rider and the occasional rider will not buy; price "
     "it for the occasional rider and the book loses money on the heavy one. "
     "That is textbook adverse selection, and a flat-premium insurer entering "
     "this market gets the worst half of it. Exposure pricing dissolves the "
     "problem rather than managing it.")
