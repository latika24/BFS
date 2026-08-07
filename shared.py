<<<<<<< HEAD
"""Shared helpers: formatting, cached data loading, and page furniture."""
from __future__ import annotations
=======
"""Design system, formatting helpers and cached data loading."""
from __future__ import annotations

>>>>>>> 03dbdc9 (Initial commit)
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.config import CFG  # noqa: E402
from engine import data_gen  # noqa: E402

<<<<<<< HEAD
PLAN = "Usage-Based Insurance for India's Gig Workers"


# ---------------------------------------------------------------- formatting
def inr(x, decimals=0):
    """Indian-format a rupee amount with thousands/lakh/crore separators."""
=======
BRAND = CFG["meta"]["product_name"]
TAGLINE = CFG["meta"]["tagline"]
SEC = CFG["sections"]

# --------------------------------------------------------------------- palette
INK = "#12211F"
PRIMARY = "#0F5C57"
PRIMARY_SOFT = "#E7F1F0"
ACCENT = "#E2653A"
ACCENT_SOFT = "#FCEDE6"
MUTED = "#6A7B79"
LINE = "#DCE5E4"
OK = "#2E7D5B"
WARN = "#B8791F"
BAD = "#B23F30"

CSS = f"""
<style>
  .block-container {{ padding-top: 1.8rem; padding-bottom: 3rem; max-width: 1380px; }}
  h1, h2, h3 {{ color: {INK}; letter-spacing: -0.015em; }}

  /* ---------- hero ---------- */
  .hero {{
    background: linear-gradient(135deg, {PRIMARY} 0%, #14746D 55%, #1C8A7E 100%);
    color: #fff; border-radius: 18px; padding: 2.2rem 2.4rem;
    margin-bottom: 1.4rem;
  }}
  .hero h1 {{ color:#fff; font-size: 2.15rem; margin: 0 0 .35rem 0; line-height:1.15; }}
  .hero .tag {{ font-size: 1.12rem; opacity: .93; margin-bottom: 1.1rem; }}
  .hero .sub {{ font-size: .95rem; opacity: .82; max-width: 66ch; line-height:1.55; }}
  .hero .chips {{ margin-top: 1.2rem; }}
  .chip {{
    display:inline-block; background: rgba(255,255,255,.15);
    border: 1px solid rgba(255,255,255,.28); color:#fff;
    padding: .3rem .75rem; border-radius: 999px; font-size: .8rem;
    margin-right: .45rem; margin-bottom: .4rem;
  }}

  /* ---------- cards ---------- */
  .card {{
    background:#fff; border:1px solid {LINE}; border-radius: 14px;
    padding: 1.15rem 1.3rem; height:100%;
  }}
  .card h4 {{ margin:.1rem 0 .5rem 0; font-size:1.02rem; color:{INK}; }}
  .card p {{ margin:0; color:{MUTED}; font-size:.88rem; line-height:1.5; }}
  .card .num {{ font-size:.78rem; color:{ACCENT}; font-weight:700;
                letter-spacing:.08em; text-transform:uppercase; }}

  /* ---------- kpi tiles ---------- */
  .kpi {{
    background:{PRIMARY_SOFT}; border:1px solid {LINE}; border-radius: 12px;
    padding: .9rem 1.05rem;
  }}
  .kpi .k {{ font-size:.74rem; color:{MUTED}; text-transform:uppercase;
             letter-spacing:.07em; margin-bottom:.25rem; }}
  .kpi .v {{ font-size:1.55rem; font-weight:700; color:{PRIMARY}; line-height:1.1; }}
  .kpi .d {{ font-size:.78rem; color:{MUTED}; margin-top:.2rem; }}

  /* ---------- pills / refs ---------- */
  .ref {{ display:inline-block; background:{PRIMARY_SOFT}; color:{PRIMARY};
          padding:.14rem .55rem; border-radius:6px; font-size:.75rem;
          font-weight:600; margin-bottom:.5rem; }}
  .pill {{ display:inline-block; padding:.16rem .6rem; border-radius:999px;
           font-size:.75rem; font-weight:600; margin-right:.3rem; }}
  .pill-fixed {{ background:#E8F2EC; color:{OK}; }}
  .pill-ind {{ background:{ACCENT_SOFT}; color:#A8481F; }}
  .pill-svc {{ background:#EEF1F6; color:#42546B; }}

  .formula {{
    background:#F5F8F8; border-left:3px solid {PRIMARY}; padding:.7rem .95rem;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size:.83rem; border-radius:4px; margin:.5rem 0 .9rem 0; color:{INK};
  }}

  /* ---------- phone mockup ---------- */
  .phone {{
    width: 320px; margin: 0 auto; background:{INK}; border-radius: 34px;
    padding: 12px; box-shadow: 0 14px 40px rgba(0,0,0,.22);
  }}
  .phone-screen {{ background:#F7FAFA; border-radius: 25px; overflow:hidden; }}
  .phone-top {{ background:{PRIMARY}; color:#fff; padding: 1rem 1.1rem .95rem; }}
  .phone-top .brand {{ font-size:.72rem; letter-spacing:.16em;
                       text-transform:uppercase; opacity:.8; }}
  .phone-top .status {{ font-size:1.28rem; font-weight:700; margin-top:.15rem; }}
  .phone-top .meta {{ font-size:.8rem; opacity:.88; margin-top:.15rem; }}
  .phone-body {{ padding: .9rem 1.1rem 1.2rem; }}
  .prow {{ display:flex; justify-content:space-between; align-items:baseline;
           padding:.5rem 0; border-bottom:1px solid #E6EDEC; }}
  .prow:last-child {{ border-bottom:none; }}
  .prow .l {{ font-size:.83rem; color:{MUTED}; }}
  .prow .r {{ font-size:.95rem; font-weight:700; color:{INK}; }}
  .live {{ display:inline-block; width:8px; height:8px; border-radius:50%;
           background:#4ADE80; margin-right:6px; }}
  .phone-cta {{ background:{ACCENT}; color:#fff; text-align:center;
                padding:.7rem; border-radius:10px; font-weight:700;
                font-size:.9rem; margin-top:.9rem; }}

  /* ---------- steps ---------- */
  .step {{ display:flex; gap:.9rem; padding:.8rem 0;
           border-bottom:1px solid {LINE}; }}
  .step:last-child {{ border-bottom:none; }}
  .step .n {{ flex:0 0 30px; height:30px; border-radius:50%;
              background:{PRIMARY}; color:#fff; font-weight:700;
              display:flex; align-items:center; justify-content:center;
              font-size:.85rem; }}
  .step .t {{ font-weight:700; color:{INK}; font-size:.94rem; }}
  .step .d {{ color:{MUTED}; font-size:.85rem; line-height:1.5; margin-top:.15rem; }}
  .step .clock {{ margin-left:auto; font-size:.78rem; color:{ACCENT};
                  font-weight:700; white-space:nowrap; }}

  /* ---------- misc ---------- */
  .quadrant td {{ padding:.9rem; border:1px solid {LINE}; vertical-align:top;
                  font-size:.85rem; }}
  .note {{ background:#FFF9EC; border-left:3px solid {WARN};
           padding:.75rem 1rem; border-radius:6px; font-size:.87rem;
           color:#5A4A22; margin:.6rem 0; }}
  [data-testid="stSidebarNav"] {{ padding-top: .5rem; }}
</style>
"""


