"""Rider app — my cover."""
from __future__ import annotations

from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from shared import (light, html, topbar, h, kpi, inr, lakh, rows, badge, MUTED, PRIMARY,
                    OK, LINE, empty)
from engine import store
from engine.config import CFG

r = store.rider()
pols = store.active_policies()
allp = store.store()["policies"]
ben = store.benefits()

topbar("Rider app", f"{r.name} · {r.rider_id}")

h("My cover", "Everything you hold, what it pays, and what you have paid for it.")

if not pols:
    empty("You have no active cover. Head to <b>Buy cover</b> to get protected "
          "from ₹8 a shift.")
    st.stop()

# ------------------------------------------------------------------ the policy
for p in pols:
    started = datetime.fromisoformat(p.started)
    months = max(1, int((datetime.now() - started).days / 30))
    contents = CFG["tiers"][p.tier]["contents"]

    _rows1 = rows([
        ("Covers", contents),
        ("Add-ons", ", ".join(p.addons) if p.addons else "—"),
        ("Base rate", "₹%.2f per active hour" % p.base_rate),
        ("Hours covered so far", "{:,.0f} hours".format(p.hours_covered)),
        ("Premium paid to date", inr(p.premium_collected)),
        ("No-claim wallet",
         "<span style='color:%s'>%s</span>" % (OK, inr(p.wallet))),
        ("Claims made", str(p.claims_made)),
    ])

    st.markdown(html(f"""
    <div class='pol'>
      <div class='h'>
        <span class='hl'><span class='t'>{p.tier}</span><br>
              <span class='n'>{p.policy_id}</span></span>
        <span class='hr'>{badge('Active', 'ok')}<br>
              <span style='font-size:.76rem;color:{MUTED}'>
              since {started.strftime('%d %b %Y')}</span></span>
      </div>
      <div class='b'>{_rows1}</div>
    </div>"""), unsafe_allow_html=True)

    a, b, c = st.columns(3)
    if a.button("Download certificate", key=f"cert{p.policy_id}",
                width="stretch"):
        st.session_state["show_cert"] = p.policy_id
    if b.button("Change plan", key=f"chg{p.policy_id}", width="stretch"):
        st.switch_page("views/rider_buy.py")
    if c.button("Cancel cover", key=f"can{p.policy_id}", width="stretch"):
        store.cancel_policy(p.policy_id)
        st.rerun()

    if st.session_state.get("show_cert") == p.policy_id:
        cert = f"""GIGSURE GENERAL INSURANCE
CERTIFICATE OF INSURANCE

Policy number      {p.policy_id}
Policyholder       {r.name}  ({r.rider_id})
Vehicle            {r.vehicle_reg}
Plan               {p.tier}
Effective from     {started.strftime('%d %B %Y')}
Basis              Usage-based. Cover is live during declared or
                   detected on-duty riding only.
Rating             ₹{p.base_rate:.2f} per active hour, adjusted for time,
                   weather, city and riding behaviour, within a
                   governance band of 0.6x to 2.2x.

BENEFITS
  Accidental death / permanent total disability   {inr(ben['accidental_death']['value'])}
  Daily income benefit                            {inr(ben['daily_income_benefit']['value'])} per day
                                                  3-day wait, 90 days maximum
  Hospital daily cash                             {inr(ben['fixed']['hospital_daily_cash'])} per day, 30 days
  Fracture and OPD                                {inr(ben['fixed']['fracture_range'][0])}–{inr(ben['fixed']['fracture_range'][1])}
  Ambulance                                       up to {inr(ben['fixed']['ambulance_network_cap'])}
  Legal assistance                                panel lawyer, MV Act matters

This policy belongs to the policyholder, not to any platform. It stays in
force across every app the policyholder earns from, and continues if they
stop riding for any particular platform.
"""
        st.code(cert, language=None)
        st.download_button("Save as .txt", cert,
                           file_name=f"{p.policy_id}.txt", mime="text/plain")

st.divider()

# ------------------------------------------------------------------ benefits
h("What you are covered for",
  "Your benefit amounts are not fixed numbers we picked — they scale with what "
  "you actually earn, which we read from your bank with your consent.")

b1, b2 = st.columns([1.15, 1])

