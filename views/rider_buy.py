"""Rider app — buy cover. Product catalogue, premium calculator, checkout."""
from __future__ import annotations

import time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from shared import (html, topbar, h, kpi, inr, lakh, rows, badge, MUTED, PRIMARY,
                    ACCENT, OK, LINE, note)
from engine import store, pricing, sum_insured as si_engine
from engine.config import CFG

r = store.rider()
topbar("Rider app", f"{r.name} · {r.rider_id}")

h("Buy cover",
  "Pick a plan, see what it costs you — not a list price, your price, based on "
  "the hours you actually ride.")

TIERS = CFG["tiers"]
FEATURES = [
    ("Death & permanent disability", ["GigSure Basic", "GigSure Plus", "GigSure Pro"]),
    ("Ambulance & first response", ["GigSure Basic", "GigSure Plus", "GigSure Pro"]),
    ("Broken bone benefit", ["GigSure Basic", "GigSure Plus", "GigSure Pro"]),
    ("Daily income while you cannot ride", ["GigSure Plus", "GigSure Pro"]),
    ("Hospital daily cash", ["GigSure Plus", "GigSure Pro"]),
    ("Legal help after an FIR", ["GigSure Plus", "GigSure Pro"]),
    ("Your bike, damaged on shift", ["GigSure Pro"]),
    ("Orders you get charged for", ["GigSure Pro"]),
    ("Phone screen", ["GigSure Pro"]),
]

# ------------------------------------------------------------- calculator
st.markdown("#### Your price")
cc = st.columns([1, 1, 1, 1])
hours_pm = cc[0].slider("Hours you ride a month", 20, 280,
                        int(sum(x["hours"] for x in store.store()["ledger"])), 10)
city = cc[1].selectbox("Where you ride", list(CFG["city"].keys()),
                       index=list(CFG["city"]).index(r.city))
plat = cc[2].selectbox("Mostly for", list(CFG["platform"].keys()),
                       index=list(CFG["platform"]).index(r.platform))
shift_len = cc[3].slider("Typical shift length", 3.0, 12.0, 8.0, 0.5)

days_pm = max(1, round(hours_pm / shift_len))


def price_for(tier):
    prof = pricing.RiderProfile(
        age=r.age, city=city, vehicle=r.vehicle, platform=plat,
        tenure_months=r.tenure_months, safety_score=r.safety_score,
        sum_insured=TIERS[tier]["sum_insured_reference"], tier=tier)
    sh = pricing.ShiftContext(hours=shift_len, time_band="16:00-19:00",
                              weather="Clear", days_per_month=days_pm)
    return pricing.quote(prof, sh)


quotes = {t: price_for(t) for t in TIERS}

st.write("")
cols = st.columns(len(TIERS) + 1)
choice_key = "buy_tier"
if choice_key not in st.session_state:
    st.session_state[choice_key] = "GigSure Plus"

for i, (tier, meta) in enumerate(TIERS.items()):
    q = quotes[tier]
    sel = st.session_state[choice_key] == tier
    feats = ""
    for label, tiers_with in FEATURES:
        has = tier in tiers_with
        feats += (f"<li class='{'' if has else 'no'}'>"
                  f"{'✓' if has else '—'} {label}</li>")
    with cols[i]:
        st.markdown(
            html(f"""<div class='plan {'sel' if sel else ''}'>
                  <div class='nm'>{tier.replace('GigSure ', '')}</div>
                  <div class='pr'>₹{q['premium_per_hour']:.2f}</div>
                  <div class='pu'>per hour you ride · about
                       <b>{inr(q['premium_month'])}</b>/month at {hours_pm} hrs</div>
                  <div style='margin-top:.5rem;font-size:.8rem;color:{MUTED}'>
                       Cover up to {lakh(meta['sum_insured_reference'])}</div>
                  <ul>{feats}</ul>
                </div>"""), unsafe_allow_html=True)
        if st.button("Selected" if sel else "Choose", key=f"pick{tier}",
                     width="stretch", type="primary" if sel else "secondary"):
            st.session_state[choice_key] = tier
            st.rerun()

with cols[-1]:
    sp = CFG["shift_pass"]
    st.markdown(
        html(f"""<div class='plan'>
              <div class='nm'>Shift Pass</div>
              <div class='pr'>₹{sp['price']}</div>
              <div class='pu'>for one {sp['hours']}-hour shift · no commitment</div>
              <div style='margin-top:.5rem;font-size:.8rem;color:{MUTED}'>
                   Cover up to {lakh(TIERS['GigSure Basic']['sum_insured_reference'])}</div>
              <ul><li>✓ Death & disability</li><li>✓ Ambulance</li>
                  <li>✓ Broken bone benefit</li>
                  <li class='no'>— Income cover</li>
                  <li class='no'>— Bike & orders</li></ul>
            </div>"""), unsafe_allow_html=True)
    st.button("Buy a single shift", key="shiftpass", width="stretch")

tier = st.session_state[choice_key]
q = quotes[tier]

st.write("")
note(f"You ride about <b>{hours_pm} hours a month</b>. On {tier} that is "
     f"<b>{inr(q['premium_month'])} a month</b> — around "
     f"<b>₹{q['premium_month']/days_pm:.0f} on a working day</b>, roughly "
     f"{(q['premium_month']/days_pm)/r.daily_net_earnings:.1%} of a day's "
     "earnings. Debited daily, never as a lump sum.")

st.divider()

# ------------------------------------------------------------- what you get
h("What this plan pays you", "Amounts are worked out from your observed "
  "earnings, so they are yours specifically.")

ben = si_engine.full_schedule(r.monthly_net_earnings)
g1, g2 = st.columns([1, 1])

