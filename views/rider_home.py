"""Rider app — home screen."""
from __future__ import annotations

from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from shared import (light, html, topbar, kpi, inr, rows, badge, MUTED, PRIMARY, ACCENT,
                    OK, CLAIM_BADGE, LINE)
from engine import store
from engine.config import CFG

s = store.store()
r = store.rider()
pols = store.active_policies()

topbar("Rider app", f"{r.name} · {r.rider_id} · {r.vehicle_reg}")

# ------------------------------------------------------------------ controls
c = st.columns([1, 1, 1, 1.4])
with c[0]:
    on = st.toggle("On duty", value=s["on_duty"])
    s["on_duty"] = on
with c[1]:
    band = st.selectbox("Time now", list(CFG["time_of_day"].keys()), index=3,
                        label_visibility="visible")
with c[2]:
    wx = st.selectbox("Weather", list(CFG["weather"].keys()), index=1)
with c[3]:
    hrs = st.slider("Hours ridden today", 0.0, 13.0, float(s["hours_today"]), 0.5)
    s["hours_today"] = hrs

q = store.current_rate(hours=max(hrs, 0.5), time_band=band, weather=wx)
rate = q["premium_per_hour"]
cost_today = rate * hrs
ben = store.benefits()

st.write("")

# ------------------------------------------------------------------ cover
left, right = st.columns([1.25, 1])

with left:
    if on and pols:
        st.markdown(html(f"""
        <div class='cover'>
          <div class='st'><span class='live'></span>You are covered</div>
          <div class='mt'>Riding for {r.platform.split(' (')[0]} ·
               {r.city.split(' (')[0]} · {wx.lower()}</div>
          <div class='rate'>₹{rate:.2f}<span style='font-size:1rem;
               font-weight:600'> /hour</span></div>
          <div class='rl'>Charged only while you are riding.
               Today so far: ₹{cost_today:.0f} for {hrs:.1f} hours.</div>
        </div>"""), unsafe_allow_html=True)
    elif not pols:
        st.markdown(html("""
        <div class='cover off'>
          <div class='st'>No active cover</div>
          <div class='mt'>You do not have a policy yet.</div>
          <div class='rate' style='font-size:1.4rem'>Buy cover to get protected</div>
          <div class='rl'>From ₹8 for a single shift.</div>
        </div>"""), unsafe_allow_html=True)
    else:
        st.markdown(html(f"""
        <div class='cover off'>
          <div class='st'>Cover is off</div>
          <div class='mt'>You are not on duty. You are not being charged.</div>
          <div class='rate' style='font-size:1.5rem'>₹0.00
               <span style='font-size:1rem;font-weight:600'>/hour</span></div>
          <div class='rl'>Go on duty and cover starts within seconds.</div>
        </div>"""), unsafe_allow_html=True)

    st.write("")
    k = st.columns(4)
    kpi(k[0], "Today", inr(cost_today), f"{hrs:.1f} hrs ridden")
    month_spend = sum(x["amount"] for x in s["ledger"])
    kpi(k[1], "This month", inr(month_spend),
        f"{sum(x['hours'] for x in s['ledger']):.0f} hrs")
    kpi(k[2], "No-claim wallet",
        inr(pols[0].wallet if pols else 0), "back to you each quarter")
    kpi(k[3], "Safety score", f"{r.safety_score:.0f}",
        f"×{q['multipliers']['M_behaviour']['value']:.2f} on your price")

with right:
    st.markdown("**If something happens today**")
    _fx = ben["fixed"]
    _body = rows([
        ("Cannot ride — per day",
         inr(ben["daily_income_benefit"]["value"])
         + " <span style='color:%s;font-weight:400;font-size:.78rem'>"
           "after 3 days</span>" % MUTED),
        ("Hospital — per day", inr(_fx["hospital_daily_cash"])),
        ("Broken bone",
         inr(_fx["fracture_range"][0]) + "–" + inr(_fx["fracture_range"][1])),
        ("Ambulance", "Covered, paid direct"),
        ("Your family, if the worst happens",
         "<b style='color:%s'>%s</b>" % (PRIMARY,
                                         inr(ben["accidental_death"]["value"]))),
    ])
    st.markdown("<div class='card'>%s</div>" % _body, unsafe_allow_html=True)

    st.write("")
    b1, b2 = st.columns(2)
    if b1.button("Raise a claim", type="primary", width="stretch"):
        st.switch_page("views/rider_claims.py")
    if b2.button("Buy more cover", width="stretch"):
        st.switch_page("views/rider_buy.py")

st.divider()

# ------------------------------------------------------------------ why price
w1, w2 = st.columns([1.3, 1])

