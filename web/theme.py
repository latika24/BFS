"""
Design system for the commercial site.

Two rules govern everything here.

1. The site is louder than the app. A gig worker arriving cold has about four
   seconds to understand that this is insurance they own, priced by the hour.
   That needs display type, colour blocks and short sentences — not the
   restrained density that suits the insurer console.

2. Markup goes through `st.html`, never `st.markdown`. Streamlit's markdown
   pipeline restructures nested block elements; `st.html` does not touch them,
   so flex and grid behave normally and components can nest.

The insurer console keeps the original palette in `shared.py`. This module
extends it rather than replacing it, so the analytics screens are untouched.
"""
from __future__ import annotations

import streamlit as st

# --------------------------------------------------------------------- palette
INK        = "#0A1F1C"   # headlines
BODY       = "#3B4B48"   # body copy
MUTED      = "#6E807D"   # captions
BRAND      = "#0F5C57"   # the teal carried over from the app
BRAND_DEEP = "#08332F"   # hero and footer grounds
BRAND_MID  = "#14796F"
BRAND_SOFT = "#E7F1F0"
ACCENT     = "#FF6A35"   # the only colour a call to action is allowed to be
ACCENT_DEEP = "#D94E1F"
ACCENT_SOFT = "#FFEDE4"
MINT       = "#7FE3C4"   # highlights on dark grounds
SIGNAL     = "#FFC94D"   # attention, never alarm
CREAM      = "#FFF9F3"
SAND       = "#F5F1EA"
LINE       = "#E3EAE8"
OK         = "#1F8A5B"
BAD        = "#B23F30"

# Noto Color Emoji is loaded deliberately. Streamlit Community Cloud runs on a
# Linux image with no emoji font installed, so the icon on every card renders as
# an empty box there while looking fine on the developer's Mac.
FONT_URL = ("https://fonts.googleapis.com/css2?"
            "family=Manrope:wght@400;500;600;700;800&"
            "family=Noto+Sans+Devanagari:wght@400;500;600;700;800&"
            "family=Noto+Color+Emoji&display=swap")

