"""
Suraksha — usage-based insurance for India's gig workers.

Two products in one prototype:
  · the Rider App, which a gig worker uses to hold cover and claim on it
  · the Insurer Console, which the company uses to run the book

They share one live state (engine/store.py), so buying a policy or raising a
claim on the rider side shows up immediately on the insurer side.

Run with:  streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Suraksha", page_icon="🛵", layout="wide",
                   initial_sidebar_state="expanded")

from shared import CSS, PRIMARY, MUTED  # noqa: E402
from engine import store  # noqa: E402

st.markdown(CSS, unsafe_allow_html=True)

# --------------------------------------------------------------- sidebar chrome
with st.sidebar:
    st.markdown(
        f"<div style='font-size:1.25rem;font-weight:800;color:{PRIMARY};"
        f"margin-bottom:.1rem'>🛵 Suraksha</div>"
        f"<div style='font-size:.78rem;color:{MUTED};margin-bottom:.9rem'>"
        "Pay-as-you-work cover</div>", unsafe_allow_html=True)

    r = store.rider()
    pols = store.active_policies()
    m = store.claim_metrics()

    st.markdown(
        f"<div style='background:#F2F7F6;border-radius:9px;padding:.6rem .75rem;"
        f"font-size:.8rem;line-height:1.55;margin-bottom:.6rem'>"
        f"<b>{r.name}</b><br>"
        f"<span style='color:{MUTED}'>{r.rider_id} · "
        f"{len(pols)} active {'policy' if len(pols)==1 else 'policies'}<br>"
        f"{m['open']} open claim{'' if m['open']==1 else 's'}</span></div>",
        unsafe_allow_html=True)

pages = {
    "Rider app": [
        st.Page("views/rider_home.py", title="Home", icon=":material/home:",
                default=True),
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
                icon=":material/dashboard:"),
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

nav = st.navigation(pages)

with st.sidebar:
    st.divider()
    if st.button("Reset demo data", width="stretch"):
        store.reset()
        st.rerun()
    st.caption("Resets policies, claims and the ledger to their seeded state.")

nav.run()
