"""Insurer console — portfolio overview."""
from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from shared import (topbar, h, kpi, inr, crore, lakh, badge, rows, MUTED,
                    PRIMARY, ACCENT, OK, LINE, riders, note)
from engine import store, portfolio
from engine.config import CFG

topbar("Insurer console",
       f"Book as at {datetime.now().strftime('%d %b %Y, %H:%M')} · live production data")

R = riders()
live_pols = store.active_policies()
m = store.claim_metrics()

# Live book = the synthetic in-force book plus whatever the demo rider holds
BOOK = len(R) + len(live_pols)
gwp_pw = CFG["portfolio"]["gwp_per_worker"]
run_rate = BOOK * gwp_pw

h("Portfolio", "The in-force book, updated as policies are issued and claims "
  "are settled.")

k = st.columns(5)
kpi(k[0], "Policies in force", f"{BOOK:,}",
    f"+{len(live_pols)} issued in this session")
kpi(k[1], "GWP run-rate", crore(run_rate), "annualised")
kpi(k[2], "Average premium", inr(gwp_pw), "per worker per year")
kpi(k[3], "Claims settled", f"{m['paid']}", inr(m["paid_amount"]))
kpi(k[4], "Settlement ratio", f"{m['settlement_ratio']:.0%}",
    f"repudiation {m['repudiation_rate']:.0%}")

st.write("")

# ------------------------------------------------------------------ growth
g1, g2 = st.columns([1.4, 1])

with g1:
    st.markdown("**Book growth against plan**")
    traj = portfolio.trajectory()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=traj["Year"], y=traj["GWP"] / 1e7, name="GWP (₹ cr)",
                         marker_color=PRIMARY))
    fig.add_trace(go.Scatter(x=traj["Year"], y=traj["Active workers"] / 1e5,
                             name="Workers (lakh)", yaxis="y2",
                             line=dict(color=ACCENT, width=3)))
    fig.add_vrect(x0=0.5, x1=1.5, fillcolor="#DCE9E7", opacity=.45,
                  line_width=0, annotation_text="we are here")
    fig.update_layout(height=330, margin=dict(l=0, r=0, t=28, b=0),
                      yaxis=dict(title="GWP (₹ crore)"),
                      yaxis2=dict(title="Workers (lakh)", overlaying="y",
                                  side="right", showgrid=False),
                      legend=dict(orientation="h", y=1.16),
                      xaxis_title="Year")
    st.plotly_chart(fig, width="stretch")

with g2:
    st.markdown("**Book mix**")
    tab1, tab2, tab3 = st.tabs(["Segment", "City", "Platform"])
    with tab1:
        d = R["segment"].value_counts()
        f = go.Figure(go.Pie(labels=d.index, values=d.values, hole=.58,
                             marker_colors=[PRIMARY, "#3E8F87", "#9BB5B2"]))
        f.update_layout(height=250, margin=dict(l=0, r=0, t=6, b=0))
        st.plotly_chart(f, width="stretch")
    with tab2:
        d = R["city"].value_counts()
        f = go.Figure(go.Pie(labels=[i.split(" (")[0] for i in d.index],
                             values=d.values, hole=.58,
                             marker_colors=[PRIMARY, "#3E8F87", "#9BB5B2"]))
        f.update_layout(height=250, margin=dict(l=0, r=0, t=6, b=0))
        st.plotly_chart(f, width="stretch")
    with tab3:
        d = R["platform"].value_counts()
        f = go.Figure(go.Pie(labels=d.index, values=d.values, hole=.58,
                             marker_colors=[PRIMARY, "#3E8F87", "#9BB5B2",
                                            "#C4D3D1"]))
        f.update_layout(height=250, margin=dict(l=0, r=0, t=6, b=0))
        st.plotly_chart(f, width="stretch")

st.divider()

# ------------------------------------------------------------------ exposure
h("Exposure is the unit we sell",
  "We do not sell policies, we sell covered hours. This is what distinguishes "
  "the book from a conventional personal accident portfolio.")

e = st.columns(4)
total_hours = R["hours_per_month"].sum()
kpi(e[0], "Covered hours a month", f"{total_hours/1e5:.1f} lakh",
    "the actual revenue driver")
kpi(e[1], "Average per worker", f"{R['hours_per_month'].mean():.0f} hrs",
    "plan assumes 180 blended")
kpi(e[2], "Heaviest decile", f"{R['hours_per_month'].quantile(.9):.0f} hrs",
    f"vs {R['hours_per_month'].quantile(.1):.0f} in the lightest")
kpi(e[3], "Spread, P90 : P10",
    f"{R['hours_per_month'].quantile(.9)/R['hours_per_month'].quantile(.1):.1f}×",
    "why a flat premium cannot work")

st.write("")
x1, x2 = st.columns([1.4, 1])
with x1:
    fig2 = px.histogram(R, x="hours_per_month", color="segment", nbins=44,
                        color_discrete_sequence=["#9BB5B2", "#3E8F87", PRIMARY],
                        labels={"hours_per_month": "Active hours per month"})
    fig2.update_layout(height=300, margin=dict(l=0, r=0, t=26, b=0),
                       legend=dict(orientation="h", y=1.16),
                       yaxis_title="Policies")
    st.plotly_chart(fig2, width="stretch")
with x2:
    seg = R.groupby("segment").agg(
        Policies=("rider_id", "count"),
        Hours=("hours_per_month", "mean"),
        Earnings=("monthly_net_earnings", "mean")).reset_index()
    seg["Premium/yr"] = (seg["Hours"] * 12 * 2.5).map(inr)
    seg["Hours"] = seg["Hours"].map(lambda v: f"{v:.0f}")
    seg["Earnings"] = seg["Earnings"].map(inr)
    seg.columns = ["Segment", "Policies", "Hrs/mo", "Earnings", "Premium/yr"]
    st.dataframe(seg, width="stretch", hide_index=True)
    note("A rider on 40 hours a month and one on 260 pay different premiums for "
         "the same cover. Under a flat annual premium the first would be "
         "overcharged and would not buy; the second would be underpriced and we "
         "would lose money on them.")

st.divider()

# ------------------------------------------------------------------ recent
h("Recently issued")
pols = store.store()["policies"]
if pols:
    df = pd.DataFrame([{
        "Policy": p.policy_id,
        "Rider": store.rider().name,
        "Plan": p.tier,
        "Add-ons": ", ".join(p.addons) if p.addons else "—",
        "Started": datetime.fromisoformat(p.started).strftime("%d %b %Y"),
        "Hours covered": f"{p.hours_covered:,.0f}",
        "Premium to date": inr(p.premium_collected),
        "Claims": p.claims_made,
        "Status": p.status,
    } for p in pols])
    st.dataframe(df, width="stretch", hide_index=True)

ev = store.store()["events"]
if ev:
    st.markdown("**Activity log this session**")
    st.dataframe(pd.DataFrame(ev).rename(columns={"at": "Time", "msg": "Event"}),
                 width="stretch", hide_index=True, height=180)
