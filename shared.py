"""Design system, formatting and cached data for the GigSure platform."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.config import CFG  # noqa: E402
from engine import data_gen  # noqa: E402

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
LINE = "#DDE6E5"
OK = "#2E7D5B"
OK_SOFT = "#E6F2EB"
WARN = "#B8791F"
WARN_SOFT = "#FDF3E2"
BAD = "#B23F30"
BAD_SOFT = "#FAEBE8"

CSS = f"""
<style>
  .block-container {{ padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1440px; }}
  h1,h2,h3,h4 {{ color:{INK}; letter-spacing:-0.015em; }}
  hr {{ border-color:{LINE}; }}

  /* ---------- top bar ---------- */
  /* ---------- top bar ----------
     One block element, inline children, floats instead of flex.
     Flex + nested <div>s did not survive Streamlit's markdown pipeline:
     the right-hand block escaped the bar and rendered above it. Floats with
     a clearfix need no height negotiation and cannot do that. */
  .topbar {{
    background:{PRIMARY}; color:#fff; border-radius:12px;
    padding:.85rem 1.2rem; margin:0 0 1.1rem 0;
    line-height:1.6; font-size:.85rem;
  }}
  .topbar::after {{ content:""; display:table; clear:both; }}
  .topbar .logo {{ float:left; font-weight:800; font-size:1.05rem;
                   letter-spacing:-.02em; white-space:nowrap;
                   margin-right:.6rem; line-height:1.6; }}
  .topbar .mode {{ float:left; background:rgba(255,255,255,.16);
                   border:1px solid rgba(255,255,255,.3);
                   padding:.1rem .6rem; border-radius:999px; font-size:.7rem;
                   text-transform:uppercase; letter-spacing:.1em;
                   white-space:nowrap; margin-top:.22rem; }}
  .topbar .tb-right {{ float:right; text-align:right; opacity:.93;
                       white-space:nowrap; }}

  /* ---------- generic surfaces ---------- */
  .card {{ background:#fff; border:1px solid {LINE}; border-radius:14px;
           padding:1.05rem 1.2rem; height:100%; }}
  .card h4 {{ margin:.1rem 0 .45rem 0; font-size:1rem; }}
  .card p {{ margin:0; color:{MUTED}; font-size:.87rem; line-height:1.5; }}
  .card .num {{ font-size:.75rem; color:{ACCENT}; font-weight:700;
                letter-spacing:.08em; text-transform:uppercase; }}

  .kpi {{ background:#fff; border:1px solid {LINE}; border-left:4px solid {PRIMARY};
          border-radius:10px; padding:.8rem 1rem; }}
  .kpi .k {{ font-size:.72rem; color:{MUTED}; text-transform:uppercase;
             letter-spacing:.07em; }}
  .kpi .v {{ font-size:1.5rem; font-weight:800; color:{INK}; line-height:1.15;
             margin-top:.15rem; }}
  .kpi .d {{ font-size:.76rem; color:{MUTED}; margin-top:.15rem; }}

  /* ---------- status ---------- */
  .badge {{ display:inline-block; padding:.16rem .6rem; border-radius:999px;
            font-size:.73rem; font-weight:700; }}
  .b-ok {{ background:{OK_SOFT}; color:{OK}; }}
  .b-warn {{ background:{WARN_SOFT}; color:{WARN}; }}
  .b-bad {{ background:{BAD_SOFT}; color:{BAD}; }}
  .b-info {{ background:{PRIMARY_SOFT}; color:{PRIMARY}; }}
  .b-mute {{ background:#EEF1F1; color:{MUTED}; }}

  .live {{ display:inline-block; width:9px; height:9px; border-radius:50%;
           background:#3FD68B; margin-right:7px;
           box-shadow:0 0 0 0 rgba(63,214,139,.7); animation:p 1.8s infinite; }}
  @keyframes p {{ 70% {{ box-shadow:0 0 0 9px rgba(63,214,139,0); }}
                  100% {{ box-shadow:0 0 0 0 rgba(63,214,139,0); }} }}

  /* ---------- cover status banner ---------- */
  .cover {{ border-radius:14px; padding:1.25rem 1.4rem; color:#fff;
            background:linear-gradient(135deg,{PRIMARY} 0%,#15837A 100%); }}
  .cover.off {{ background:linear-gradient(135deg,#5A6866 0%,#77837F 100%); }}
  .cover .st {{ font-size:1.5rem; font-weight:800; }}
  .cover .mt {{ font-size:.88rem; opacity:.9; margin-top:.15rem; }}
  .cover .rate {{ font-size:2.6rem; font-weight:800; line-height:1; margin-top:.7rem; }}
  .cover .rl {{ font-size:.8rem; opacity:.85; }}

  /* ---------- policy card ----------
     Header uses floats, not flex, for the same reason as the top bar. */
  .pol {{ border:1px solid {LINE}; border-radius:14px; background:#fff; }}
  .pol .h {{ background:{PRIMARY_SOFT}; padding:.85rem 1.1rem;
             border-radius:14px 14px 0 0; }}
  .pol .h::after {{ content:""; display:table; clear:both; }}
  .pol .h .hl {{ float:left; }}
  .pol .h .hr {{ float:right; text-align:right; }}
  .pol .h .t {{ font-weight:800; color:{INK}; font-size:1.02rem;
                line-height:1.35; }}
  .pol .h .n {{ font-size:.76rem; color:{MUTED};
                font-family:ui-monospace,monospace; line-height:1.35; }}
  .pol .b {{ padding:.5rem 1.1rem .95rem; }}
  /* Rows: table layout, so label and value can never separate. */
  .row {{ display:table; width:100%; padding:.45rem 0;
          border-bottom:1px solid #EDF2F1; }}
  .row:last-child {{ border-bottom:none; }}
  .row .l {{ display:table-cell; font-size:.85rem; color:{MUTED};
             text-align:left; padding-right:1rem; }}
  .row .r {{ display:table-cell; font-size:.9rem; font-weight:700;
             color:{INK}; text-align:right; white-space:nowrap; }}

  /* ---------- product / plan card ---------- */
  .plan {{ border:1px solid {LINE}; border-radius:14px; background:#fff;
           padding:1.1rem 1.2rem; height:100%; }}
  .plan.sel {{ border:2px solid {PRIMARY}; box-shadow:0 4px 18px rgba(15,92,87,.12); }}
  .plan .nm {{ font-weight:800; font-size:1.05rem; color:{INK}; }}
  .plan .pr {{ font-size:1.9rem; font-weight:800; color:{PRIMARY};
               line-height:1.1; margin:.35rem 0 .1rem; }}
  .plan .pu {{ font-size:.78rem; color:{MUTED}; }}
  .plan ul {{ margin:.7rem 0 0 0; padding-left:1.05rem; }}
  .plan li {{ font-size:.85rem; color:{INK}; margin-bottom:.28rem; line-height:1.4; }}
  .plan li.no {{ color:#AEB9B7; }}

  /* ---------- claim tracker ----------
     Table layout: each step is a cell, so the steps cannot separate from
     their connectors however the markup is reflowed. */
  .track {{ display:table; width:100%; margin:.6rem 0 .2rem;
            table-layout:fixed; }}
  .track .cell {{ display:table-cell; text-align:center; vertical-align:top;
                  position:relative; }}
  .track .n {{ display:inline-block; width:28px; height:28px; line-height:28px;
               border-radius:50%; font-size:.78rem; font-weight:800;
               background:#E8EDEC; color:#93A2A0; text-align:center; }}
  .track .n.on {{ background:{PRIMARY}; color:#fff; }}
  .track .n.bad {{ background:{BAD}; color:#fff; }}
  .track .lab {{ display:block; font-size:.72rem; color:{MUTED};
                 margin-top:.3rem; }}
  .track .lab.on {{ color:{PRIMARY}; font-weight:700; }}

  /* ---------- phone ---------- */
  .phone {{ width:310px; margin:0 auto; background:{INK}; border-radius:34px;
            padding:11px; box-shadow:0 14px 40px rgba(0,0,0,.2); }}
  .screen {{ background:#F6FAFA; border-radius:25px; overflow:hidden; }}

  /* ---------- misc ---------- */
  .formula {{ background:#F5F8F8; border-left:3px solid {PRIMARY};
              padding:.6rem .9rem; font-family:ui-monospace,monospace;
              font-size:.8rem; border-radius:4px; margin:.4rem 0 .8rem; }}
  .note {{ background:{WARN_SOFT}; border-left:3px solid {WARN}; padding:.7rem 1rem;
           border-radius:6px; font-size:.86rem; color:#5A4A22; margin:.6rem 0; }}
  .ref {{ display:inline-block; background:{PRIMARY_SOFT}; color:{PRIMARY};
          padding:.12rem .5rem; border-radius:6px; font-size:.72rem;
          font-weight:600; }}
  .empty {{ border:1px dashed {LINE}; border-radius:12px; padding:2rem;
            text-align:center; color:{MUTED}; font-size:.9rem; }}
  [data-testid="stSidebarNav"] {{ padding-top:.4rem; }}
</style>
"""


# ------------------------------------------------------------------ formatting
def inr(x, decimals=0):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return str(x)
    neg, x = x < 0, abs(x)
    s = f"{x:,.{decimals}f}"
    whole, frac = (s.split(".") + [""])[:2]
    frac = "." + frac if frac else ""
    whole = whole.replace(",", "")
    if len(whole) > 3:
        last3, rest = whole[-3:], whole[:-3]
        parts = []
        while len(rest) > 2:
            parts.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            parts.insert(0, rest)
        whole = ",".join(parts) + "," + last3
    out = f"₹{whole}{frac}"
    return ("−" + out) if neg else out


def crore(x, d=0):
    return f"₹{x / 1e7:,.{d}f} cr"


def lakh(x, d=1):
    return f"₹{x / 1e5:,.{d}f} L"


# ------------------------------------------------------------------ data
@st.cache_data(show_spinner=False)
def riders(n=None):
    return data_gen.generate_riders(n=n)


@st.cache_data(show_spinner=False)
def trips(n_riders=800):
    return data_gen.generate_trips(riders().head(n_riders))


@st.cache_data(show_spinner=False)
def book_claims():
    return data_gen.simulate_claims(riders())


# ------------------------------------------------------------------ chrome
def html(markup: str) -> str:
    """
    Collapse a multi-line HTML string onto one line.

    Streamlit runs everything through a Markdown parser first, and Markdown
    treats a line indented by four or more spaces as a code block. Multi-line
    HTML written with normal Python indentation therefore gets shredded before
    it ever reaches the browser. Collapsing runs of whitespace to a single
    space fixes it, and is harmless because HTML collapses whitespace anyway.
    """
    return " ".join(markup.split())


def md(markup: str):
    """st.markdown for raw HTML, indentation-safe."""
    st.markdown(html(markup), unsafe_allow_html=True)


def boot(title):
    st.markdown(CSS, unsafe_allow_html=True)


def topbar(mode, right=""):
    """
    The green bar at the top of every screen.

    ONE block element, inline children, floats instead of flex. Streamlit runs
    markup through a Markdown parser that restructures nested block elements —
    a child <div> got hoisted out of the bar and rendered above it. Floats with
    a clearfix require no height negotiation, so nothing can escape.

    `right` must be a single short line. Anything longer belongs in the sidebar,
    which already carries the rider's identity.
    """
    md(f"<div class='topbar'>"
       f"<span class='logo'>🛵 {BRAND}</span>"
       f"<span class='mode'>{mode}</span>"
       f"<span class='tb-right'>{right}</span>"
       f"</div>")


def h(title, sub=""):
    st.markdown(f"### {title}")
    if sub:
        st.markdown(f"<div style='color:{MUTED};font-size:.9rem;margin-top:-.5rem;"
                    f"margin-bottom:.8rem;max-width:92ch'>{sub}</div>",
                    unsafe_allow_html=True)


def kpi(col, label, value, delta=""):
    col.markdown(html(f"<div class='kpi'><div class='k'>{label}</div>"
                      f"<div class='v'>{value}</div>"
                      f"<div class='d'>{delta}</div></div>"),
                 unsafe_allow_html=True)


def card(col, num, title, body):
    col.markdown(html(f"<div class='card'><div class='num'>{num}</div>"
                      f"<h4>{title}</h4><p>{body}</p></div>"),
                 unsafe_allow_html=True)


def badge(text, kind="info"):
    return f"<span class='badge b-{kind}'>{text}</span>"


def rows(items):
    """items: list of (label, value_html)"""
    return "".join(f"<div class='row'><span class='l'>{a}</span>"
                   f"<span class='r'>{b}</span></div>" for a, b in items)


def note(text):
    st.markdown(f"<div class='note'>{text}</div>", unsafe_allow_html=True)


def formula(text):
    st.markdown(f"<div class='formula'>{text}</div>", unsafe_allow_html=True)


def ref(text):
    st.markdown(f"<span class='ref'>{text}</span>", unsafe_allow_html=True)


def empty(text):
    st.markdown(f"<div class='empty'>{text}</div>", unsafe_allow_html=True)


def tracker(stage: int, declined=False, labels=None):
    """
    Claim progress bar, stage 0..3.

    Table layout rather than flex — each step and its label live in one cell,
    so nothing can drift apart when Streamlit reflows the markup.
    """
    labels = labels or ["Submitted", "Verifying", "Approved", "Paid"]
    out = "<div class='track'>"
    for i, label in enumerate(labels):
        on = i <= stage
        bad = declined and i == stage
        cls = "bad" if bad else ("on" if on else "")
        mark = "✕" if bad else ("✓" if on else str(i + 1))
        out += (f"<span class='cell'>"
                f"<span class='n {cls}'>{mark}</span>"
                f"<span class='lab {'on' if on else ''}'>{label}</span>"
                f"</span>")
    out += "</div>"
    md(out)


CLAIM_BADGE = {
    "Paid": "ok", "Approved": "ok", "Submitted": "info", "Verifying": "info",
    "Investigating": "warn", "Declined": "bad",
}
