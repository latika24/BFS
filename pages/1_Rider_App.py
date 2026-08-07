"""Rider App — what the worker actually sees. §1.2, §1.3, §3.2."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import plotly.graph_objects as go
import streamlit as st

from shared import (page_setup, page_header, kpi, inr, note, SEC,
                    MUTED, PRIMARY, ACCENT, OK)
from engine.config import CFG
from engine import pricing, safety_score as ss, sum_insured as si_engine

page_setup("Rider App")

page_header(
    "The Rider App",
    f"{SEC['app_as_instrument']} · {SEC['value_prop']}",
    "The app is not a distribution channel — it is the measuring instrument. "
    "Without a phone SDK recording on-duty minutes there is no exposure to "
    "price on. This is the screen a rider sees while working.")

# ------------------------------------------------------------------ controls
sb = st.sidebar
sb.header("Simulate a rider")
name = sb.text_input("Name", "Ramesh K.")
city = sb.selectbox("City", list(CFG["city"].keys()), index=0)
platform = sb.selectbox("Riding for", list(CFG["platform"].keys()), index=0)
earnings = sb.slider("Monthly net earnings (₹)", 8000, 40000, 22000, 500)
tier = sb.selectbox("Plan", list(CFG["tiers"].keys()), index=1)

sb.header("Right now")
on_duty = sb.toggle("On duty", value=True)
hours_today = sb.slider("Hours ridden today", 0.0, 12.0, 5.5, 0.5)
time_band = sb.selectbox("Time of day", list(CFG["time_of_day"].keys()), index=3)
weather = sb.selectbox("Weather", list(CFG["weather"].keys()), index=1)
profile = sb.radio("Riding style", ["safe", "average", "risky"], index=1,
                   horizontal=True)
tenure = sb.slider("Months with us", 0, 40, 8)

score = ss.compute(ss.default_inputs(profile))
si = CFG["tiers"][tier]["sum_insured_reference"]

rider = pricing.RiderProfile(age=29, city=city, vehicle="<=110cc petrol",
                             platform=platform, tenure_months=tenure,
                             safety_score=score["score"], sum_insured=si, tier=tier)
shift = pricing.ShiftContext(hours=max(hours_today, 0.5), time_band=time_band,
                             weather=weather, days_per_month=26)
q = pricing.quote(rider, shift)

per_hour = q["premium_per_hour"]
cost_today = per_hour * hours_today
sched = si_engine.full_schedule(earnings)
wallet = q["premium_month"] * CFG["portfolio"]["no_claim_wallet_pct_gwp"] * (tenure / 3.0)

# ------------------------------------------------------------------ phone
left, right = st.columns([1, 1.45])

with left:
    status = "COVER IS ON" if on_duty else "COVER IS OFF"
    dot = "<span class='live'></span>" if on_duty else ""
    meta = (f"Riding for {platform.split(' (')[0]} · {city.split(' (')[0]}"
            if on_duty else "Cover starts when you begin riding")
    cta = ("Report an accident" if on_duty else "Go on duty")

    st.markdown(f"""
    <div class='phone'><div class='phone-screen'>
      <div class='phone-top'>
        <div class='brand'>Suraksha</div>
        <div class='status'>{dot}{status}</div>
        <div class='meta'>{meta}</div>
      </div>
      <div class='phone-body'>
        <div class='prow'><span class='l'>Namaste, {name}</span>
             <span class='r'>{tier.replace('Suraksha ', '')}</span></div>
        <div class='prow'><span class='l'>Hours ridden today</span>
             <span class='r'>{hours_today:.1f} hrs</span></div>
        <div class='prow'><span class='l'>Rate for this hour</span>
             <span class='r'>₹{per_hour:.2f}</span></div>
        <div class='prow'><span class='l'>Cost today</span>
             <span class='r'>₹{cost_today:.0f}</span></div>
        <div class='prow'><span class='l'>Safety score</span>
             <span class='r'>{score['score']:.0f} / 100</span></div>
        <div class='prow'><span class='l'>No-Claim Wallet</span>
             <span class='r'>₹{wallet:,.0f}</span></div>
        <div class='prow'><span class='l'>If you cannot ride</span>
             <span class='r'>₹{sched['daily_income_benefit']['value']:,.0f}/day</span></div>
        <div class='prow'><span class='l'>Family cover</span>
             <span class='r'>₹{sched['accidental_death']['value']/1e5:.0f} lakh</span></div>
        <div class='phone-cta'>{cta}</div>
      </div>
    </div></div>""", unsafe_allow_html=True)

with right:
    st.markdown("#### What the rider is being told, and why")

    a, b = st.columns(2)
    kpi(a, "Today's cost", f"₹{cost_today:.0f}",
        f"{hours_today:.1f} hrs at ₹{per_hour:.2f}")
    kpi(b, "As a share of today's earnings",
        f"{(cost_today / max(earnings / 26, 1)):.1%}",
        f"day's earnings ≈ {inr(earnings/26)}")

    st.write("")
    st.markdown(
        f"<div style='color:{MUTED};font-size:.92rem;line-height:1.6'>"
        "<b>The number that matters is the daily one.</b> With 77.6% of gig "
        "workers earning under ₹2.5 lakh a year, ₹5,400 asked for once is "
        "unpayable while the same sum at ₹20 a day is not. Cadence is a pricing "
        "decision, not a billing one — this is why the app shows a rate per hour "
        "and a cost for today rather than an annual premium.</div>",
        unsafe_allow_html=True)

    st.write("")
    st.markdown("**Where this hour's rate came from**")
    exp = q["exposure"]
    drivers = [
        ("Base rate, " + tier, CFG["tiers"][tier]["price_per_hour"], "₹/hr"),
        ("Time of day — " + time_band, exp["m_time"], "×"),
        ("Weather — " + weather, exp["m_weather"], "×"),
        ("City — " + city.split(" (")[0], exp["m_geo"], "×"),
        ("Safety score band " + score["band"], q["multipliers"]["M_behaviour"]["value"], "×"),
    ]
    fig = go.Figure(go.Bar(
        x=[d[1] for d in drivers[1:]],
        y=[d[0] for d in drivers[1:]],
        orientation="h",
        marker_color=[ACCENT if d[1] > 1 else OK for d in drivers[1:]],
        text=[f"×{d[1]:.2f}" for d in drivers[1:]], textposition="outside",
    ))
    fig.add_vline(x=1.0, line_dash="dot", line_color="#999")
    fig.update_layout(height=230, margin=dict(l=0, r=30, t=6, b=0),
                      xaxis_title="Multiplier on the base rate",
                      yaxis=dict(autorange="reversed"), showlegend=False)
    st.plotly_chart(fig, width="stretch")

    if q["was_capped"]:
        st.warning(
            f"**The governance band is protecting this rider.** Raw conditions "
            f"give ×{q['raw_multiplier_product']:.2f}, but the band caps the "
            f"total at ×{q['capped_total_multiplier']:.2f}, holding the price at "
            f"₹{per_hour:.2f}. Beyond the band the plan declines the risk or "
            "mandates a safety intervention rather than pricing out the workers "
            "who most need cover.")

st.divider()

# ------------------------------------------------------------------ score
st.markdown("### Your safety score, and exactly what would lower your price")
st.markdown(
    f"<div style='color:{MUTED};max-width:86ch'>Published pricing factors are "
    "not a transparency gesture — the score both prices behaviour and changes "
    "it. A rider can see which input is costing them and what to fix. It is "
    "also what a regulator will ask for when it wants the rating structure "
    "justified.</div>", unsafe_allow_html=True)
st.write("")

sc1, sc2 = st.columns([1.2, 1])
with sc1:
    contrib = sorted(score["contributions"].values(),
                     key=lambda c: c["points_lost"], reverse=True)
    fig2 = go.Figure(go.Bar(
        x=[c["points_lost"] for c in contrib],
        y=[c["label"] for c in contrib], orientation="h",
        marker_color=ACCENT,
        text=[f"−{c['points_lost']:.1f}" for c in contrib], textposition="outside"))
    fig2.update_layout(height=330, margin=dict(l=0, r=34, t=6, b=0),
                       xaxis_title="Score points lost",
                       yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig2, width="stretch")

with sc2:
    gauge = go.Figure(go.Indicator(
        mode="gauge+number", value=score["score"],
        number={"suffix": " / 100", "font": {"size": 34}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": PRIMARY, "thickness": 0.75},
            "steps": [
                {"range": [0, 50], "color": "#F6DDD8"},
                {"range": [50, 70], "color": "#FBEEDD"},
                {"range": [70, 90], "color": "#E4F0E9"},
                {"range": [90, 100], "color": "#CFE8DA"},
            ],
        }))
    gauge.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=0))
    st.plotly_chart(gauge, width="stretch")
    st.markdown(
        f"<div style='text-align:center;margin-top:-1rem'>"
        f"<b>Band {score['band']}</b> → premium ×{score['multiplier']:.2f}<br>"
        f"<span style='color:{MUTED};font-size:.87rem'>Biggest opportunity: "
        f"{score['biggest_opportunity']}</span></div>", unsafe_allow_html=True)

st.divider()

# ------------------------------------------------------------------ consent
st.markdown("### The three things this design costs us")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("**Battery drain is the binding constraint**")
    st.markdown(
        f"<div style='color:{MUTED};font-size:.88rem;line-height:1.55'>An SDK "
        "consuming more than about 3% an hour gets uninstalled, and an "
        "exposure-priced insurer whose exposure tracker is not running has no "
        "product. Exposure is captured through the motion coprocessor rather "
        "than continuous GPS.</div>", unsafe_allow_html=True)
with c2:
    st.markdown("**On-duty verification is imperfect**")
    st.markdown(
        f"<div style='color:{MUTED};font-size:.88rem;line-height:1.55'>Without "
        "platform data we cannot cleanly separate delivery riding from a "
        "personal trip. Cover therefore attaches to a declared shift window "
        "supported by a route-shape classifier — and we should not pretend this "
        "is solved.</div>", unsafe_allow_html=True)
with c3:
    st.markdown("**Consent is a live dependency**")
    st.markdown(
        f"<div style='color:{MUTED};font-size:.88rem;line-height:1.55'>Location "
        "data makes us a data fiduciary under the DPDP Act, 2023. The design "
        "rule: revoking telematics consent reverts the worker to a flat book "
        "rate and <b>never lapses cover</b>. Revoking consent must not cost "
        "someone their insurance.</div>", unsafe_allow_html=True)

st.write("")
consent = st.toggle("Simulate: rider revokes telematics consent", value=False)
if consent:
    flat = q["band"]["base_per_hour"]
    st.info(
        f"**Cover continues.** Pricing reverts to the flat book rate of "
        f"₹{flat:.2f} an hour — this rider now pays "
        f"{'more' if flat > per_hour else 'less'} than their behaviour-priced "
        f"rate of ₹{per_hour:.2f}, and keeps every benefit. This is both the "
        "right thing and the thing that keeps the model defensible.")
