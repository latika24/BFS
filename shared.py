"""Shared helpers: formatting, cached data loading, and page furniture."""
from __future__ import annotations
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.config import CFG  # noqa: E402
from engine import data_gen  # noqa: E402

PLAN = "Usage-Based Insurance for India's Gig Workers"


# ---------------------------------------------------------------- formatting
def inr(x, decimals=0):
    """Indian-format a rupee amount with thousands/lakh/crore separators."""
    try:
        x = float(x)
    except (TypeError, ValueError):
        return str(x)
    neg = x < 0
    x = abs(x)
    s = f"{x:,.{decimals}f}"
    # convert western grouping to Indian grouping
    if "." in s:
        whole, frac = s.split(".")
        frac = "." + frac
    else:
        whole, frac = s, ""
    whole = whole.replace(",", "")
    if len(whole) > 3:
        last3 = whole[-3:]
        rest = whole[:-3]
        parts = []
        while len(rest) > 2:
            parts.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            parts.insert(0, rest)
        whole = ",".join(parts) + "," + last3
    out = f"₹{whole}{frac}"
    return ("-" + out) if neg else out


def crore(x, decimals=0):
    return f"₹{x / 1e7:,.{decimals}f} cr"


def lakh(x, decimals=1):
    return f"₹{x / 1e5:,.{decimals}f} lakh"


def pct(x, decimals=1):
    return f"{x * 100:.{decimals}f}%"


# ---------------------------------------------------------------- data
@st.cache_data(show_spinner=False)
def riders(n=None):
    return data_gen.generate_riders(n=n)


@st.cache_data(show_spinner=False)
def trips(n_riders=800):
    return data_gen.generate_trips(riders().head(n_riders))


@st.cache_data(show_spinner=False)
def claims():
    return data_gen.simulate_claims(riders())


# ---------------------------------------------------------------- furniture
def page_setup(title, icon="•"):
    st.set_page_config(page_title=f"{title} — UBI Gig", page_icon="🛵",
                       layout="wide", initial_sidebar_state="expanded")
    st.markdown(
        """
        <style>
          .block-container {padding-top: 2.2rem; max-width: 1400px;}
          [data-testid="stMetricValue"] {font-size: 1.6rem;}
          .formula {background:#f4f4f6; border-left:3px solid #999;
                    padding:0.6rem 0.9rem; font-family: ui-monospace, monospace;
                    font-size:0.86rem; border-radius:3px; margin:0.4rem 0 0.8rem 0;}
          .ref {color:#666; font-size:0.82rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def section_ref(text):
    """Small grey pointer back to the business plan."""
    st.markdown(f"<div class='ref'>{text}</div>", unsafe_allow_html=True)


def formula(text):
    st.markdown(f"<div class='formula'>{text}</div>", unsafe_allow_html=True)


def how_it_works(title, body):
    with st.expander(f"How this works — {title}"):
        st.markdown(body)