SITE_CSS = f"""
<style>
@import url('{FONT_URL}');

:root {{
  --ink:{INK}; --body:{BODY}; --muted:{MUTED};
  --brand:{BRAND}; --brand-deep:{BRAND_DEEP}; --brand-mid:{BRAND_MID};
  --brand-soft:{BRAND_SOFT};
  --accent:{ACCENT}; --accent-deep:{ACCENT_DEEP}; --accent-soft:{ACCENT_SOFT};
  --mint:{MINT}; --signal:{SIGNAL};
  --cream:{CREAM}; --sand:{SAND}; --line:{LINE};
}}

/* The site is a marketing page, so it gets more room and more air than the
   console, which is a dense working screen. Streamlit's default top padding is
   sized for a dashboard title; on a landing page it pushes the hero below the
   fold, so it is cut back — but not below 4.6rem, because the header is fixed
   at 60px and anything above that line is unclickable. */
.block-container {{ max-width: 1180px; padding-top: 4.6rem; }}

.gs, .gs * {{
  font-family:'Manrope','Noto Sans Devanagari',-apple-system,BlinkMacSystemFont,
              'Segoe UI','Noto Color Emoji','Apple Color Emoji',
              'Segoe UI Emoji',sans-serif;
  box-sizing:border-box;
}}
.gs {{ color:var(--body); }}
.gs a {{ color:inherit; text-decoration:none; }}

/* ---------------------------------------------------------------- utility bar */
.gs-util {{
  display:flex; align-items:center; justify-content:space-between;
  gap:1rem; padding:.15rem 0 .55rem; border-bottom:1px solid var(--line);
  margin-bottom:1.1rem; flex-wrap:wrap;
}}
.gs-util .tag {{
  font-size:.82rem; font-weight:600; color:var(--brand);
  display:flex; align-items:center; gap:.5rem;
}}
.gs-util .tag .dot {{
  width:7px; height:7px; border-radius:50%; background:{MINT};
  box-shadow:0 0 0 3px rgba(127,227,196,.28);
}}
.gs-util .meta {{ font-size:.78rem; color:var(--muted); }}

/* ---------------------------------------------------------------------- hero */
.gs-hero {{
  position:relative; overflow:hidden;
  border-radius:26px; padding:3.1rem 3rem 2.6rem;
  background:
    radial-gradient(900px 380px at 88% -12%, rgba(127,227,196,.30), transparent 62%),
    radial-gradient(620px 340px at 4% 108%, rgba(255,106,53,.26), transparent 60%),
    linear-gradient(140deg, {BRAND_DEEP} 0%, {BRAND} 52%, {BRAND_MID} 100%);
  color:#fff;
}}
.gs-hero.compact {{ padding:2.3rem 2.6rem 2.1rem; border-radius:22px; }}
.gs-hero .eyebrow {{
  display:inline-flex; align-items:center; gap:.45rem;
  background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.26);
  color:#EAFBF6; font-size:.74rem; font-weight:700; letter-spacing:.11em;
  text-transform:uppercase; padding:.34rem .8rem; border-radius:999px;
  margin-bottom:1.1rem;
}}
.gs-hero h1 {{
  font-size:3.15rem; line-height:1.04; font-weight:800; letter-spacing:-.033em;
  color:#fff; margin:0 0 .85rem; max-width:19ch;
}}
.gs-hero.compact h1 {{ font-size:2.4rem; max-width:22ch; }}
.gs-hero h1 em {{ font-style:normal; color:{MINT}; }}
.gs-hero .sub {{
  font-size:1.08rem; line-height:1.6; color:rgba(255,255,255,.9);
  max-width:56ch; margin:0 0 1.5rem; font-weight:500;
}}
.gs-hero .hero-note {{
  font-size:.83rem; color:rgba(255,255,255,.72); margin-top:1.1rem;
}}
.gs-hero .badges {{ display:flex; gap:.5rem; flex-wrap:wrap; margin-top:1.35rem; }}
.gs-hero .badges span {{
  background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.22);
  border-radius:999px; padding:.4rem .85rem; font-size:.82rem; font-weight:600;
  color:#EAFBF6;
}}

/* price flag that sits in the hero */
.gs-flag {{
  background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.22);
  border-radius:18px; padding:1.15rem 1.3rem; backdrop-filter:blur(4px);
}}
.gs-flag .l {{ font-size:.76rem; text-transform:uppercase; letter-spacing:.1em;
               color:rgba(255,255,255,.7); font-weight:700; }}
.gs-flag .v {{ font-size:2.5rem; font-weight:800; color:#fff; line-height:1.05;
               margin:.25rem 0 .1rem; }}
.gs-flag .v small {{ font-size:1rem; font-weight:600; opacity:.8; }}
.gs-flag .d {{ font-size:.84rem; color:rgba(255,255,255,.78); line-height:1.5; }}

/* Split hero: copy on the left, illustration on the right, one colour ground. */
.gs-hero.split {{
  display:grid; grid-template-columns:1.02fr .98fr; gap:1.8rem;
  align-items:center; padding:2.4rem 2.4rem 2.4rem 3rem;
}}
.gs-hero.split h1 {{ font-size:2.9rem; max-width:16ch; }}
.gs-hero.split .sub {{ font-size:1rem; max-width:44ch; margin-bottom:1.1rem; }}
.gs-hero .art {{ width:100%; }}
.gs-hero .ticks {{ list-style:none; padding:0; margin:0 0 .2rem; }}
.gs-hero .ticks li {{
  display:flex; align-items:flex-start; gap:.6rem; font-size:.97rem;
  font-weight:600; color:rgba(255,255,255,.94); margin-bottom:.55rem;
  line-height:1.45;
}}
.gs-hero .ticks .tk {{
  flex:0 0 22px; width:22px; height:22px; border-radius:50%;
  background:{MINT}; display:flex; align-items:center; justify-content:center;
  margin-top:.05rem;
}}
@media (max-width:980px) {{
  .gs-hero.split {{ grid-template-columns:1fr; }}
  .gs-hero.split h1 {{ font-size:2.1rem; }}
}}

/* Platform wordmark chips */
.gs-chips {{ display:flex; flex-wrap:wrap; gap:.5rem; align-items:center; }}
.gs-chip {{
  display:inline-flex; align-items:center; border:1.5px solid;
  border-radius:999px; padding:.42rem .95rem; font-size:.88rem;
  font-weight:800; letter-spacing:-.01em; white-space:nowrap;
}}

/* Icon tile grid — the Acko-style "what we cover" board */
.gs-tiles {{ display:grid; grid-template-columns:repeat(5,1fr); gap:.7rem; }}
.gs-tile {{
  background:#fff; border:1px solid var(--line); border-radius:16px;
  padding:1.05rem .9rem; text-align:center; transition:.15s;
}}
.gs-tile:hover {{ border-color:var(--brand); transform:translateY(-2px); }}
.gs-tile .ic {{
  width:44px; height:44px; margin:0 auto .6rem; border-radius:13px;
  background:var(--brand-soft); display:flex; align-items:center;
  justify-content:center;
}}
.gs-tile .t {{ font-size:.86rem; font-weight:800; color:var(--ink);
               line-height:1.32; margin-bottom:.2rem; }}
.gs-tile .v {{ font-size:.92rem; font-weight:800; color:var(--brand); }}
.gs-tile .s {{ font-size:.74rem; color:var(--muted); line-height:1.4;
               margin-top:.15rem; }}
.gs-tile.hot .ic {{ background:var(--accent-soft); }}
.gs-tile.hot .v {{ color:var(--accent-deep); }}
@media (max-width:1000px) {{ .gs-tiles {{ grid-template-columns:repeat(3,1fr); }} }}

/* Product card with an illustrated header */
.gs-product {{
  background:#fff; border:2px solid var(--line); border-radius:22px;
  overflow:hidden; height:100%; display:flex; flex-direction:column;
}}
.gs-product.a {{ border-color:{BRAND}; }}
.gs-product.b {{ border-color:{ACCENT}; }}
.gs-product .banner {{ line-height:0; }}
.gs-product .body {{ padding:1.3rem 1.4rem 1.4rem; display:flex;
                     flex-direction:column; flex:1; }}
.gs-product .tag {{
  display:inline-flex; align-items:center; gap:.4rem; align-self:flex-start;
  font-size:.7rem; font-weight:800; letter-spacing:.12em;
  text-transform:uppercase; padding:.3rem .7rem; border-radius:999px;
  margin-bottom:.6rem;
}}
.gs-product.a .tag {{ background:var(--brand-soft); color:{BRAND}; }}
.gs-product.b .tag {{ background:var(--accent-soft); color:{ACCENT_DEEP}; }}
.gs-product h3 {{ font-size:1.32rem; font-weight:800; color:var(--ink);
                  margin:0 0 .35rem; letter-spacing:-.022em; }}
.gs-product .lede {{ font-size:.93rem; line-height:1.55; color:var(--body);
                     margin:0 0 1rem; min-height:4.3rem; }}
.gs-product .lines {{ margin-top:auto; }}
.gs-product .line {{
  display:flex; align-items:center; gap:.7rem; padding:.62rem 0;
  border-top:1px solid #EEF3F2;
}}
.gs-product .line .ico {{ flex:0 0 34px; width:34px; height:34px;
  border-radius:10px; background:var(--brand-soft); display:flex;
  align-items:center; justify-content:center; }}
.gs-product.b .line .ico {{ background:var(--accent-soft); }}
.gs-product .line .lb {{ flex:1; font-size:.9rem; font-weight:700;
                         color:var(--ink); line-height:1.35; }}
.gs-product .line .lb small {{ display:block; font-size:.77rem; font-weight:500;
                               color:var(--muted); margin-top:.1rem; }}
.gs-product .line .vl {{ font-size:1.02rem; font-weight:800; color:{BRAND};
                         white-space:nowrap; text-align:right; }}
.gs-product.b .line .vl {{ color:{ACCENT_DEEP}; }}

/* Media band — illustration beside copy */
.gs-media {{
  background:#fff; border:1px solid var(--line); border-radius:22px;
  padding:1.6rem 1.8rem; height:100%;
}}
.gs-media.soft {{ background:var(--cream); border-color:#F0E4D8; }}
.gs-media.mint {{ background:var(--brand-soft); border-color:#D3E6E3; }}

/* ------------------------------------------------------------------ sections */
.gs-kicker {{
  font-size:.75rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase;
  color:var(--accent); margin-bottom:.5rem;
}}
.gs-h2 {{
  font-size:2.05rem; line-height:1.14; font-weight:800; letter-spacing:-.028em;
  color:var(--ink); margin:0 0 .6rem; max-width:24ch;
}}
.gs-h2.wide {{ max-width:34ch; }}
.gs-lede {{
  font-size:1.02rem; line-height:1.62; color:var(--body); max-width:64ch;
  margin:0 0 .3rem;
}}

/* ------------------------------------------------------------------- cards */
.gs-grid {{ display:grid; gap:.9rem; }}
.gs-grid.c2 {{ grid-template-columns:repeat(2,1fr); }}
.gs-grid.c3 {{ grid-template-columns:repeat(3,1fr); }}
.gs-grid.c4 {{ grid-template-columns:repeat(4,1fr); }}
@media (max-width:900px) {{
  .gs-grid.c3, .gs-grid.c4 {{ grid-template-columns:repeat(2,1fr); }}
  .gs-hero h1 {{ font-size:2.2rem; }}
}}

.gs-card {{
  background:#fff; border:1px solid var(--line); border-radius:18px;
  padding:1.35rem 1.4rem; height:100%; transition:border-color .15s, box-shadow .15s;
}}
.gs-card:hover {{ border-color:#C8DAD7; box-shadow:0 8px 26px rgba(10,31,28,.07); }}
.gs-card .ic {{
  width:42px; height:42px; border-radius:12px; background:var(--brand-soft);
  display:flex; align-items:center; justify-content:center; font-size:1.22rem;
  margin-bottom:.85rem;
}}
.gs-card h3 {{
  font-size:1.06rem; font-weight:800; color:var(--ink); margin:0 0 .4rem;
  letter-spacing:-.012em; line-height:1.3;
}}
.gs-card p {{ font-size:.9rem; line-height:1.58; color:var(--body); margin:0; }}
.gs-card .amt {{
  font-size:1.5rem; font-weight:800; color:var(--brand); letter-spacing:-.02em;
  margin:.1rem 0 .3rem; line-height:1.1;
}}
.gs-card .amt small {{ font-size:.8rem; font-weight:600; color:var(--muted); }}
.gs-card.dark {{ background:var(--brand-deep); border-color:transparent; color:#fff; }}
.gs-card.dark h3 {{ color:#fff; }}
.gs-card.dark p {{ color:rgba(255,255,255,.82); }}
.gs-card.dark .ic {{ background:rgba(255,255,255,.13); }}
.gs-card.cream {{ background:var(--cream); }}
.gs-card.sand {{ background:var(--sand); border-color:#E7E0D5; }}
.gs-card.accent {{ border-color:var(--accent); border-width:2px; }}

/* ---------------------------------------------------------------- stat strip */
.gs-stats {{
  display:grid; grid-template-columns:repeat(4,1fr); gap:0;
  background:#fff; border:1px solid var(--line); border-radius:18px;
  overflow:hidden;
}}
.gs-stats .s {{ padding:1.15rem 1.25rem; border-right:1px solid var(--line); }}
.gs-stats .s:last-child {{ border-right:none; }}
.gs-stats .v {{
  font-size:1.85rem; font-weight:800; color:var(--brand); line-height:1.05;
  letter-spacing:-.028em;
}}
.gs-stats .k {{ font-size:.83rem; color:var(--body); margin-top:.3rem;
                font-weight:600; line-height:1.4; }}
.gs-stats .n {{ font-size:.74rem; color:var(--muted); margin-top:.18rem; }}
@media (max-width:900px) {{
  .gs-stats {{ grid-template-columns:repeat(2,1fr); }}
}}

/* --------------------------------------------------------------------- steps */
.gs-steps {{ display:grid; grid-template-columns:repeat(4,1fr); gap:.9rem; }}
.gs-step {{
  background:#fff; border:1px solid var(--line); border-radius:18px;
  padding:1.25rem 1.3rem; position:relative; height:100%;
}}
.gs-step .n {{
  width:30px; height:30px; border-radius:50%; background:var(--accent);
  color:#fff; font-weight:800; font-size:.85rem; display:flex;
  align-items:center; justify-content:center; margin-bottom:.75rem;
}}
.gs-step h4 {{ font-size:.98rem; font-weight:800; color:var(--ink);
               margin:0 0 .32rem; }}
.gs-step p {{ font-size:.87rem; line-height:1.55; color:var(--body); margin:0; }}
.gs-step .t {{ font-size:.76rem; font-weight:700; color:var(--brand);
               margin-top:.6rem; text-transform:uppercase; letter-spacing:.07em; }}
@media (max-width:900px) {{ .gs-steps {{ grid-template-columns:repeat(2,1fr); }} }}

/* ----------------------------------------------------------------- CTA band */
.gs-cta {{
  border-radius:24px; padding:2.4rem 2.6rem; color:#fff;
  background:
    radial-gradient(560px 260px at 92% 10%, rgba(255,201,77,.24), transparent 60%),
    linear-gradient(120deg, {ACCENT_DEEP} 0%, {ACCENT} 100%);
  display:flex; align-items:center; justify-content:space-between;
  gap:2rem; flex-wrap:wrap;
}}
.gs-cta h2 {{ font-size:1.9rem; font-weight:800; margin:0 0 .4rem; color:#fff;
              letter-spacing:-.026em; max-width:20ch; line-height:1.14; }}
.gs-cta p {{ margin:0; font-size:1rem; color:rgba(255,255,255,.92);
             max-width:46ch; line-height:1.55; }}
.gs-cta .rt {{ text-align:right; }}
.gs-cta .rt .big {{ font-size:2.5rem; font-weight:800; line-height:1; }}
.gs-cta .rt .sm {{ font-size:.85rem; color:rgba(255,255,255,.85); }}

/* ------------------------------------------------------------------- quotes */
.gs-quote {{
  background:var(--cream); border:1px solid #F0E4D8; border-radius:18px;
  padding:1.35rem 1.4rem; height:100%;
}}
.gs-quote .q {{
  font-size:.98rem; line-height:1.62; color:var(--ink); font-weight:600;
  margin-bottom:.9rem;
}}
.gs-quote .who {{ display:flex; align-items:center; gap:.65rem; }}
.gs-quote .av {{
  width:38px; height:38px; border-radius:50%; background:var(--brand);
  color:#fff; font-weight:800; font-size:.9rem; display:flex;
  align-items:center; justify-content:center; flex:0 0 38px;
}}
.gs-quote .nm {{ font-size:.87rem; font-weight:800; color:var(--ink); }}
.gs-quote .rl {{ font-size:.78rem; color:var(--muted); }}

/* -------------------------------------------------------------- comparison */
.gs-table {{ width:100%; border-collapse:separate; border-spacing:0;
             border:1px solid var(--line); border-radius:18px; overflow:hidden;
             background:#fff; }}
.gs-table th {{
  background:var(--brand-deep); color:#fff; font-size:.83rem; font-weight:700;
  text-align:left; padding:.85rem 1.05rem; letter-spacing:.01em;
}}
.gs-table th.us {{ background:var(--accent); }}
.gs-table td {{
  padding:.85rem 1.05rem; font-size:.89rem; border-top:1px solid var(--line);
  color:var(--body); vertical-align:top; line-height:1.5;
}}
.gs-table td.lbl {{ font-weight:700; color:var(--ink); background:#FBFCFC; }}
.gs-table td.us {{ background:var(--accent-soft); font-weight:600;
                   color:var(--ink); }}

/* ---------------------------------------------------------------- list rows */
.gs-rows {{ background:#fff; border:1px solid var(--line); border-radius:18px;
            overflow:hidden; }}
.gs-row {{
  display:flex; align-items:flex-start; justify-content:space-between; gap:1rem;
  padding:.9rem 1.2rem; border-bottom:1px solid #EEF3F2;
}}
.gs-row:last-child {{ border-bottom:none; }}
.gs-row .l {{ font-size:.92rem; color:var(--ink); font-weight:600; }}
.gs-row .l small {{ display:block; font-size:.79rem; color:var(--muted);
                    font-weight:500; margin-top:.15rem; line-height:1.45; }}
.gs-row .r {{ font-size:1rem; font-weight:800; color:var(--brand);
              white-space:nowrap; text-align:right; }}
.gs-row .r small {{ display:block; font-size:.74rem; color:var(--muted);
                    font-weight:600; }}

/* -------------------------------------------------------------------- misc */
.gs-pill {{
  display:inline-block; padding:.28rem .72rem; border-radius:999px;
  font-size:.78rem; font-weight:700; margin:0 .3rem .35rem 0;
}}
.gs-pill.brand {{ background:var(--brand-soft); color:var(--brand); }}
.gs-pill.accent {{ background:var(--accent-soft); color:var(--accent-deep); }}
.gs-pill.ok {{ background:#E4F4EC; color:{OK}; }}
.gs-pill.sand {{ background:var(--sand); color:var(--body); }}

.gs-callout {{
  border-left:4px solid var(--accent); background:var(--accent-soft);
  border-radius:0 14px 14px 0; padding:1.05rem 1.3rem;
  font-size:.94rem; line-height:1.6; color:#5A2E17;
}}
.gs-callout b {{ color:#3F1E0C; }}
.gs-callout.brand {{ border-left-color:var(--brand); background:var(--brand-soft);
                     color:#0C3E3A; }}
.gs-callout.brand b {{ color:{BRAND_DEEP}; }}

.gs-band {{
  background:var(--sand); border-radius:22px; padding:1.9rem 2.1rem;
}}
.gs-band.deep {{ background:var(--brand-deep); color:#fff; }}
.gs-band.deep .gs-h2 {{ color:#fff; }}
.gs-band.deep .gs-lede {{ color:rgba(255,255,255,.84); }}
.gs-band.deep .gs-kicker {{ color:{MINT}; }}

.gs-foot {{
  background:{BRAND_DEEP}; color:rgba(255,255,255,.76); border-radius:22px;
  padding:2.1rem 2.3rem 1.5rem; margin-top:.6rem;
}}
.gs-foot .cols {{ display:grid; grid-template-columns:1.6fr 1fr 1fr 1fr; gap:1.6rem; }}
.gs-foot h5 {{ color:#fff; font-size:.8rem; text-transform:uppercase;
               letter-spacing:.1em; margin:0 0 .7rem; font-weight:800; }}
.gs-foot .lg {{ font-size:1.25rem; font-weight:800; color:#fff;
                margin-bottom:.5rem; }}
.gs-foot p {{ font-size:.86rem; line-height:1.6; margin:0; }}
.gs-foot ul {{ list-style:none; padding:0; margin:0; }}
.gs-foot li {{ font-size:.86rem; margin-bottom:.42rem; }}
.gs-foot .rule {{ border-top:1px solid rgba(255,255,255,.14); margin:1.5rem 0 1rem; }}
.gs-foot .fine {{ font-size:.76rem; color:rgba(255,255,255,.5); line-height:1.65; }}
@media (max-width:900px) {{ .gs-foot .cols {{ grid-template-columns:1fr 1fr; }} }}

/* Streamlit widget restyling, scoped so the console is unaffected */
.stButton > button {{
  border-radius:999px; font-weight:700; padding:.55rem 1.3rem; font-size:.92rem;
  border-width:1.5px;
}}
.stButton > button[kind="primary"] {{
  background:{ACCENT}; border-color:{ACCENT};
}}
.stButton > button[kind="primary"]:hover {{
  background:{ACCENT_DEEP}; border-color:{ACCENT_DEEP};
}}
[data-testid="stExpander"] details {{
  border:1px solid {LINE}; border-radius:14px; background:#fff;
}}
[data-testid="stExpander"] summary p {{ font-weight:700; color:{INK}; }}
</style>
"""


