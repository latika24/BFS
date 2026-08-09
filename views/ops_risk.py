"""Insurer console — risk and exposure."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from shared import (topbar, h, kpi, inr, crore, MUTED, PRIMARY, ACCENT, OK,
                    BAD, riders, trips, book_claims, note)
from engine.config import CFG

topbar("Insurer console", "Risk & exposure")

R = riders()
T = trips()
C = book_claims()

h("Risk & exposure",
  "In a conventional book exposure is spread across time and geography. In a "
  "usage-based book it concentrates exactly where risk is highest, which is "
  "both the pricing opportunity and the accumulation problem.")

# ------------------------------------------------------------------ live
st.markdown("**Riders on the road right now, by hour**")
hours = list(range(24))
shape = np.array([0.4, 0.2, 0.1, 0.1, 0.1, 0.3, 0.8, 1.4, 1.8, 2.0, 2.4, 3.6,
                  4.2, 3.4, 2.6, 2.4, 3.0, 4.0, 4.8, 5.2, 4.6, 3.4, 2.0, 0.9])
on_road = (shape / shape.sum() * len(R) * 0.62).round()
peak = int(on_road.max())

k = st.columns(4)
kpi(k[0], "Peak concurrent riders", f"{peak:,}", "20:00–21:00")
kpi(k[1], "Peak-hour exposure", f"{peak * 1.9 / 1000:.1f}k EEU",
    "at wet-weather multipliers")
kpi(k[2], "Single-event exposure", crore(peak * 12000),
    "if a metro flood hits at peak")
kpi(k[3], "Cat cover attachment", crore(50), "excess-of-loss, from day one")

fig = go.Figure()
fig.add_trace(go.Bar(x=hours, y=on_road, marker_color=[
    ACCENT if CFG["time_of_day"]["19:00-23:00"] > 1.2 and 19 <= hh <= 22
    else (BAD if hh >= 23 or hh < 5 else PRIMARY) for hh in hours]))
fig.update_layout(height=250, margin=dict(l=0, r=0, t=10, b=0),
                  xaxis_title="Hour of day", yaxis_title="Riders with cover live",
                  xaxis=dict(dtick=2))
st.plotly_chart(fig, use_container_width=True)

note("<b>This chart is the accumulation risk.</b> At 8pm on a wet Friday, tens "
     "of thousands of riders are on the road simultaneously, all with cover "
     "live, all being charged our highest multipliers. One severe urban flood, "
     "a heatwave day or a large-scale disturbance produces a claims spike that "
     "an independent-frequency model would never predict. Catastrophe "
     "excess-of-loss cover is bought from day one, and correlated-event "
     "scenarios are modelled explicitly.")

st.divider()

# ------------------------------------------------------------------ heatmap
h1_, h2_ = st.columns([1.35, 1])

with h1_:
    st.markdown("**Where the risk sits — mean exposure per block**")
    pivot = T.pivot_table(index="weather", columns="time_band", values="eeu",
                          aggfunc="mean")
    order = list(CFG["time_of_day"].keys())
    pivot = pivot.reindex(columns=[b for b in order if b in pivot.columns])
    figh = px.imshow(pivot, text_auto=".3f", aspect="auto",
                     color_continuous_scale="OrRd",
                     labels=dict(x="Time band", y="Weather",
                                 color="Mean EEU per block"))
    figh.update_layout(height=330, margin=dict(l=0, r=0, t=14, b=0))
    st.plotly_chart(figh, use_container_width=True)

with h2_:
    st.markdown("**Exposure concentration**")
    top_right = T[(T["time_band"].isin(["19:00-23:00", "23:00-05:00"])) &
                  (T["weather"].isin(["Heavy rain", "Fog / low visibility"]))]
    st.metric("Blocks in the top-right cells",
              f"{len(top_right)/len(T):.1%} of all blocks")
    st.metric("Share of total EEU they carry",
              f"{top_right['eeu'].sum()/T['eeu'].sum():.1%}")
    st.caption("A small share of blocks carries a disproportionate share of "
               "exposure. That concentration is what we price for — and what "
               "the reinsurance programme protects against.")

    st.write("")
    st.markdown("**Reinsurance programme**")
    st.dataframe(pd.DataFrame([
        {"Layer": "Quota share 30%", "Purpose": "Risk transfer + solvency relief"},
        {"Layer": "Cat excess-of-loss", "Purpose": "Correlated-event protection"},
        {"Layer": "GIC Re obligatory 4%", "Purpose": "Statutory cession"},
    ]), width="stretch", hide_index=True)

st.divider()

# ------------------------------------------------------------------ loss
h("Loss experience by cohort")

C2 = C.merge(R[["rider_id", "safety_band", "segment", "city", "hours_per_month"]],
             on="rider_id", how="left")
by_band = C2.groupby("safety_band").agg(
    claims=("count", "sum"), amount=("amount", "sum")).reset_index()
riders_by_band = R.groupby("safety_band")["rider_id"].count()
by_band["riders"] = by_band["safety_band"].map(riders_by_band)
by_band["freq"] = by_band["claims"] / by_band["riders"] * 1000
by_band["cost_per_rider"] = by_band["amount"] / by_band["riders"]

order = ["90-100", "70-89", "50-69", "Below 50"]
by_band["_o"] = by_band["safety_band"].map({b: i for i, b in enumerate(order)})
by_band = by_band.sort_values("_o")

l1, l2 = st.columns([1.3, 1])
with l1:
    figl = go.Figure()
    figl.add_trace(go.Bar(x=by_band["safety_band"], y=by_band["freq"],
                          name="Claims per 1,000 riders", marker_color=PRIMARY))
    figl.add_trace(go.Scatter(x=by_band["safety_band"],
                              y=by_band["cost_per_rider"],
                              name="Claim cost per rider (₹)", yaxis="y2",
                              line=dict(color=ACCENT, width=3)))
    figl.update_layout(height=300, margin=dict(l=0, r=0, t=26, b=0),
                       yaxis=dict(title="Frequency / 1,000"),
                       yaxis2=dict(title="₹ per rider", overlaying="y",
                                   side="right", showgrid=False),
                       legend=dict(orientation="h", y=1.18),
                       xaxis_title="Safety score band")
    st.plotly_chart(figl, use_container_width=True)
    st.caption("The safety score separates loss experience cleanly — which is "
               "what justifies it as a rating factor to a regulator, and what "
               "makes showing it to riders worth doing.")

with l2:
    show = by_band[["safety_band", "riders", "freq", "cost_per_rider"]].copy()
    show["freq"] = show["freq"].map(lambda v: f"{v:.0f}")
    show["cost_per_rider"] = show["cost_per_rider"].map(inr)
    show.columns = ["Band", "Riders", "Claims/1,000", "Cost/rider"]
    st.dataframe(show, width="stretch", hide_index=True)

    seg = C2.groupby("segment").agg(amount=("amount", "sum")).reset_index()
    seg_r = R.groupby("segment")["rider_id"].count()
    seg["riders"] = seg["segment"].map(seg_r)
    seg["per_rider"] = (seg["amount"] / seg["riders"]).map(inr)
    st.dataframe(seg[["segment", "riders", "per_rider"]].rename(
        columns={"segment": "Segment", "riders": "Riders",
                 "per_rider": "Claim cost/rider"}),
        width="stretch", hide_index=True)

st.divider()

# ------------------------------------------------------------------ anti-sel
h("What a flat premium would do to this book",
  "The case for exposure pricing, tested against the in-force portfolio.")

flat = st.slider("If we charged one flat annual premium instead (₹)",
                 2000, 9000, CFG["portfolio"]["gwp_per_worker"], 100)

bc = 3148.0
R2 = R.copy()
R2["expected_cost"] = bc * (R2["hours_per_month"] / 208.0)
R2["margin"] = flat - R2["expected_cost"]

a1, a2, a3 = st.columns(3)
loss_makers = int((R2["margin"] < 0).sum())
overcharged = int((R2["expected_cost"] < flat * 0.4).sum())
kpi(a1, "Policies written at a loss", f"{loss_makers:,}",
    f"{loss_makers/len(R2):.0%} of the book")
kpi(a2, "Policies overcharged 2.5×+", f"{overcharged:,}",
    f"{overcharged/len(R2):.0%} — these riders would not buy")
kpi(a3, "Aggregate margin", crore(R2["margin"].sum()),
    "before expenses of any kind")

figa = px.scatter(R2.sample(1800, random_state=5), x="hours_per_month",
                  y="expected_cost", color="margin",
                  color_continuous_scale="RdYlGn",
                  labels={"hours_per_month": "Active hours per month",
                          "expected_cost": "Expected claim cost (₹/yr)",
                          "margin": "Margin under a flat premium"})
figa.add_hline(y=flat, line_dash="dash", line_color="#2d3436",
               annotation_text=f"flat premium ₹{flat:,}")
figa.update_layout(height=380, margin=dict(l=0, r=0, t=16, b=0))
st.plotly_chart(figa, use_container_width=True)