# ------------------------------------------------------------------ formatting
def inr(x, decimals=0):
    """Indian-grouped rupee amount."""
>>>>>>> 03dbdc9 (Initial commit)
    try:
        x = float(x)
    except (TypeError, ValueError):
        return str(x)
<<<<<<< HEAD
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
=======
    neg, x = x < 0, abs(x)
    s = f"{x:,.{decimals}f}"
    whole, frac = (s.split(".") + [""])[:2]
    frac = "." + frac if frac else ""
    whole = whole.replace(",", "")
    if len(whole) > 3:
        last3, rest = whole[-3:], whole[:-3]
>>>>>>> 03dbdc9 (Initial commit)
        parts = []
        while len(rest) > 2:
            parts.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            parts.insert(0, rest)
        whole = ",".join(parts) + "," + last3
    out = f"₹{whole}{frac}"
<<<<<<< HEAD
    return ("-" + out) if neg else out
=======
    return ("−" + out) if neg else out
>>>>>>> 03dbdc9 (Initial commit)


def crore(x, decimals=0):
    return f"₹{x / 1e7:,.{decimals}f} cr"


def lakh(x, decimals=1):
    return f"₹{x / 1e5:,.{decimals}f} lakh"


<<<<<<< HEAD
def pct(x, decimals=1):
    return f"{x * 100:.{decimals}f}%"