# Devanagari carries matras above and below the baseline, so the tight display
# leading that makes the English headline look sharp collapses the vowel signs
# into the line above. Loosen it, and only in Hindi.
HINDI_CSS = """
<style>
  .gs-hero h1 { line-height:1.28; letter-spacing:0; }
  .gs-h2 { line-height:1.34; letter-spacing:-.01em; max-width:30ch; }
  .gs-h2.wide { max-width:40ch; }
  .gs-hero .eyebrow, .gs-kicker { letter-spacing:.06em; }
  .gs-card h3, .gs-step h4, .gs-cta h2 { line-height:1.45; }
  .gs-stats .v, .gs-card .amt, .gs-flag .v { line-height:1.35; }
</style>
"""


def boot():
    """
    Inject the site stylesheet. Call once at the top of every web page.

    No scoping selector is needed: Streamlit re-runs the whole script on every
    navigation, so this CSS exists only while a site page is on screen. The
    insurer console never sees it.
    """
    from .i18n import is_hi

    st.html(SITE_CSS)
    if is_hi():
        st.html(HINDI_CSS)


def spacer(rem: float = 1.6):
    st.html(f"<div style='height:{rem}rem'></div>")


# --------------------------------------------------------------- components
def hero(eyebrow: str, headline: str, sub: str, badges: list[str] | None = None,
         note: str = "", compact: bool = False) -> str:
    b = ""
    if badges:
        b = "<div class='badges'>" + "".join(f"<span>{x}</span>" for x in badges) + "</div>"
    n = f"<div class='hero-note'>{note}</div>" if note else ""
    return (f"<div class='gs gs-hero{' compact' if compact else ''}'>"
            f"<div class='eyebrow'>{eyebrow}</div>"
            f"<h1>{headline}</h1><div class='sub'>{sub}</div>{b}{n}</div>")