with w1:
    st.markdown("**Why you are paying ₹%.2f an hour right now**" % rate)
    exp = q["exposure"]
    drivers = [
        (f"Base rate — {pols[0].tier if pols else 'GigSure Plus'}",
         CFG["tiers"][pols[0].tier if pols else "GigSure Plus"]["price_per_hour"], True),
        (f"Time — {band}", exp["m_time"], False),
        (f"Weather — {wx}", exp["m_weather"], False),
        (f"City — {r.city.split(' (')[0]}", exp["m_geo"], False),
        (f"Your riding — score {r.safety_score:.0f}",
         q["multipliers"]["M_behaviour"]["value"], False),
    ]
    fig = go.Figure(go.Bar(
        x=[d[1] for d in drivers[1:]], y=[d[0] for d in drivers[1:]],
        orientation="h",
        marker_color=[ACCENT if d[1] > 1.001 else OK for d in drivers[1:]],
        text=[("+" if d[1] > 1 else "") + f"{(d[1]-1)*100:.0f}%" for d in drivers[1:]],
        textposition="outside"))
    fig.add_vline(x=1.0, line_dash="dot", line_color="#AAB5B4")
    fig.update_layout(height=225, margin=dict(l=0, r=44, t=6, b=0),
                      xaxis_title=None, yaxis=dict(autorange="reversed"),
                      xaxis=dict(showticklabels=False))
    st.plotly_chart(light(fig), use_container_width=True,
                    theme=None)

    if q["was_capped"] and q["capped_total_multiplier"] >= q["band"]["cap_ceiling"]:
        st.info(f"Tonight's conditions are rough. Your price is capped at "
                f"₹{q['band']['ceiling_per_hour']:.2f} an hour — we never charge "
                "more than that, however bad the weather gets.")

with w2:
    st.markdown("**Your price range**")
    b = q["band"]
    g = go.Figure(go.Indicator(
        mode="gauge+number", value=rate,
        number={"prefix": "₹", "suffix": "/hr", "font": {"size": 30}},
        gauge={"axis": {"range": [0, b["ceiling_per_hour"] * 1.08],
                        "tickprefix": "₹"},
               "bar": {"color": PRIMARY, "thickness": 0.72},
               "steps": [
                   {"range": [0, b["floor_per_hour"]], "color": "#EEF3F2"},
                   {"range": [b["floor_per_hour"], b["base_per_hour"]],
                    "color": "#DDEBE9"},
                   {"range": [b["base_per_hour"], b["ceiling_per_hour"]],
                    "color": "#FBE7DC"}]}))
    g.update_layout(height=195, margin=dict(l=18, r=18, t=8, b=0))
    st.plotly_chart(light(g), use_container_width=True,
                    theme=None)
    st.caption(f"Best hour ₹{b['floor_per_hour']:.2f} · "
               f"worst hour ₹{b['ceiling_per_hour']:.2f}. "
               "Ride safer and in better conditions to move left.")

st.divider()

# ------------------------------------------------------------------ activity
a1, a2 = st.columns([1.25, 1])

with a1:
    st.markdown("**What you have paid, last 30 days**")
    led = store.ledger_df()
    fig2 = go.Figure(go.Bar(x=led["date"], y=led["amount"],
                            marker_color=PRIMARY,
                            hovertemplate="%{x}<br>₹%{y:.0f}<extra></extra>"))
    fig2.update_layout(height=210, margin=dict(l=0, r=0, t=6, b=0),
                       yaxis_title="₹ per day", xaxis_title=None)
    st.plotly_chart(light(fig2), use_container_width=True,
                    theme=None)
    st.caption(f"Average ₹{led['amount'].mean():.0f} a day — about "
               f"{led['amount'].mean() / r.daily_net_earnings:.1%} of a day's "
               "earnings. Debited by UPI Autopay each evening.")

with a2:
    st.markdown("**Recent claims**")
    cs = store.claims()[:4]
    if not cs:
        st.markdown("<div class='empty'>No claims yet.</div>",
                    unsafe_allow_html=True)
    for c_ in cs:
        when = datetime.fromisoformat(c_.submitted).strftime("%d %b")
        amt = inr(c_.amount_approved if c_.amount_approved else c_.amount_claimed)
        st.markdown(
            html(f"<div class='card' style='margin-bottom:.5rem;padding:.75rem .95rem'>"
            f"<div style='display:flex;justify-content:space-between;"
            f"align-items:center'><div><b style='font-size:.92rem'>{c_.incident}</b>"
            f"<div style='color:{MUTED};font-size:.78rem'>{c_.claim_id} · {when}"
            f"</div></div><div style='text-align:right'>"
            f"<div style='font-weight:800'>{amt}</div>"
            f"{badge(c_.status, CLAIM_BADGE.get(c_.status, 'mute'))}</div>"
            f"</div></div>"), unsafe_allow_html=True)