# ---------------------------------------------------------------- data
=======
# ------------------------------------------------------------------ data
>>>>>>> 03dbdc9 (Initial commit)
@st.cache_data(show_spinner=False)
def riders(n=None):
    return data_gen.generate_riders(n=n)


@st.cache_data(show_spinner=False)
def trips(n_riders=800):
    return data_gen.generate_trips(riders().head(n_riders))


@st.cache_data(show_spinner=False)
def claims():
    return data_gen.simulate_claims(riders())


<<<<<<< HEAD
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
=======
# ------------------------------------------------------------------ components
def page_setup(title):
    st.set_page_config(page_title=f"{BRAND} · {title}", page_icon="🛵",
                       layout="wide", initial_sidebar_state="expanded")
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title, tagline, sub="", chips=()):
    chip_html = "".join(f"<span class='chip'>{c}</span>" for c in chips)
    st.markdown(
        f"""<div class='hero'>
              <h1>{title}</h1>
              <div class='tag'>{tagline}</div>
              <div class='sub'>{sub}</div>
              <div class='chips'>{chip_html}</div>
            </div>""",
        unsafe_allow_html=True)


def page_header(title, ref, sub=""):
    st.markdown(f"<div class='ref'>{ref}</div>", unsafe_allow_html=True)
    st.markdown(f"## {title}")
    if sub:
        st.markdown(f"<div style='color:{MUTED};font-size:.95rem;"
                    f"margin-top:-.4rem;margin-bottom:.9rem;max-width:80ch'>"
                    f"{sub}</div>", unsafe_allow_html=True)


def kpi(col, label, value, delta=""):
    col.markdown(
        f"""<div class='kpi'><div class='k'>{label}</div>
            <div class='v'>{value}</div>
            <div class='d'>{delta}</div></div>""",
        unsafe_allow_html=True)


def card(col, num, title, body):
    col.markdown(
        f"""<div class='card'><div class='num'>{num}</div>
            <h4>{title}</h4><p>{body}</p></div>""",
        unsafe_allow_html=True)


def ref(text):
>>>>>>> 03dbdc9 (Initial commit)
    st.markdown(f"<div class='ref'>{text}</div>", unsafe_allow_html=True)


def formula(text):
    st.markdown(f"<div class='formula'>{text}</div>", unsafe_allow_html=True)


<<<<<<< HEAD
def how_it_works(title, body):
    with st.expander(f"How this works — {title}"):
        st.markdown(body)
=======
def note(text):
    st.markdown(f"<div class='note'>{text}</div>", unsafe_allow_html=True)


def steps(items):
    """items: list of (title, detail, timing)."""
    html = ""
    for i, (t, d, clock) in enumerate(items, 1):
        html += (f"<div class='step'><div class='n'>{i}</div>"
                 f"<div><div class='t'>{t}</div><div class='d'>{d}</div></div>"
                 f"<div class='clock'>{clock}</div></div>")
    st.markdown(html, unsafe_allow_html=True)


def note_ref(text):
    """Small section pointer back to the business plan."""
    st.markdown(f"<div class='ref'>{text}</div>", unsafe_allow_html=True)
>>>>>>> 03dbdc9 (Initial commit)