def heading(kicker: str, title: str, lede: str = "", wide: bool = False):
    k = f"<div class='gs-kicker'>{kicker}</div>" if kicker else ""
    l = f"<div class='gs-lede'>{lede}</div>" if lede else ""
    st.html(f"<div class='gs'>{k}<div class='gs-h2{' wide' if wide else ''}'>"
            f"{title}</div>{l}</div>")


def split_hero(eyebrow: str, headline: str, sub: str, ticks: list[str],
               art: str) -> str:
    """
    The landing hero: copy and proof points on the left, a picture of the
    customer on the right. A gig worker should see someone like themselves
    before they read a word.
    """
    from .art import icon
    tk = "".join(
        f"<li><span class='tk'>{icon('check', INK, 13, 3)}</span>{t}</li>"
        for t in ticks)
    return (f"<div class='gs gs-hero split'>"
            f"<div><div class='eyebrow'>{eyebrow}</div><h1>{headline}</h1>"
            f"<div class='sub'>{sub}</div>"
            f"<ul class='ticks'>{tk}</ul></div>"
            f"<div class='art'>{art}</div></div>")


def tiles(items: list[dict], cols: int = 5):
    """items: [{icon, title, value, sub, hot?}] — the covered-events board."""
    from .art import icon as _icon
    out = ""
    for it in items:
        hot = it.get("hot")
        col = ACCENT if hot else BRAND
        v = f"<div class='v'>{it['value']}</div>" if it.get("value") else ""
        s = f"<div class='s'>{it['sub']}</div>" if it.get("sub") else ""
        out += (f"<div class='gs-tile{' hot' if hot else ''}'>"
                f"<div class='ic'>{_icon(it['icon'], col, 22)}</div>"
                f"<div class='t'>{it['title']}</div>{v}{s}</div>")
    st.html(f"<div class='gs gs-tiles' style='grid-template-columns:"
            f"repeat({cols},1fr)'>{out}</div>")


