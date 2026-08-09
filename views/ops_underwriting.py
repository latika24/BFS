"""Insurer console — underwriting: rating control and quoting."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from shared import (topbar, h, kpi, inr, lakh, rows, badge, MUTED, PRIMARY,
                    ACCENT, OK, BAD, riders, note, formula)
from engine import pricing, safety_score as ss
from engine.config import CFG

topbar("Insurer console", "Underwriting · rating basis v2.0")

h("Underwriting",
  "The live rating basis. Every quote in the book is produced by this engine, "
  "and every factor below is filed and auditable.")

tab_quote, tab_basis, tab_monitor = st.tabs(
    ["Quote a rider", "Rating basis", "Portfolio pricing monitor"])

# ------------------------------------------------------------------ quote
with tab_quote:
    st.markdown("**Underwriter quote tool**")
    c = st.columns(4)
    age = c[0].slider("Age", 18, 58, 27)
    city = c[1].selectbox("City", list(CFG["city"].keys()), index=1)
    vehicle = c[2].selectbox("Vehicle", list(CFG["vehicle"].keys()), index=1)
    plat = c[3].selectbox("Platform", list(CFG["platform"].keys()), index=0)

    c2 = st.columns(4)
    tier = c2[0].selectbox("Plan", list(CFG["tiers"].keys()), index=1)
    band = c2[1].selectbox("Time band", list(CFG["time_of_day"].keys()), index=1)
    wx = c2[2].selectbox("Weather", list(CFG["weather"].keys()), index=0)
    prof = c2[3].select_slider("Telematics profile",
                               ["safe", "average", "risky"], value="average")

    c3 = st.columns(3)
    hours = c3[0].slider("Shift length", 1.0, 14.0, 8.0, 0.5)
    days = c3[1].slider("Days per month", 1, 30, 26)
    tenure = c3[2].slider("Tenure (months)", 0, 40, 0)

    sc = ss.compute(ss.default_inputs(prof))
    si = CFG["tiers"][tier]["sum_insured_reference"]
    rp = pricing.RiderProfile(age=age, city=city, vehicle=vehicle,
                              platform=plat, tenure_months=tenure,
                              safety_score=sc["score"], sum_insured=si, tier=tier)
    sh = pricing.ShiftContext(hours=hours, time_band=band, weather=wx,
                              days_per_month=days)
    q = pricing.quote(rp, sh)
    b = q["band"]

    st.write("")
    k = st.columns(5)
    kpi(k[0], "Rate", f"₹{q['premium_per_hour']:.2f}/hr",
        f"band ₹{b['floor_per_hour']:.2f}–{b['ceiling_per_hour']:.2f}")
    kpi(k[1], "Annual premium", inr(q["premium_year"]),
        f"{hours*days*12:.0f} hrs")
    kpi(k[2], "Total multiplier", f"×{q['raw_multiplier_product']:.2f}",
        "capped ×%.2f" % q["capped_total_multiplier"] if q["was_capped"] else "within band")
    kpi(k[3], "Sum insured", lakh(si))
    kpi(k[4], "Safety score", f"{sc['score']:.0f}", sc["band"])

    st.write("")
    qc1, qc2 = st.columns([1.4, 1])
    with qc1:
        steps = pricing.waterfall(q)
        wf = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute"] + ["relative"] * (len(steps) - 1),
            x=[s["label"] for s in steps],
            y=[steps[0]["value"]] + [steps[i]["value"] - steps[i-1]["value"]
                                     for i in range(1, len(steps))],
            connector={"line": {"color": "#CCD5D4"}},
            increasing={"marker": {"color": ACCENT}},
            decreasing={"marker": {"color": OK}},
            totals={"marker": {"color": PRIMARY}}))
        wf.update_layout(height=380, margin=dict(l=0, r=0, t=20, b=0),
                         yaxis_title="Premium for the shift (₹)",
                         xaxis_tickangle=-35)
        st.plotly_chart(wf, use_container_width=True)
    with qc2:
        st.dataframe(pd.DataFrame(
            [{"Factor": "Time of day", "Level": band,
              "×": f"{q['exposure']['m_time']:.2f}"},
             {"Factor": "Weather", "Level": wx,
              "×": f"{q['exposure']['m_weather']:.2f}"},
             {"Factor": "City", "Level": city.split(" (")[0],
              "×": f"{q['exposure']['m_geo']:.2f}"}]
            + [{"Factor": kk.replace("M_", "").title(), "Level": vv["band"],
                "×": f"{vv['value']:.2f}"} for kk, vv in q["multipliers"].items()]),
            width="stretch", hide_index=True)

        if q["was_capped"]:
            st.error(f"Governance band binding. Raw ×{q['raw_multiplier_product']:.2f} "
                     f"→ charged ×{q['capped_total_multiplier']:.2f}. "
                     "Refer for a safety intervention rather than repricing.")
        else:
            st.success("Inside the governance band. Auto-accept.")

        if st.button("Bind this risk", type="primary", width="stretch"):
            st.success("Bound. In production this writes the policy, registers "
                       "the UPI mandate and starts the exposure meter.")

# ------------------------------------------------------------------ basis
with tab_basis:
    formula("Premium = BaseRate × (SI / 100,000) × hours × [ M_time × M_weather "
            "× M_geo × M_behaviour × M_age × M_vehicle × M_platform × M_fatigue "
            "]<sub>capped 0.6–2.2</sub> × (1 − D_loyalty) × (1 + Load_expense) "
            "× (1 + Load_margin)")

    bc1, bc2, bc3 = st.columns(3)
    with bc1:
        st.markdown("**Exposure — Layer A**")
        st.dataframe(pd.DataFrame(
            [{"Band": k, "×": v} for k, v in CFG["time_of_day"].items()]),
            width="stretch", hide_index=True)
        st.dataframe(pd.DataFrame(
            [{"Weather": k, "×": v} for k, v in CFG["weather"].items()]),
            width="stretch", hide_index=True)
    with bc2:
        st.markdown("**Behaviour — Layer B**")
        st.dataframe(pd.DataFrame(
            [{"Input": ss.LABELS[k], "Weight": f"{v:.0%}"}
             for k, v in CFG["safety_score_weights"].items()]),
            width="stretch", hide_index=True)
        st.dataframe(pd.DataFrame(
            [{"Score band": k, "×": v}
             for k, v in CFG["safety_score_bands"].items()]),
            width="stretch", hide_index=True)
    with bc3:
        st.markdown("**Static — Layer C**")
        for label, key in [("Age", "age"), ("Vehicle", "vehicle"),
                           ("Platform", "platform"), ("City", "city")]:
            st.dataframe(pd.DataFrame(
                [{label: k.split(" (")[0], "×": v} for k, v in CFG[key].items()]),
                width="stretch", hide_index=True)

    note("<b>Factors we will never use:</b> gender, religion, caste, home state, "
         "or any geographic variable fine enough to proxy for these. Indian "
         "motor insurance does not gender-rate and we will not start. The "
         "rating basis is audited annually for proxy discrimination.")

# ------------------------------------------------------------------ monitor
with tab_monitor:
    R = riders()
    rng = np.random.default_rng(3)
    bands = list(CFG["time_of_day"].keys())
    wxs = list(CFG["weather"].keys())

    rates = []
    for _, row in R.sample(1200, random_state=2).iterrows():
        tb = rng.choice(bands, p=[.15, .20, .28, .27, .10])
        w = rng.choice(wxs, p=[.68, .14, .06, .04, .08])
        rp = pricing.RiderProfile(age=int(row["age"]), city=row["city"],
                                  vehicle=row["vehicle"], platform=row["platform"],
                                  tenure_months=int(row["tenure_months"]),
                                  safety_score=float(row["safety_score"]),
                                  sum_insured=1000000)
        sh = pricing.ShiftContext(hours=8.0, time_band=tb, weather=w)
        qq = pricing.quote(rp, sh)
        rates.append({"rate": qq["premium_per_hour"],
                      "capped": qq["was_capped"],
                      "raw": qq["raw_multiplier_product"],
                      "band": row["safety_band"], "city": row["city"]})
    RD = pd.DataFrame(rates)
    bb = pricing.price_band(pricing.RiderProfile(sum_insured=1000000))

    k = st.columns(4)
    kpi(k[0], "Median rate charged", f"₹{RD['rate'].median():.2f}/hr")
    kpi(k[1], "At the ceiling", f"{(RD['rate'] >= bb['ceiling_per_hour']-.01).mean():.1%}",
        "capped — cross-subsidised")
    kpi(k[2], "At the floor", f"{(RD['rate'] <= bb['floor_per_hour']+.01).mean():.1%}",
        "minimum contribution")
    kpi(k[3], "Would exceed band uncapped", f"{(RD['raw'] > 2.2).mean():.1%}",
        "the cap is doing real work")

    st.write("")
    mc1, mc2 = st.columns([1.35, 1])
    with mc1:
        fig = go.Figure(go.Histogram(x=RD["rate"], nbinsx=48,
                                     marker_color=PRIMARY))
        fig.add_vline(x=bb["floor_per_hour"], line_dash="dash", line_color=OK,
                      annotation_text=f"floor ₹{bb['floor_per_hour']:.2f}")
        fig.add_vline(x=bb["base_per_hour"], line_dash="dot", line_color=MUTED,
                      annotation_text=f"base ₹{bb['base_per_hour']:.2f}")
        fig.add_vline(x=bb["ceiling_per_hour"], line_dash="dash", line_color=BAD,
                      annotation_text=f"ceiling ₹{bb['ceiling_per_hour']:.2f}")
        fig.update_layout(height=330, margin=dict(l=0, r=0, t=30, b=0),
                          xaxis_title="Rate actually charged (₹/hour)",
                          yaxis_title="Quotes")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Every quote in the book sits inside the filed band. The "
                   "spike at the ceiling is riders whose raw risk exceeds "
                   "×2.2 — we absorb the difference rather than price them out.")
    with mc2:
        agg = RD.groupby("band")["rate"].agg(["count", "mean"]).reset_index()
        order = ["90-100", "70-89", "50-69", "Below 50"]
        agg["_o"] = agg["band"].map({b: i for i, b in enumerate(order)})
        agg = agg.sort_values("_o").drop(columns="_o")
        agg["mean"] = agg["mean"].map(lambda v: f"₹{v:.2f}")
        agg["share"] = (agg["count"] / agg["count"].sum()).map(lambda v: f"{v:.0%}")
        agg.columns = ["Safety band", "Quotes", "Mean rate", "Share"]
        st.dataframe(agg, width="stretch", hide_index=True)

        note("Riders in the worst safety band pay about 50% more per hour and "
             "generate materially more claims. The score is not a loyalty "
             "gimmick — it is the single largest controllable driver of loss "
             "ratio in the book.")
