"""Insurer console — claims desk. Live queue, adjudication, SLA."""
from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from shared import (html, topbar, h, kpi, inr, rows, badge, MUTED, PRIMARY, ACCENT,
                    OK, BAD, WARN, CLAIM_BADGE, empty, note, riders)
from engine import store

topbar("Insurer console", "Claims desk · live queue")

m = store.claim_metrics()
queue = store.open_claims()

h("Claims desk", "Everything a rider raises lands here. Tier 1 is settled by "
  "machine before it reaches a human; this queue is the exceptions.")

k = st.columns(5)
kpi(k[0], "In queue", str(len(queue)), "needing a decision")
kpi(k[1], "Settled to date", str(m["paid"]), inr(m["paid_amount"]))
kpi(k[2], "Settlement ratio", f"{m['settlement_ratio']:.0%}", "target > 95%")
kpi(k[3], "Repudiation rate", f"{m['repudiation_rate']:.0%}",
    "hard ceiling 5%")
kpi(k[4], "Settled instantly", f"{m['instant_share']:.0%}", "target > 50%")

if m["repudiation_rate"] > 0.05:
    st.error("**Repudiation rate is above 5%.** The plan treats this as a hard "
             "ceiling: in a market whose core problem is that nobody trusts an "
             "insurer to pay, a rising rejection rate is an existential "
             "reputational risk, not a cost saving. Review the declines below.")

st.write("")

# ------------------------------------------------------------------ queue
h("Queue")

if not queue:
    empty("Queue is clear. Raise a claim from the rider app to see one arrive "
          "here.")
else:
    for c_ in queue:
        when = datetime.fromisoformat(c_.submitted)
        age_min = (datetime.now() - when).total_seconds() / 60
        flag_html = "".join(badge(f, "warn") + " " for f in c_.flags)

        with st.container(border=True):
            top = st.columns([2.3, 1, 1, 1.2])
            top[0].markdown(
                f"**{c_.incident}**  \n"
                + html(f"<span style='color:{MUTED};font-size:.8rem'>"
                       f"{c_.claim_id} · {c_.rider_name} ({c_.rider_id}) · "
                       f"policy {c_.policy_id}</span>"),
                unsafe_allow_html=True)
            top[1].markdown(html(f"**{inr(c_.amount_claimed)}**  \n"
                            f"<span style='color:{MUTED};font-size:.8rem'>"
                            f"{c_.basis}</span>"), unsafe_allow_html=True)
            top[2].markdown(html(f"**Tier {c_.tier}**  \n"
                            f"<span style='color:{MUTED};font-size:.8rem'>"
                            f"raised {age_min:.0f} min ago</span>"),
                            unsafe_allow_html=True)
            top[3].markdown(html(badge(c_.status, CLAIM_BADGE.get(c_.status, "mute"))
                            + " " + flag_html), unsafe_allow_html=True)

            ev = st.columns([1.5, 1])
            with ev[0]:
                yes = "<span style='color:%s'>Yes</span>" % OK
                no = "<span style='color:%s'>No</span>" % BAD
                det = "<span style='color:%s'>Detected</span>" % OK
                none_ = "<span style='color:%s'>None</span>" % BAD
                _ev = rows([
                    ("Cover live at reported time", yes if c_.cover_live else no),
                    ("Impact signature in accelerometer",
                     det if c_.telematics_impact else none_),
                    ("Benefit head", c_.head),
                    ("Settlement basis", c_.basis),
                ])
                st.markdown("<div style='font-size:.85rem'>%s</div>" % _ev,
                            unsafe_allow_html=True)
            with ev[1]:
                amt = st.number_input("Approve amount", 0,
                                      int(c_.amount_claimed * 2),
                                      int(c_.amount_claimed), 100,
                                      key=f"amt{c_.claim_id}")
                b1, b2 = st.columns(2)
                if b1.button("Settle", key=f"set{c_.claim_id}",
                             type="primary", width="stretch"):
                    store.settle(c_, amt)
                    st.rerun()
                if b2.button("Decline", key=f"dec{c_.claim_id}",
                             width="stretch"):
                    store.decline(
                        c_, "Declined at claims desk after review of the "
                            "telematics record and cover status.")
                    st.rerun()

st.divider()

# ------------------------------------------------------------------ sla
h("Service performance", "Published monthly — settlement ratio, median "
  "turnaround and the reason for every rejection.")