def product(kind: str, tag: str, title: str, lede: str,
            lines: list[tuple], banner: str) -> str:
    """
    One of the two product cards. Both are built from the same function with
    the same number of lines, which is what keeps them the same height —
    previously they were two hand-written blocks and drifted apart.
    """
    from .art import icon as _icon
    col = BRAND if kind == "a" else ACCENT
    body = ""
    for ic, label, sub, value in lines:
        s = f"<small>{sub}</small>" if sub else ""
        body += (f"<div class='line'><div class='ico'>{_icon(ic, col, 18)}</div>"
                 f"<div class='lb'>{label}{s}</div>"
                 f"<div class='vl'>{value}</div></div>")
    return (f"<div class='gs gs-product {kind}'>"
            f"<div class='banner'>{banner}</div>"
            f"<div class='body'><span class='tag'>{tag}</span>"
            f"<h3>{title}</h3><div class='lede'>{lede}</div>"
            f"<div class='lines'>{body}</div></div></div>")


def cards(items: list[dict], cols: int = 3, variant: str = ""):
    """
    items: [{icon, title, body, amount?, amount_note?}]

    `icon` is a name from the line-icon set in `art.py`. Anything not in that
    set is passed through untouched, so a raw glyph still works.
    """
    from .art import icon as _icon, _ICONS
    out = []
    for it in items:
        ic = ""
        if it.get("icon"):
            v = it.get("variant", variant)
            col = "#fff" if v == "dark" else BRAND
            glyph = _icon(it["icon"], col, 22) if it["icon"] in _ICONS else it["icon"]
            ic = f"<div class='ic'>{glyph}</div>"
        amt = ""
        if it.get("amount"):
            note = (f"<small> {it['amount_note']}</small>"
                    if it.get("amount_note") else "")
            amt = f"<div class='amt'>{it['amount']}{note}</div>"
        v = it.get("variant", variant)
        out.append(f"<div class='gs-card {v}'>{ic}<h3>{it['title']}</h3>"
                   f"{amt}<p>{it['body']}</p></div>")
    st.html(f"<div class='gs gs-grid c{cols}'>" + "".join(out) + "</div>")


