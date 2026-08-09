"""Rider app — my riding: score, exposure, and how to pay less."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from shared import (light, topbar, h, kpi, inr, rows, MUTED, PRIMARY, ACCENT, OK,
                    BAD, note)
from engine import store, safety_score as ss, pricing
from engine.config import CFG

r = store.rider()
pols = store.active_policies()
topbar("Rider app", f"{r.name} · {r.rider_id}")

h("My riding",
  "Your price moves with how and when you ride. Nothing here is hidden from "
  "you — this is exactly what our pricing engine sees.")

# ------------------------------------------------------------------ score
tel = ss.default_inputs("average")
tel["harsh_braking"] = st.session_state.get("t_brake", 9.0)
tel["screen_on_while_moving"] = st.session_state.get("t_screen", 7.0)
tel["over_speeding"] = st.session_state.get("t_speed", 12.0)
tel["night_riding_share"] = st.session_state.get("t_night", 22.0)
score = ss.compute(tel)
r.safety_score = score["score"]

k = st.columns(4)
kpi(k[0], "Safety score", f"{score['score']:.0f}", f"band {score['band']}")
kpi(k[1], "Effect on your price", f"×{score['multiplier']:.2f}",
    "better score, lower price")
hrs_month = sum(x["hours"] for x in store.store()["ledger"])
kpi(k[2], "Hours ridden", f"{hrs_month:.0f}", "last 30 days")
kpi(k[3], "Observed earnings", inr(r.monthly_net_earnings),
    "read from your bank, with consent")

st.write("")
g1, g2 = st.columns([1, 1.35])

with g1:
    gauge = go.Figure(go.Indicator(
        mode="gauge+number", value=score["score"],
        number={"suffix": " / 100", "font": {"size": 36}},
        gauge={"axis": {"range": [0, 100]},
               "bar": {"color": PRIMARY, "thickness": 0.74},
               "steps": [{"range": [0, 50], "color": "#F7DED8"},
                         {"range": [50, 70], "color": "#FBEEDD"},
                         {"range": [70, 90], "color": "#E4F0E9"},
                         {"range": [90, 100], "color": "#CDE8DA"}]}))
    gauge.update_layout(height=250, margin=dict(l=20, r=20, t=14, b=0))
    st.plotly_chart(light(gauge), use_container_width=True,
                    theme=None)
    st.caption("Shown to you for three months before it affects your price, "
               "so you can see it is fair before it costs you anything.")

with g2:
    st.markdown("**What is costing you points**")
    contrib = sorted(score["contributions"].values(),
                     key=lambda c: c["points_lost"], reverse=True)
    fig = go.Figure(go.Bar(
        x=[c["points_lost"] for c in contrib],
        y=[c["label"] for c in contrib], orientation="h",
        marker_color=[ACCENT if c["points_lost"] > 4 else "#9FB3B0"
                      for c in contrib],
        text=[f"−{c['points_lost']:.1f}" for c in contrib],
        textposition="outside"))
    fig.update_layout(height=290, margin=dict(l=0, r=34, t=6, b=0),
                      xaxis_title="points lost",
                      yaxis=dict(autorange="reversed"))
    st.plotly_chart(light(fig), use_container_width=True,
                    theme=None)

st.divider()

# ------------------------------------------------------------------ what if
h("What would happen if you changed one thing",
  "Move a slider and watch your price change. This is not a projection — it is "
  "the live rating engine.")

w = st.columns(4)
st.session_state["t_brake"] = w[0].slider("Hard braking / 100 km", 0.0, 25.0,
                                          float(tel["harsh_braking"]), 0.5)
st.session_state["t_screen"] = w[1].slider("Phone in hand while moving (%)",
                                           0.0, 20.0,
                                           float(tel["screen_on_while_moving"]), 0.5)
st.session_state["t_speed"] = w[2].slider("Over the limit (% of distance)",
                                          0.0, 30.0, float(tel["over_speeding"]), 0.5)
st.session_state["t_night"] = w[3].slider("Riding after 11pm (%)", 0.0, 60.0,
                                          float(tel["night_riding_share"]), 1.0)

new_tel = dict(tel)
new_tel.update(harsh_braking=st.session_state["t_brake"],
               screen_on_while_moving=st.session_state["t_screen"],
               over_speeding=st.session_state["t_speed"],
               night_riding_share=st.session_state["t_night"])
new_score = ss.compute(new_tel)

tier = pols[0].tier if pols else "GigSure Plus"
si = CFG["tiers"][tier]["sum_insured_reference"]


def month_cost(sc):
    prof = pricing.RiderProfile(age=r.age, city=r.city, vehicle=r.vehicle,
                                platform=r.platform,
                                tenure_months=r.tenure_months,
                                safety_score=sc, sum_insured=si, tier=tier)
    sh = pricing.ShiftContext(hours=8.0, time_band="16:00-19:00",
                              weather="Clear",
                              days_per_month=max(1, round(hrs_month / 8)))
    return pricing.quote(prof, sh)["premium_month"]


now_cost = month_cost(74.0)
new_cost = month_cost(new_score["score"])
best_cost = month_cost(95.0)

r1, r2, r3 = st.columns(3)
kpi(r1, "Your score now", f"{new_score['score']:.0f}",
    f"band {new_score['band']}")
kpi(r2, "Monthly premium", inr(new_cost),
    ("saves " + inr(now_cost - new_cost) if new_cost < now_cost
     else "costs " + inr(new_cost - now_cost) + " more") if abs(new_cost - now_cost) > 1
    else "unchanged")
kpi(r3, "If you scored 95", inr(best_cost),
    f"you'd save {inr(new_cost - best_cost)} a month")

if new_score["score"] > 74:
    st.success(f"**Ride like this for 30 days and your premium falls to "
               f"{inr(new_cost)} a month.** Biggest win available to you right "
               f"now: {new_score['biggest_opportunity'].lower()}.")
else:
    st.warning(f"At this score your premium is {inr(new_cost)} a month. Fixing "
               f"{new_score['biggest_opportunity'].lower()} moves it most.")

st.divider()

# ------------------------------------------------------------------ exposure
h("When you ride", "Your exposure is not just how long you ride — it is when. "
  "An hour at 10pm in heavy rain carries about 2.2 times the risk of the same "
  "hour at 11am in the dry, and it is priced that way.")

e1, e2 = st.columns([1.3, 1])

with e1:
    bands = list(CFG["time_of_day"].keys())
    rng = np.random.default_rng(11)
    share = np.array([0.13, 0.19, 0.28, 0.29, 0.11])
    hrs = share * hrs_month
    fig2 = go.Figure(go.Bar(
        x=bands, y=hrs,
        marker_color=[ACCENT if CFG["time_of_day"][b] > 1.1 else PRIMARY
                      for b in bands],
        text=[f"×{CFG['time_of_day'][b]:.2f}" for b in bands],
        textposition="outside"))
    fig2.update_layout(height=280, margin=dict(l=0, r=0, t=26, b=0),
                       yaxis_title="hours ridden", xaxis_title=None)
    st.plotly_chart(light(fig2), use_container_width=True,
                    theme=None)
    st.caption("Orange bands are priced above the standard rate. Shifting even "
               "a few hours earlier is the fastest way to cut your bill.")

with e2:
    night_h = hrs[3] + hrs[4]
    day_h = hrs_month - night_h
    _rows1 = rows([
      ('Hours in daytime bands', f"{day_h:.0f} hrs"),
      ('Hours in evening and night bands', f"{night_h:.0f} hrs"),
      ('Share of your riding at premium rates',
       f"<b>{night_h/hrs_month:.0%}</b>" if hrs_month else "—"),
      ('If you moved 10 night hours to mornings',
       f"<b style='color:{OK}'>save about "
       f"{inr(10 * (CFG['time_of_day']['19:00-23:00'] - CFG['time_of_day']['05:00-11:00']) * 2.5)}"
       "/month</b>"),
    ])
    st.markdown(f"""<div class='card'>{_rows1}</div>""", unsafe_allow_html=True)

    st.write("")
    st.markdown("**Your data, your call**")
    consent = st.toggle("Share riding data for personalised pricing",
                        value=r.telematics_consent)
    r.telematics_consent = consent
    if not consent:
        flat = pricing.price_band(
            pricing.RiderProfile(sum_insured=si, tier=tier))["base_per_hour"]
        st.info(f"**Your cover continues, unchanged.** Pricing has reverted to "
                f"the standard rate of ₹{flat:.2f} an hour. Turning off "
                "tracking never cancels your policy and never removes a "
                "benefit — it just means we price you like everybody else.")
    else:
        st.caption("We never sell your individual score to Swiggy, Zomato or "
                   "anyone else. If a platform could see who we score as "
                   "high-risk, they would deactivate them. Only anonymous, "
                   "aggregated road-safety data ever leaves us.")
