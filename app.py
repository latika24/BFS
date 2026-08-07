"""
Suraksha — usage-based insurance for India's gig workers.
Proof-of-concept product site and pricing engine.

Run with:  streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

from shared import (page_setup, hero, kpi, card, inr, crore, note,
                    BRAND, TAGLINE, SEC, MUTED, PRIMARY)
from engine.config import CFG
from engine import pricing, portfolio

page_setup("Home")

hero(
    "Suraksha",
    TAGLINE,
    "Cover that switches on when a rider starts working — on whichever app — "
    "priced by the hour actually ridden, and settled inside a day. Built for "
    "India's 1.2 crore gig workers, 77.6% of whom earn under ₹2.5 lakh a year "
    "and cannot pay an annual premium of any size.",
    chips=["₹15–30 a day by UPI Autopay", "Cover follows the worker, not the app",
           "Income replaced while you cannot ride", "Claims paid in under a day"],
)

# ------------------------------------------------------------------ KPIs
traj = portfolio.trajectory()
final = traj.iloc[-1]
bc = portfolio.burning_cost()
ref_cfg = CFG["reference_rider"]
r = pricing.RiderProfile(age=ref_cfg["age"], city=ref_cfg["city"],
                         vehicle=ref_cfg["vehicle"], platform=ref_cfg["platform"],
                         safety_score=ref_cfg["safety_score"],
                         sum_insured=ref_cfg["sum_insured"])
s = pricing.ShiftContext(hours=ref_cfg["hours_per_shift"],
                         time_band=ref_cfg["time_band"], weather=ref_cfg["weather"],
                         days_per_month=ref_cfg["days_per_month"])
q = pricing.quote(r, s)
band = q["band"]

k1, k2, k3, k4 = st.columns(4)
kpi(k1, "Price band, Suraksha Plus",
    f"₹{band['floor_per_hour']:.2f}–{band['ceiling_per_hour']:.2f}",
    "per active hour, inside the governance band")
kpi(k2, "Typical daily debit", f"₹{q['premium_shift']:.0f}",
    "an 8-hour shift in fair weather")
kpi(k3, "Addressable riders", "42 lakh",
    "primary + secondary segments")
kpi(k4, "Underwriting break-even", "Year 7",
    f"at {final['Active workers']:,.0f} covered workers")

st.write("")

# ------------------------------------------------------------------ the gap
st.markdown("### The gap we are solving")
st.markdown(
    f"<div style='color:{MUTED};max-width:88ch;margin-bottom:1rem'>"
    "Gig workers in India are not uninsured — Eternal spent roughly ₹100 crore "
    "on delivery-partner premiums in a single year, Acko covers close to a "
    "million riders through platform tie-ups, and the state offers PMSBY at ₹20 "
    "a year. The cover exists. It fails in four specific ways.</div>",
    unsafe_allow_html=True)

g1, g2, g3, g4 = st.columns(4)
card(g1, "Gap 01", "It belongs to a platform, not a person",
     "Live only while the worker is logged in to that app. Roughly 40% of a "
     "rider's day is spent multi-homing, and that time falls between two policies.")
card(g2, "Gap 02", "It insures the event, not the livelihood",
     "Death is rare. Six weeks off the road with a fractured wrist is common, "
     "and ruinous on ₹22,000 a month with no savings. Almost nobody covers it.")
card(g3, "Gap 03", "The vehicle cover is quietly void",
     "Most riders use a privately-registered two-wheeler commercially. Every "
     "private policy excludes commercial use, so it will not pay for a crash at work.")
card(g4, "Gap 04", "It is slow to pay",
     "Unions in Telangana and Karnataka have documented injured riders waiting "
     "months. Where nobody trusts an insurer to pay, speed is the product.")

st.write("")
st.divider()

# ------------------------------------------------------------------ nav
st.markdown("### Explore the proof of concept")

n1, n2, n3 = st.columns(3)
card(n1, "01 · Rider App", "What the worker actually sees",
     "The phone view: cover live right now, hours ridden today, what it has "
     "cost, safety score and what would lower it.")
card(n2, "02 · Pricing Engine", "Price any rider, any hour",
     "Move the exposure controls and watch the premium move. Shows the full "
     "derivation and the governance band that keeps it affordable.")
card(n3, "03 · Cover & Benefits", "Benefits sized from observed earnings",
     "Death benefit, income benefit, vehicle and consignment limits — all "
     "calculated, none chosen from a menu. With the settlement basis for each.")

st.write("")
n4, n5, n6 = st.columns(3)
card(n4, "04 · Claims Journey", "One tap to money in the account",
     "The 60-second fixed-benefit settlement, step by step, and why holding the "
     "telematics trace is what makes it possible.")
card(n5, "05 · Market & Strategy", "Who we target and why",
     "Segment sizing across the 1.2 crore workforce, and the competitive "
     "quadrant our largest competitor structurally cannot enter.")
card(n6, "06 · Portfolio & Risk", "The book, years 1 to 7",
     "Premium, loss ratio, expense ratio, solvency — with the stress cases "
     "where the plan fails.")

st.write("")
st.divider()

# ------------------------------------------------------------------ reconcile
with st.expander("Model calibration — how to check these numbers against the report"):
    blended = q["premium_per_hour"] * ref_cfg["blended_book_hours_per_month"] * 12
    st.markdown("Every figure the engine produces is checked against a published "
                "number in the business plan, so nothing here has to be taken on trust.")
    st.dataframe({
        "Figure": [
            "Suraksha Plus, base rate per active hour",
            "Suraksha Plus, price band under the governance cap",
            "Full-time rider, monthly premium",
            "Book-average premium per active worker per year",
            "Expected claim cost per rider-year",
            "Year 7 combined ratio",
            "Underwriting break-even",
        ],
        "Plan says": [
            f"₹2.50 ({SEC['marketing_mix']})",
            f"₹1.50–₹5.50 ({SEC['marketing_mix']})",
            "₹520",
            f"₹5,400 ({SEC['monetization']})",
            "₹3,148",
            f"95% ({SEC['breakeven']})",
            f"Year 7 ({SEC['breakeven']})",
        ],
        "Engine produces": [
            f"₹{band['base_per_hour']:.2f}",
            f"₹{band['floor_per_hour']:.2f}–₹{band['ceiling_per_hour']:.2f}",
            inr(q["premium_month"]),
            inr(blended),
            inr(bc["per_rider"]),
            f"{final['Combined ratio']:.0%}",
            f"Year {portfolio.breakeven_year(traj)}",
        ],
    }, width="stretch", hide_index=True)

    st.markdown(
        "**A reconciliation worth understanding.** The plan prices Suraksha Plus "
        "at ₹2.50 per active hour with a full-time rider at ~208 hours a month — "
        "that is ₹6,240 a year. It also uses ₹5,400 of premium per active worker. "
        "Both hold: ₹5,400 is the blended average across a book that includes "
        "part-time and Shift Pass riders, implying about 180 active hours a "
        "month. The Pricing Engine prices an individual; the Portfolio page uses "
        "the book average.")

    note(f"<b>One discrepancy found in the report.</b> {CFG['portfolio']['funding_note']}")

    st.markdown(
        "**On the data.** Every rider shown in this proof of concept is "
        "synthetic, generated by `engine/data_gen.py` with a fixed seed. There "
        "is no public gig-worker telematics dataset. Distributions match the "
        "plan — about a quarter of workers ride more than eight hours a day, "
        "about a third work purely in free time — and claim frequencies come "
        "from the burning cost table. Nothing here is fitted to real loss "
        "experience; these are prior estimates for a pilot.")

st.caption("Use the sidebar to move between pages. "
           "All rating factors live in `config/rating_factors.yaml`.")