def stats(items: list[tuple]):
    """items: [(value, label, note)]"""
    out = "".join(f"<div class='s'><div class='v'>{v}</div>"
                  f"<div class='k'>{k}</div><div class='n'>{n}</div></div>"
                  for v, k, n in items)
    st.html(f"<div class='gs gs-stats'>{out}</div>")


def steps(items: list[dict]):
    """items: [{title, body, time}]"""
    out = ""
    for i, it in enumerate(items, 1):
        t = f"<div class='t'>{it['time']}</div>" if it.get("time") else ""
        out += (f"<div class='gs-step'><div class='n'>{i}</div>"
                f"<h4>{it['title']}</h4><p>{it['body']}</p>{t}</div>")
    st.html(f"<div class='gs gs-steps'>{out}</div>")


def quotes(items: list[dict], cols: int = 3):
    """items: [{quote, name, role}]"""
    out = ""
    for it in items:
        initial = it["name"][:1].upper()
        out += (f"<div class='gs-quote'><div class='q'>“{it['quote']}”</div>"
                f"<div class='who'><div class='av'>{initial}</div><div>"
                f"<div class='nm'>{it['name']}</div>"
                f"<div class='rl'>{it['role']}</div></div></div></div>")
    st.html(f"<div class='gs gs-grid c{cols}'>{out}</div>")