s1, s2 = st.columns([1.3, 1])

with s1:
    fig = go.Figure(go.Bar(
        x=["Tier 1 — instant", "Tier 2 — fast-track", "Tier 3 — investigated"],
        y=[55, 35, 10],
        marker_color=[OK, PRIMARY, "#93A5A3"],
        text=["55%<br>under 60 sec", "35%<br>24–48 hrs", "10%<br>7 days"],
        textposition="inside"))
    fig.update_layout(height=280, margin=dict(l=0, r=0, t=24, b=0),
                      yaxis_title="Share of claims by count", showlegend=False)
    st.plotly_chart(fig, width="stretch")
    st.caption("Roughly 80% of premium sits in fixed benefits, so most claims "
               "need an event verified rather than a loss assessed. That is "
               "what makes machine settlement possible at all.")

with s2:
    settled = [c for c in store.claims() if c.settled]
    if settled:
        df = pd.DataFrame([{
            "Claim": c_.claim_id,
            "Rider": c_.rider_name,
            "Incident": c_.incident,
            "Paid": inr(c_.amount_approved) if c_.amount_approved else "—",
            "Status": c_.status,
            "TAT": ("%.0f sec" % (c_.turnaround_hours * 3600)
                    if c_.turnaround_hours is not None and c_.turnaround_hours < 0.05
                    else ("%.1f hrs" % c_.turnaround_hours
                          if c_.turnaround_hours is not None else "—")),
        } for c_ in settled])
        st.dataframe(df, width="stretch", hide_index=True, height=280)
    else:
        empty("Nothing settled yet.")

declines = [c for c in store.claims() if c.status == "Declined"]
if declines:
    st.markdown("**Rejections, with reasons — published verbatim**")
    st.dataframe(pd.DataFrame([{
        "Claim": c_.claim_id, "Incident": c_.incident,
        "Reason": c_.decline_reason} for c_ in declines]),
        width="stretch", hide_index=True)

st.divider()

# ------------------------------------------------------------------ fraud
h("Fraud controls",
  "The highest-frequency benefit is the daily income benefit, and the classic "
  "attack is a collusive certificate. Our defence is data we already hold.")

f = st.columns(3)
with f[0]:
    st.markdown("**Telematics contradiction check**")
    st.markdown(html(f"<div style='color:{MUTED};font-size:.87rem;line-height:1.6'>"
                "Runs daily on every open income-benefit claim. A rider drawing "
                "the benefit while the SDK shows them riding for another app is "
                "a provable, automatic denial. No conventional insurer can do "
                "this.</div>"), unsafe_allow_html=True)
    R = riders()
    flagged = int(len(R) * 0.006)
    st.metric("Open contradictions", flagged, "0.6% of active income claims")

with f[1]:
    st.markdown("**Crash signature**")
    t = np.linspace(0, 6, 260)
    real = np.where(t < 3, 0.4 * np.sin(3 * t) + 1.0,
                    np.where(t < 3.15, -14, 0.02 * np.random.default_rng(4).normal(size=260)))
    fake = 0.5 * np.sin(4 * t) + 1.0
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=t, y=real, name="Genuine crash",
                              line=dict(color=BAD, width=2)))
    fig2.add_trace(go.Scatter(x=t, y=fake, name="Staged / no impact",
                              line=dict(color="#9FB3B0", width=2, dash="dot")))
    fig2.update_layout(height=190, margin=dict(l=0, r=0, t=6, b=0),
                       yaxis_title="g-force", xaxis_title="seconds",
                       legend=dict(orientation="h", y=1.3))
    st.plotly_chart(fig2, width="stretch")
    st.caption("Deceleration spike, then the device goes still.")

with f[2]:
    st.markdown("**Controls by benefit**")
    st.dataframe(pd.DataFrame([
        {"Benefit": "Daily income", "Control": "Objective injury evidence + daily telematics check"},
        {"Benefit": "Hospital cash", "Control": "Minimum 24-hour admission"},
        {"Benefit": "Fracture", "Control": "X-ray required"},
        {"Benefit": "OPD", "Control": "Only against a corroborated incident"},
        {"Benefit": "Ambulance", "Control": "Paid to the operator, never cash"},
        {"Benefit": "Vehicle", "Control": "Baseline photos + network garage"},
        {"Benefit": "Deductions", "Control": "Platform statement is the evidence"},
    ]), width="stretch", hide_index=True, height=270)
