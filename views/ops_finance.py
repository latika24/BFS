"""Insurer console — finance, solvency and capital."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from shared import (topbar, h, kpi, inr, crore, MUTED, PRIMARY, ACCENT, OK,
                    BAD, WARN, note)
from engine import portfolio
from engine.config import CFG

topbar("Insurer console", "Finance & solvency")

h("Finance & solvency",
  "The book from year 1 to year 7, the capital that supports it, and the "
  "scenarios in which the plan does not work.")

# ------------------------------------------------------------------ scenario
sb = st.sidebar
sb.header("Scenario")
scenario = sb.radio("Preset", ["Base plan", "Loss ratio plateaus at 78%",
                               "Growth stalls at 7 lakh", "Custom"], index=0)

plan_lr = [y["loss_ratio"] for y in CFG["portfolio"]["trajectory"]]
growth, lr_override = 1.0, None

if scenario == "Loss ratio plateaus at 78%":
    lr_override = [max(0.78, lr) for lr in plan_lr]
    sb.caption("Fraud on income-benefit claims proves harder to control than "
               "modelled.")
elif scenario == "Growth stalls at 7 lakh":
    growth = 700000 / CFG["portfolio"]["trajectory"][-1]["workers"]
    sb.caption("The book never reaches the scale that drags the expense ratio "
               "down. This is the failure mode the only comparable business "
               "actually experienced.")
elif scenario == "Custom":
    growth = sb.slider("Growth multiplier", 0.3, 1.5, 1.0, 0.05)
    floor = sb.slider("Loss ratio floor", 0.55, 1.00, 0.64, 0.01)
    lr_override = [max(floor, lr) for lr in plan_lr]

gwp_pw = sb.slider("Premium per worker (₹/yr)", 3000, 9000,
                   CFG["portfolio"]["gwp_per_worker"], 100)

df = portfolio.trajectory(loss_ratio_override=lr_override,
                          growth_factor=growth, gwp_per_worker=gwp_pw)
sol = portfolio.solvency_position(df)
be = portfolio.breakeven_year(df)
final = df.iloc[-1]

k = st.columns(5)
kpi(k[0], "Underwriting break-even", f"Year {be}" if be else "Not reached",
    "plan: year 7")
kpi(k[1], "Year 7 combined ratio", f"{final['Combined ratio']:.0%}")
kpi(k[2], "Year 7 GWP", crore(final["GWP"]),
    f"{final['Active workers']:,.0f} workers")
kpi(k[3], "Cumulative UW result", crore(final["Cumulative UW result"]),
    "years 1–7")
kpi(k[4], "Equity required",
    f"₹{sum(r['amount_cr'] for r in CFG['portfolio']['funding_rounds']):,.0f} cr",
    "three rounds")

if be is None:
    st.error("**This scenario never reaches underwriting profit.** The response "
             "in the plan is to extend into the 55 lakh bike-taxi and "
             "ride-hailing pool rather than cut price to buy volume.")

st.write("")
st.divider()

# ------------------------------------------------------------------ ratios
h("It is the expense ratio that moves, not the loss ratio")

fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Bar(x=df["Year"], y=df["GWP"] / 1e7, name="GWP (₹ cr)",
                     marker_color="#DFE8E7"), secondary_y=True)
for col, colour, name in [("Loss ratio", BAD, "Loss ratio"),
                          ("Expense ratio", PRIMARY, "Expense ratio"),
                          ("Combined ratio", "#2d3436", "Combined ratio")]:
    fig.add_trace(go.Scatter(x=df["Year"], y=df[col] * 100, name=name,
                             mode="lines+markers",
                             line=dict(color=colour, width=3,
                                       dash="dot" if col == "Combined ratio" else None)))
fig.add_hline(y=100, line_dash="dash", line_color="#888",
              annotation_text="underwriting break-even")
fig.update_yaxes(title_text="Ratio (%)", secondary_y=False)
fig.update_yaxes(title_text="GWP (₹ crore)", secondary_y=True, showgrid=False)
fig.update_layout(height=380, margin=dict(l=0, r=0, t=24, b=0),
                  xaxis_title="Year", legend=dict(orientation="h", y=1.14))
st.plotly_chart(fig, width="stretch")

st.info(f"The loss ratio reaches **{df.iloc[3]['Loss ratio']:.0%}** by year four "
        f"and improves slowly after. What moves the combined ratio from "
        f"**{df.iloc[0]['Combined ratio']:.0%}** to "
        f"**{final['Combined ratio']:.0%}** is the expense ratio falling from "
        f"**{df.iloc[0]['Expense ratio']:.0%}** to "
        f"**{final['Expense ratio']:.0%}** as premium grows against a largely "
        "fixed regulatory cost base — an Appointed Actuary, a Chief Risk "
        "Officer, statutory audit and quarterly solvency reporting cost much "
        "the same at 20,000 policies as at 12 lakh.")

st.write("")
show = df.copy()
show["Active workers"] = show["Active workers"].map(lambda v: f"{v:,.0f}")
for c in ["GWP", "Underwriting result", "Investment income",
          "Profit before tax", "Cumulative UW result"]:
    show[c] = show[c].map(crore)
for c in ["Loss ratio", "Expense ratio", "Combined ratio"]:
    show[c] = show[c].map(lambda v: f"{v:.0%}")
st.dataframe(show[["Year", "Active workers", "GWP", "Loss ratio",
                   "Expense ratio", "Combined ratio", "Underwriting result",
                   "Investment income", "Profit before tax",
                   "Cumulative UW result"]],
             width="stretch", hide_index=True)

note("<b>Net profit and underwriting profit arrive at different times, and it "
     "matters which we claim.</b> With shareholder capital sitting in the "
     "entity from launch, investment income alone runs to roughly ₹20 crore a "
     "year regardless of how the book performs, so reported net profit turns "
     "positive well before underwriting does. That is investment income "
     "carrying an underwriting loss. The number to be judged on is the combined "
     "ratio crossing 100%.")

st.divider()

# ------------------------------------------------------------------ solvency
h("Solvency", "Required margin scales with premium, so the quarters in which "
  "the book grows fastest are the ones in which the ratio falls hardest.")

s = CFG["portfolio"]["solvency"]
sv1, sv2 = st.columns([1.4, 1])

with sv1:
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=sol["Year"], y=sol["Solvency ratio"] * 100,
                              mode="lines+markers", name="Solvency ratio",
                              line=dict(color=PRIMARY, width=3),
                              fill="tozeroy", fillcolor="rgba(15,92,87,.08)"))
    fig2.add_hline(y=s["statutory_ratio"] * 100, line_dash="dash",
                   line_color=BAD, annotation_text="statutory floor 150%")
    fig2.add_hline(y=s["internal_throttle_ratio"] * 100, line_dash="dot",
                   line_color=WARN, annotation_text="internal throttle 180%")
    fig2.add_hline(y=s["target_ratio"] * 100, line_dash="dot", line_color=OK,
                   annotation_text="target 200%")
    fig2.update_layout(height=330, margin=dict(l=0, r=0, t=24, b=0),
                       xaxis_title="Year", yaxis_title="Solvency ratio (%)")
    st.plotly_chart(fig2, width="stretch")

with sv2:
    breach = sol[~sol["Above statutory 150%"]]
    throttle = sol[~sol["Above throttle 180%"]]
    if len(breach):
        st.error(f"**Statutory breach in year(s) {list(breach['Year'])}.** Not a "
                 "bad quarter — a regulatory event that stops new business "
                 "being written and ends a fundraise in progress.")
    elif len(throttle):
        st.warning(f"Internal throttle fires in year(s) {list(throttle['Year'])}. "
                   "New business writing slows automatically before the "
                   "regulator has to intervene.")
    else:
        st.success("Above the 180% internal throttle throughout.")

    ss_ = sol.copy()
    for c in ["Capital raised (cumulative)", "Net worth (ASM proxy)", "RSM"]:
        ss_[c] = ss_[c].map(crore)
    ss_["Solvency ratio"] = ss_["Solvency ratio"].map(lambda v: f"{v:.0%}")
    st.dataframe(ss_[["Year", "Capital raised (cumulative)", "RSM",
                      "Solvency ratio"]], width="stretch", hide_index=True)

st.caption("RSM computed on simplified factors — the higher of the ₹50 crore "
           "floor and 20% of net written premium. The statutory calculation is "
           "line-specific and certified by the Appointed Actuary. Ceding 30% "
           "through the quota share is a capital instrument as much as a risk "
           "one: it reduces required margin materially in the growth years.")

st.divider()

# ------------------------------------------------------------------ unit
u1, u2 = st.columns(2)

with u1:
    h("Unit economics, at steady state")
    pnl = portfolio.per_rider_pnl()
    pnl["% of GWP"] = pnl["% of GWP"].map(lambda v: f"{v:.0%}")
    pnl["Rs per rider-year"] = pnl["Rs per rider-year"].map(inr)
    pnl.columns = ["Line", "₹ per rider-year", "% of premium"]
    st.dataframe(pnl, width="stretch", hide_index=True)

with u2:
    h("Where the premium rupee goes")
    p = CFG["portfolio"]
    fin = p["trajectory"][-1]
    parts = [("Claims to riders", fin["loss_ratio"]),
             ("Reinsurance", p["reinsurance_pct_gwp"]),
             ("Running the company", fin["expense_ratio"]),
             ("No-claim wallet, back to riders", p["no_claim_wallet_pct_gwp"]),
             ("Underwriting margin",
              1 - fin["loss_ratio"] - fin["expense_ratio"]
              - p["reinsurance_pct_gwp"] - p["no_claim_wallet_pct_gwp"])]
    figp = go.Figure(go.Pie(
        labels=[a for a, _ in parts], values=[b for _, b in parts], hole=.56,
        marker_colors=[PRIMARY, "#6E9E99", "#A9C0BD", OK, ACCENT],
        textinfo="label+percent"))
    figp.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0),
                       showlegend=False)
    st.plotly_chart(figp, width="stretch")
    back = fin["loss_ratio"] + p["no_claim_wallet_pct_gwp"]
    st.caption(f"**{back:.0%} of every rupee goes back to the rider** as claims "
               "or wallet credits. Published monthly — it is the number we lead "
               "with in the field, and one a broker could never credibly claim "
               "because a broker does not control it.")

st.divider()

# ------------------------------------------------------------------ capital
h("Capital plan")
cap = portfolio.capital_plan()[["name", "year", "amount_cr", "investors",
                                "underwriting"]].copy()
cap["amount_cr"] = cap["amount_cr"].map(lambda v: f"₹{v:,.0f} cr")
cap.columns = ["Round", "Year", "Size", "Investor types", "What they underwrite"]
st.dataframe(cap, width="stretch", hide_index=True)
note(f"<b>A discrepancy in the plan worth resolving.</b> "
     f"{CFG['portfolio']['funding_note']}")