def rows(items: list[tuple]):
    """items: [(label, sub, value, value_note)]"""
    out = ""
    for label, sub, value, vnote in items:
        s = f"<small>{sub}</small>" if sub else ""
        vn = f"<small>{vnote}</small>" if vnote else ""
        out += (f"<div class='gs-row'><div class='l'>{label}{s}</div>"
                f"<div class='r'>{value}{vn}</div></div>")
    st.html(f"<div class='gs gs-rows'>{out}</div>")


def callout(text: str, brand: bool = False):
    st.html(f"<div class='gs gs-callout{' brand' if brand else ''}'>{text}</div>")


def cta_band(title: str, body: str, right_big: str = "", right_small: str = ""):
    rt = ""
    if right_big:
        rt = (f"<div class='rt'><div class='big'>{right_big}</div>"
              f"<div class='sm'>{right_small}</div></div>")
    st.html(f"<div class='gs gs-cta'><div><h2>{title}</h2><p>{body}</p></div>"
            f"{rt}</div>")


def comparison(headers: list[str], body: list[list[str]], us_col: int = -1):
    """A table where one column is ours and is visually claimed as such."""
    th = "".join(f"<th class='{'us' if i == us_col % len(headers) else ''}'>{h}</th>"
                 for i, h in enumerate(headers))
    tr = ""
    for row in body:
        tds = ""
        for i, cell in enumerate(row):
            cls = "lbl" if i == 0 else ("us" if i == us_col % len(headers) else "")
            tds += f"<td class='{cls}'>{cell}</td>"
        tr += f"<tr>{tds}</tr>"
    st.html(f"<div class='gs'><table class='gs-table'><thead><tr>{th}</tr>"
            f"</thead><tbody>{tr}</tbody></table></div>")


def pills(items: list[tuple]):
    """items: [(text, kind)]"""
    out = "".join(f"<span class='gs-pill {k}'>{t}</span>" for t, k in items)
    st.html(f"<div class='gs'>{out}</div>")
