"""
GigSure — usage-based insurance for India's gig workers.

Three products in one prototype, in the order a real business meets its
customer:

  · GigSure.com     the commercial site — what we sell, what it costs, what
                    happens when you claim, and how to sign up
  · the Rider app   what a gig worker uses to hold cover and claim on it
  · the Insurer     what the company uses to run the book: rating, claims,
    console         accumulation, solvency and capital

All three share one live state (engine/store.py) and one rating engine
(engine/pricing.py). A price quoted on the website is produced by the same
function that prices the in-force book, and buying a policy or raising a claim
on the rider side shows up immediately on the insurer side.

Navigation sits in the header, not a sidebar, because the first screen a
visitor sees has to read as a website rather than a dashboard.

Run with:  streamlit run app.py
"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

st.set_page_config(page_title="GigSure — insurance that belongs to you",
                   page_icon="🛡️", layout="wide",
                   initial_sidebar_state="collapsed")

ROOT = Path(__file__).resolve().parent
st.logo(str(ROOT / "assets" / "logo.svg"),
        icon_image=str(ROOT / "assets" / "icon.svg"), size="large")

from shared import CSS, FORCE_LIGHT  # noqa: E402

st.markdown(CSS, unsafe_allow_html=True)
st.markdown(FORCE_LIGHT, unsafe_allow_html=True)

pages = {
    "GigSure": [
        st.Page("web/home.py", title="Home", icon=":material/home:",
                default=True),
        st.Page("web/rider_shield.py", title="Rider Shield",
                icon=":material/health_and_safety:"),
        st.Page("web/ride_shield.py", title="Ride Shield",
                icon=":material/two_wheeler:"),
        st.Page("web/pricing.py", title="Pricing",
                icon=":material/schedule:"),
        st.Page("web/claims.py", title="Claims",
                icon=":material/bolt:"),
        st.Page("web/why.py", title="Why GigSure",
                icon=":material/compare_arrows:"),
        st.Page("web/trust.py", title="Trust",
                icon=":material/verified_user:"),
        st.Page("web/referral.py", title="Refer a rider",
                icon=":material/group_add:"),
        st.Page("web/register.py", title="Get covered",
                icon=":material/rocket_launch:"),
    ],
    "Rider app": [
        st.Page("views/rider_home.py", title="Home", icon=":material/dashboard:"),
        st.Page("views/rider_policies.py", title="My cover",
                icon=":material/shield:"),
        st.Page("views/rider_buy.py", title="Buy cover",
                icon=":material/add_shopping_cart:"),
        st.Page("views/rider_claims.py", title="Claims",
                icon=":material/receipt_long:"),
        st.Page("views/rider_score.py", title="My riding",
                icon=":material/speed:"),
    ],
    "Insurer console": [
        st.Page("views/ops_portfolio.py", title="Portfolio",
                icon=":material/analytics:"),
        st.Page("views/ops_underwriting.py", title="Underwriting",
                icon=":material/calculate:"),
        st.Page("views/ops_claims.py", title="Claims desk",
                icon=":material/gavel:"),
        st.Page("views/ops_risk.py", title="Risk & exposure",
                icon=":material/warning:"),
        st.Page("views/ops_finance.py", title="Finance & solvency",
                icon=":material/account_balance:"),
    ],
}

st.navigation(pages, position="top").run()
