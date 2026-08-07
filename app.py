"""
Usage-Based Insurance for India's Gig Workers
Pricing and portfolio dashboard.

Run with:  streamlit run app.py
"""
from __future__ import annotations
import streamlit as st

from shared import page_setup, inr, crore, section_ref
from engine.config import CFG
from engine import pricing, portfolio

page_setup("Overview")

st.title("Usage-Based Insurance for India's Gig Workers")
st.caption("Pricing and portfolio dashboard · companion to the business plan · "
           "all figures reconcile to the sections referenced on each page")

st.markdown(
    "**The thesis this dashboard demonstrates:** a rider working 40 hours in "
    "January and 200 hours in February has genuinely different risk in each "
    "month, and no annual premium can express that. Price on measured exposure "
    "instead, charge it daily, and the product becomes both affordable to a "
    "worker earning ₹22,000 a month and correctly priced to the insurer."
)

st.divider()

# ---------------------------------------------------------------- headline
traj = portfolio.trajectory()
final = traj.iloc[-1]
bc = portfolio.burning_cost()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Steady-state GWP per worker",
          inr(CFG["portfolio"]["gwp_per_worker"]), "book average, year 7")
c2.metric("Expected claim cost", inr(bc["per_rider"]), "per rider-year, §6.1")
c3.metric("Year 7 combined ratio", f"{final['Combined ratio']:.0%}",
          "underwriting break-even")
c4.metric("Year 7 book", crore(final["GWP"]),
          f"{final['Active workers']:,.0f} workers")

st.divider()

# ---------------------------------------------------------------- pages
st.subheader("What is in here")

left, right = st.columns(2)
with left:
    st.markdown(
        "**1 · Rider Quote**  \n"
        "Price a single rider. Move the exposure controls — hours, time of day, "
        "weather, city, safety score — and watch the premium move. Shows the "
        "full derivation, not just the answer.  \n"
        "<span class='ref'>Implements §5.1 (Effective Exposure Unit) and §5.3 "
        "(the premium function)</span>",
        unsafe_allow_html=True)
    st.markdown(
        "**3 · Portfolio Simulator**  \n"
        "The book from year 1 to year 7: GWP, loss ratio, expense ratio, "
        "combined ratio, solvency. Includes the stress cases — what happens if "
        "the loss ratio plateaus, or growth stalls at 7 lakh workers.  \n"
        "<span class='ref'>Implements §6.2, §6.4, §6.6 and §6.7</span>",
        unsafe_allow_html=True)
with right:
    st.markdown(
        "**2 · Sum Insured**  \n"
        "Cover is calculated from observed earnings, not chosen from a menu, "
        "because gig workers do not have the information to choose well. Also "
        "sets out which benefits settle as fixed benefit and which as indemnity, "
        "and the moral-hazard control on each.  \n"
        "<span class='ref'>Implements §5.4 and the §4.2/§4.3 benefit schedule</span>",
        unsafe_allow_html=True)
    st.markdown(
        "**4 · Risk Explorer**  \n"
        "The synthetic book of 5,000 riders: exposure heatmaps by hour and "
        "weather, safety score distribution, and the anti-selection problem that "
        "flat pricing creates.  \n"
        "<span class='ref'>Illustrates §3.2 and §5.5</span>",
        unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------------- calibration
st.subheader("Calibration and reconciliation")
st.markdown(
    "The engine is calibrated against a single reference rider so that its "
    "output can be checked against the published figures in the plan rather "
    "than taken on trust."
)

ref = CFG["reference_rider"]
r = pricing.RiderProfile(age=ref["age"], city=ref["city"], vehicle=ref["vehicle"],
                         platform=ref["platform"], safety_score=ref["safety_score"],
                         sum_insured=ref["sum_insured"])
s = pricing.ShiftContext(hours=ref["hours_per_shift"], time_band=ref["time_band"],
                         weather=ref["weather"], days_per_month=ref["days_per_month"])
q = pricing.quote(r, s)

blended_year = q["premium_per_hour"] * ref["blended_book_hours_per_month"] * 12

st.dataframe(
    {
        "Figure": [
            "Suraksha Plus price per active hour",
            "Full-time rider, monthly premium",
            "Book-average GWP per active worker per year",
            "Expected claim cost per rider-year",
            "Year 7 combined ratio",
            "Underwriting break-even",
        ],
        "Plan says": [
            "₹2.50 (§4.4)", "₹520 (§4.4)", "₹5,400 (§6.2)",
            "₹3,148 (§6.1)", "95% (§6.4)", "Year 7 (§6.4)",
        ],
        "Engine produces": [
            f"₹{q['premium_per_hour']:.2f}",
            inr(q["premium_month"]),
            inr(blended_year),
            inr(bc["per_rider"]),
            f"{final['Combined ratio']:.0%}",
            f"Year {portfolio.breakeven_year(traj)}",
        ],
    },
    width="stretch", hide_index=True,
)

st.info(
    "**One reconciliation worth understanding.** §4.4 prices Suraksha Plus at "
    "₹2.50 per active hour and describes a full-time rider as working ~208 hours "
    "a month — that is ₹6,240 a year. §6.2 uses ₹5,400 of GWP per active worker. "
    "Both hold: ₹5,400 is the blended average across a book that includes "
    "part-time and occasional riders, implying about 180 active hours a month "
    "rather than 208. The Rider Quote page prices an individual at the tier "
    "rate; the Portfolio page uses the book average."
)

st.divider()
with st.expander("Where the numbers come from"):
    st.markdown(
        "- **Rating factors** — every multiplier, cap, formula parameter and "
        "trajectory assumption lives in `config/rating_factors.yaml`. Nothing is "
        "hard-coded. Change that file and the whole dashboard follows.\n"
        "- **Data** — synthetic, generated by `engine/data_gen.py` with a fixed "
        "seed. There is no public gig-worker telematics dataset. Distributions "
        "are drawn to match the plan: about a quarter of workers ride more than "
        "eight hours a day, about a third work purely in free time, and claim "
        "frequencies come from the §6.1 burning cost table.\n"
        "- **Nothing here is fitted to real loss experience.** These are prior "
        "estimates for a pilot, to be replaced by a fitted GLM once roughly "
        "12 months and 2,000 claims of real data exist (§5.6)."
    )

st.caption("Select a page from the sidebar to begin.")