with g1:
    incl = [f for f, t in FEATURES if tier in t]
    body = []
    if "Death & permanent disability" in incl:
        body.append(("If you die or are permanently disabled",
                     f"<b>{inr(ben['accidental_death']['value'])}</b>"))
    if "Daily income while you cannot ride" in incl:
        body.append(("Every day you cannot ride",
                     f"<b>{inr(ben['daily_income_benefit']['value'])}</b>"))
    if "Hospital daily cash" in incl:
        body.append(("Every day in hospital",
                     inr(ben["fixed"]["hospital_daily_cash"])))
    if "Broken bone benefit" in incl:
        body.append(("Broken bone",
                     f"{inr(ben['fixed']['fracture_range'][0])}–"
                     f"{inr(ben['fixed']['fracture_range'][1])}"))
    if "Ambulance & first response" in incl:
        body.append(("Ambulance", f"up to {inr(ben['fixed']['ambulance_network_cap'])}"))
    if "Your bike, damaged on shift" in incl:
        body.append(("Bike repair, per event", inr(ben["vehicle"]["per_event"])))
    if "Orders you get charged for" in incl:
        body.append(("An order deducted from your pay", "The exact amount"))
    if "Phone screen" in incl:
        body.append(("Phone screen", "Repaired at our network"))
    if "Legal help after an FIR" in incl:
        body.append(("Legal help", "Panel lawyer"))
    st.markdown(f"<div class='card'>{rows(body)}</div>", unsafe_allow_html=True)

with g2:
    st.markdown("**Compared with a normal annual policy**")
    flat = CFG["portfolio"]["gwp_per_worker"]
    mine = q["premium_year"]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=["A normal annual policy", f"{tier}, your usage"],
                         y=[flat, mine],
                         marker_color=["#C9D6D4", PRIMARY],
                         text=[inr(flat), inr(mine)], textposition="outside"))
    fig.update_layout(height=250, margin=dict(l=0, r=0, t=28, b=0),
                      yaxis_title="A year of cover (₹)", showlegend=False)
    st.plotly_chart(fig, width="stretch")
    diff = flat - mine
    if diff > 0:
        st.success(f"You save **{inr(diff)} a year** because you ride "
                   f"{hours_pm} hours a month, not 208. A flat premium would "
                   "charge you for someone else's exposure.")
    else:
        st.info(f"You ride more than average, so usage pricing costs "
                f"**{inr(-diff)} more** — and covers you properly for it. A "
                "flat premium would be underpricing your real risk.")

st.divider()

# ------------------------------------------------------------- add-ons
h("Add-ons")
a = st.columns(3)
addons = []
if a[0].checkbox("Family top-up — extend hospital cash and life cover to your "
                 "spouse and children (+₹0.40/hr)"):
    addons.append("Family top-up")
if a[1].checkbox("Phone screen & theft (+₹0.25/hr)",
                 value=(tier == "GigSure Pro")):
    addons.append("Phone screen")
if a[2].checkbox("EV battery cover (+₹0.35/hr)"):
    addons.append("EV battery")

addon_rate = 0.40 * ("Family top-up" in addons) + \
             0.25 * ("Phone screen" in addons and tier != "GigSure Pro") + \
             0.35 * ("EV battery" in addons)
final_hr = q["premium_per_hour"] + addon_rate
final_month = final_hr * hours_pm

st.divider()

# ------------------------------------------------------------- checkout
h("Confirm and activate")

ch1, ch2 = st.columns([1, 1.1])

with ch1:
    _order = rows([
        ("Plan", "<b>%s</b>" % tier),
        ("Add-ons", ", ".join(addons) if addons else "—"),
        ("Rate", "₹%.2f per active hour" % final_hr),
        ("Estimated monthly",
         "<b style='color:%s;font-size:1.05rem'>%s</b>" % (PRIMARY,
                                                           inr(final_month))),
        ("Billed", "Daily by UPI Autopay, only for hours you ride"),
        ("Lock-in", "None — cancel any time"),
    ])
    st.markdown(html("<div class='card'><h4 style='margin-bottom:.6rem'>Your order"
                "</h4>%s</div>" % _order), unsafe_allow_html=True)

with ch2:
    st.markdown("**Three steps, about ninety seconds**")
    s1 = st.checkbox(f"Aadhaar KYC — verified via DigiLocker "
                     f"{'✓' if r.kyc_done else ''}", value=r.kyc_done)
    s2 = st.checkbox(f"Vehicle {r.vehicle_reg} and licence confirmed from VAHAN "
                     "and Sarathi", value=True)
    s3 = st.checkbox("UPI Autopay mandate — up to ₹60 a day, cancel any time",
                     value=False)
    s4 = st.checkbox("Share riding data so my price reflects how I actually "
                     "ride (you can withdraw this any time and keep your cover)",
                     value=True)

    ready = s1 and s2 and s3
    if not ready:
        st.caption("Tick all three to activate.")

    if st.button(f"Activate {tier} — ₹{final_hr:.2f}/hr", type="primary",
                 width="stretch", disabled=not ready):
        with st.status("Issuing your policy…", expanded=True) as status:
            st.write("Verifying identity and vehicle…")
            time.sleep(0.4)
            st.write("Registering UPI Autopay mandate…")
            time.sleep(0.4)
            st.write("Filing the policy…")
            time.sleep(0.4)
            p = store.buy_policy(tier, addons)
            r.telematics_consent = s4
            status.update(label=f"Policy {p.policy_id} is live", state="complete")
        st.balloons()
        st.success(f"**You are covered.** Policy {p.policy_id} is active from "
                   "now. Cover switches on the moment you start riding — on any "
                   "app. See it under **My cover**.")
