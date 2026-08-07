"""Portfolio Simulator — the book from year 1 to 7. Implements §6.2, §6.4, §6.6, §6.7."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from shared import page_setup, inr, crore, section_ref
from engine.config import CFG
from engine import portfolio

page_setup("Portfolio Simulator")

st.title("Portfolio Simulator")
st.caption("The book from year 1 to year 7. §6.2, §6.4, §6.6 and §6.7. "
           "Year 1 is the first full year of writing — project month 21 onward.")

# ------------------------------------------------------------------ sidebar
sb = st.sidebar
sb.header("Scenario")

scenario = sb.radio(
    "Preset",
    ["Base plan", "Loss ratio plateaus at 78%", "Growth stalls at 7 lakh", "Custom"],
    index=0,
)

plan_lr = [y["loss_ratio"] for y in CFG["portfolio"]["trajectory"]]
growth = 1.0
lr_override = None

if scenario == "Loss ratio plateaus at 78%":
    lr_override = [max(0.78, lr) for lr in plan_lr]
    sb.caption("Fraud on income-benefit claims proves harder to control than "
               "modelled. §6.7, first failure mode.")
elif scenario == "Growth stalls at 7 lakh":
    growth = 700000 / CFG["portfolio"]["trajectory"][-1]["workers"]
    sb.caption("The Zego failure mode (§3.5): the expense ratio never falls "
               "because premium never reaches scale. §6.7, second failure mode.")
elif scenario == "Custom":
    growth = sb.slider("Growth multiplier on worker count", 0.3, 1.5, 1.0, 0.05)
    floor = sb.slider("Loss ratio floor", 0.55, 1.00, 0.64, 0.01)
    lr_override = [max(floor, lr) for lr in plan_lr]

gwp_pw = sb.slider("GWP per active worker (₹/year)", 3000, 9000,
                   CFG["portfolio"]["gwp_per_worker"], 100)

df = portfolio.trajectory(loss_ratio_override=lr_override,
                          growth_factor=growth, gwp_per_worker=gwp_pw)
sol = portfolio.solvency_position(df)
be = portfolio.breakeven_year(df)
final = df.iloc[-1]

# ------------------------------------------------------------------ headline
c1, c2, c3, c4 = st.columns(4)
c1.metric("Underwriting break-even",
          f"Year {be}" if be else "Not reached",
          "plan: year 7")
c2.metric("Year 7 combined ratio", f"{final['Combined ratio']:.0%}")
c3.metric("Year 7 GWP", crore(final["GWP"]),
          f"{final['Active workers']:,.0f} workers")
c4.metric("Cumulative UW result", crore(final["Cumulative UW result"]),
          "years 1–7")

if be is None:
    st.error("**This scenario never reaches underwriting profit.** The book "
             "would need either a further capital round or a change of strategy "
             "— the plan's response is in §6.7: extend to ride-hail and bike-taxi "
             "drivers rather than cutting price to buy volume.")
elif be > 7:
    st.warning(f"Break-even slips to year {be}, beyond the funded plan.")

st.divider()

# ------------------------------------------------------------------ the point
st.subheader("Read the expense ratio, not the loss ratio")
section_ref("§6.4")

fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Bar(x=df["Year"], y=df["GWP"] / 1e7, name="GWP (₹ cr)",
                     marker_color="#dfe6ee"), secondary_y=True)
fig.add_trace(go.Scatter(x=df["Year"], y=df["Loss ratio"] * 100,
                         name="Loss ratio", mode="lines+markers",
                         line=dict(color="#c0392b", width=3)))
fig.add_trace(go.Scatter(x=df["Year"], y=df["Expense ratio"] * 100,
                         name="Expense ratio", mode="lines+markers",
                         line=dict(color="#2c6fbb", width=3)))
fig.add_trace(go.Scatter(x=df["Year"], y=df["Combined ratio"] * 100,
                         name="Combined ratio", mode="lines+markers",
                         line=dict(color="#2d3436", width=3, dash="dot")))
fig.add_hline(y=100, line_dash="dash", line_color="#888",
              annotation_text="underwriting break-even")
fig.update_yaxes(title_text="Ratio (%)", secondary_y=False)
fig.update_yaxes(title_text="GWP (₹ crore)", secondary_y=True, showgrid=False)
fig.update_layout(height=430, margin=dict(l=0, r=0, t=20, b=0),
                  xaxis_title="Year", legend=dict(orientation="h", y=1.12))
st.plotly_chart(fig, width="stretch")

st.info(
    f"The loss ratio reaches a respectable **{df.iloc[3]['Loss ratio']:.0%}** by "
    f"year four and improves slowly after that. What actually moves the combined "
    f"ratio from **{df.iloc[0]['Combined ratio']:.0%}** to "
    f"**{final['Combined ratio']:.0%}** is the expense ratio collapsing from "
    f"**{df.iloc[0]['Expense ratio']:.0%}** to **{final['Expense ratio']:.0%}** "
    "as premium grows against a largely fixed regulatory cost base. This is the "
    "single most important line in the financial plan, and it is what the "
    "international benchmark in §3.5 teaches: their loss ratio was excellent "
    "throughout, and they still needed eight years, because turnover took that "
    "long to cover fixed costs."
)

st.divider()

# ------------------------------------------------------------------ P&L
st.subheader("Year by year")
show = df.copy()
show["Active workers"] = show["Active workers"].map(lambda v: f"{v:,.0f}")
show["GWP"] = show["GWP"].map(crore)
show["Underwriting result"] = show["Underwriting result"].map(crore)
show["Investment income"] = show["Investment income"].map(crore)
show["Profit before tax"] = show["Profit before tax"].map(crore)
show["Cumulative UW result"] = show["Cumulative UW result"].map(crore)
for c in ["Loss ratio", "Expense ratio", "Combined ratio"]:
    show[c] = show[c].map(lambda v: f"{v:.0%}")
st.dataframe(
    show[["Year", "Active workers", "GWP", "Loss ratio", "Expense ratio",
          "Combined ratio", "Underwriting result", "Investment income",
          "Profit before tax", "Cumulative UW result"]],
    width="stretch", hide_index=True,
)

st.warning(
    "**Net profit and underwriting profit arrive at different times, and it "
    "matters which one we claim.** With ₹300 crore of shareholder capital in "
    "the entity from launch, investment income alone runs to roughly ₹20 crore "
    "a year regardless of how the book performs — so reported net profit turns "
    "positive well before underwriting does. That is investment income carrying "
    "an underwriting loss, and it proves nothing about whether the business "
    "works. The number to be judged on is the combined ratio crossing 100%."
)

st.divider()

# ------------------------------------------------------------------ solvency
st.subheader("Solvency")
section_ref("§6.6 and §12.6")

s = CFG["portfolio"]["solvency"]
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=sol["Year"], y=sol["Solvency ratio"] * 100,
                          mode="lines+markers", name="Solvency ratio",
                          line=dict(color="#2c6fbb", width=3)))
fig2.add_hline(y=s["statutory_ratio"] * 100, line_dash="dash",
               line_color="#c0392b",
               annotation_text="statutory floor 150%")
fig2.add_hline(y=s["internal_throttle_ratio"] * 100, line_dash="dot",
               line_color="#e67e22",
               annotation_text="internal throttle 180%")
fig2.add_hline(y=s["target_ratio"] * 100, line_dash="dot", line_color="#27ae60",
               annotation_text="target 200%")
fig2.update_layout(height=360, margin=dict(l=0, r=0, t=20, b=0),
                   xaxis_title="Year", yaxis_title="Solvency ratio (%)")
st.plotly_chart(fig2, width="stretch")

breaches = sol[~sol["Above statutory 150%"]]
throttles = sol[~sol["Above throttle 180%"]]
if len(breaches):
    st.error(f"**Statutory breach in year(s) {list(breaches['Year'])}.** This is "
             "not a bad quarter — it is a regulatory event that can stop new "
             "business being written and end a fundraise in progress.")
elif len(throttles):
    st.warning(f"Internal throttle would fire in year(s) {list(throttles['Year'])}. "
               "New business writing throttles automatically before the "
               "regulator has to say anything.")
else:
    st.success("Solvency stays above the 180% internal throttle throughout.")

solshow = sol.copy()
for c in ["Capital raised (cumulative)", "Net worth (ASM proxy)", "RSM"]:
    solshow[c] = solshow[c].map(crore)
solshow["Solvency ratio"] = solshow["Solvency ratio"].map(lambda v: f"{v:.0%}")
st.dataframe(solshow[["Year", "Capital raised (cumulative)",
                      "Net worth (ASM proxy)", "RSM", "Solvency ratio"]],
             width="stretch", hide_index=True)

st.caption(
    "RSM figures are indicative, computed on simplified factors (higher of the "
    "₹50 crore floor and 20% of net written premium). The actual calculation is "
    "line-specific and must be certified by the Appointed Actuary. Note the "
    "counter-intuitive mechanism: required solvency margin scales with premium, "
    "so the quarters in which the book is growing fastest are the ones in which "
    "the ratio falls hardest."
)

st.divider()

# ------------------------------------------------------------------ per rider
l, r = st.columns(2)
with l:
    st.subheader("Steady-state per-rider P&L")
    section_ref("§6.2")
    pnl = portfolio.per_rider_pnl()
    pnl["% of GWP"] = pnl["% of GWP"].map(lambda v: f"{v:.0%}")
    pnl["Rs per rider-year"] = pnl["Rs per rider-year"].map(inr)
    st.dataframe(pnl, width="stretch", hide_index=True)

with r:
    st.subheader("Expected claim cost")
    section_ref("§6.1 — burning cost build-up, per 1,000 full-time riders")
    bc = portfolio.burning_cost()
    bdf = pd.DataFrame(bc["rows"])
    bdf["Average claim"] = bdf["Average claim"].map(inr)
    bdf["Annual cost per 1,000"] = bdf["Annual cost per 1,000"].map(inr)
    st.dataframe(bdf, width="stretch", hide_index=True)
    st.metric("Expected claim cost per rider-year", inr(bc["per_rider"]))
    st.caption("A full-time delivery rider covers 30,000–45,000 km a year in "
               "Indian urban traffic — roughly ten times a private two-wheeler "
               "owner's exposure. The variance in annual kilometres across this "
               "population is exactly why a flat premium cannot work.")

st.divider()
st.subheader("Capital plan")
cap = portfolio.capital_plan()
cap["amount_cr"] = cap["amount_cr"].map(lambda v: f"₹{v:,.0f} cr")
cap.columns = ["Round", "Year", "Amount"]
st.dataframe(cap, width="stretch", hide_index=True)
total = sum(r["amount_cr"] for r in CFG["portfolio"]["funding_rounds"])
st.caption(f"Total equity to underwriting break-even: **₹{total:,.0f} crore**. "
           "The ₹100 crore of paid-up capital sits inside the insurance entity "
           "and is not available to fund the build, marketing or salaries.")