with b1:
    ad = ben["accidental_death"]
    dib = ben["daily_income_benefit"]
    big = "<b style='color:%s;font-size:1.05rem'>%%s</b>" % PRIMARY
    sub = "<span style='font-size:.8rem;color:%s'>%%s</span>" % MUTED
    fx = ben["fixed"]
    _rows2 = rows([
        ("<b>If you die or are permanently disabled</b>",
         big % inr(ad["value"])),
        (sub % "8 × your yearly earnings", ""),
        ("<b>If you cannot ride</b>", big % (inr(dib["value"]) + "/day")),
        (sub % "75% of a normal day, from day 4, up to 90 days", ""),
        ("If you are admitted to hospital",
         inr(fx["hospital_daily_cash"]) + "/day"),
        ("If you break a bone",
         inr(fx["fracture_range"][0]) + "–" + inr(fx["fracture_range"][1])),
        ("Ambulance", "Paid direct to the ambulance"),
        ("Your bike, damaged on shift",
         inr(ben["vehicle"]["per_event"]) + " per repair"),
        ("An order you had to pay for", "The exact amount deducted"),
        ("Legal help after an FIR", "Panel lawyer, no extra cost"),
    ])
    st.markdown("<div class='card'>%s</div>" % _rows2, unsafe_allow_html=True)

with b2:
    st.markdown("**How your income cover was worked out**")
    st.markdown(
        html(f"<div style='color:{MUTED};font-size:.87rem;line-height:1.6'>"
        f"You earn about <b>{inr(r.monthly_net_earnings)}</b> a month, which is "
        f"<b>{inr(r.daily_net_earnings)}</b> on a working day.<br><br>"
        f"We pay <b>75%</b> of that — {inr(dib['gross'])} — capped at ₹1,200. "
        f"So your benefit is <b>{inr(dib['value'])} a day</b>.<br><br>"
        "It is deliberately less than you earn riding. It has to be: nobody "
        "should be better off staying at home than working.</div>"),
        unsafe_allow_html=True)

    st.write("")
    weeks = st.slider("If you were off the road for…", 1, 12, 6,
                      format="%d weeks")
    days = min(weeks * 6, dib["max_days"])
    payout = max(0, days - dib["waiting_days"]) * dib["value"]
    lost = days * r.daily_net_earnings
    _rows3 = rows([
        ('Days off the road', f"{days}"),
        ('Earnings you would lose', inr(lost)),
        ('We pay you', f"<b style='color:{PRIMARY}'>{inr(payout)}</b>"),
        ('Covers', f"{payout/lost:.0%} of the hole" if lost else "—"),
    ])
    st.markdown(f"""<div class='card' style='background:#F4F9F8'>{_rows3}</div>""", unsafe_allow_html=True)

st.divider()

# ------------------------------------------------------------------ ledger
h("Your premium ledger", "Every rupee, every day. Nothing is deducted that you "
  "cannot see here.")

led = store.ledger_df()
lc1, lc2 = st.columns([1.4, 1])
with lc1:
    fig = go.Figure()
    fig.add_trace(go.Bar(x=led["date"], y=led["amount"], name="Charged",
                         marker_color=PRIMARY))
    fig.add_trace(go.Scatter(x=led["date"], y=led["hours"], name="Hours ridden",
                             yaxis="y2", line=dict(color="#C9D6D4", width=2)))
    fig.update_layout(height=260, margin=dict(l=0, r=0, t=24, b=0),
                      yaxis=dict(title="₹ charged"),
                      yaxis2=dict(title="hours", overlaying="y", side="right",
                                  showgrid=False),
                      legend=dict(orientation="h", y=1.16))
    st.plotly_chart(light(fig), use_container_width=True,
                    theme=None)

with lc2:
    k = st.columns(2)
    kpi(k[0], "30-day total", inr(led["amount"].sum()))
    kpi(k[1], "Busiest day", inr(led["amount"].max()))
    st.write("")
    show = led.tail(8).iloc[::-1].copy()
    show["amount"] = show["amount"].map(inr)
    show["rate"] = show["rate"].map(lambda v: f"₹{v:.2f}")
    show.columns = ["Date", "Hours", "Rate/hr", "Charged"]
    st.dataframe(show, width="stretch", hide_index=True, height=250)
