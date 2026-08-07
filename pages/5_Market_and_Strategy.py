"""Market & Strategy — segmentation and competitive position. §2.1, §2.2, §3.1, §3.3, §5."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from shared import (page_setup, page_header, kpi, card, inr, crore, note,
                    SEC, MUTED, PRIMARY, PRIMARY_SOFT, ACCENT, OK, LINE, INK)
from engine.config import CFG
from engine import portfolio

page_setup("Market & Strategy")

page_header(
    "Market & Strategy",
    f"{SEC['segmentation']} · {SEC['differentiators']}",
    "Who we target out of the 1.2 crore gig workforce, and the one quadrant of "
    "the competitive map our largest competitor structurally cannot enter.")

segs = pd.DataFrame(CFG["segments"])
total_lakh = segs["size_lakh"].sum()
addressable = segs[segs["decision"].isin(["Primary", "Secondary"])]["size_lakh"].sum()
future = segs[segs["decision"] == "Year 4 onward"]["size_lakh"].sum()

k1, k2, k3, k4 = st.columns(4)
kpi(k1, "Gig workforce", f"{total_lakh} lakh", "≈1.2 crore, Economic Survey 2025-26")
kpi(k2, "Addressable now", f"{addressable} lakh", "primary + secondary segments")
kpi(k3, "Expansion pool", f"{future} lakh", "bike-taxi and ride-hailing, year 4")
kpi(k4, "Target at break-even", "12 lakh",
    f"{12/addressable:.0%} of the addressable pool")

st.write("")
st.divider()

# ------------------------------------------------------------------ funnel
st.markdown("### Segmentation and targeting")
st.markdown(f"<div class='ref'>{SEC['segmentation']}</div>", unsafe_allow_html=True)

colours = {"Primary": PRIMARY, "Secondary": "#3E8F87",
           "Year 4 onward": "#9BB5B2", "Out of scope": "#D6DEDD"}

f1, f2 = st.columns([1.15, 1])
with f1:
    order = ["Primary", "Secondary", "Year 4 onward", "Out of scope"]
    sd = segs.copy()
    sd["_o"] = sd["decision"].map({d: i for i, d in enumerate(order)})
    sd = sd.sort_values("_o")

    fig = go.Figure(go.Bar(
        x=sd["size_lakh"], y=sd["name"], orientation="h",
        marker_color=[colours[d] for d in sd["decision"]],
        text=[f"{v} lakh · {d}" for v, d in zip(sd["size_lakh"], sd["decision"])],
        textposition="outside"))
    fig.update_layout(height=340, margin=dict(l=0, r=120, t=10, b=0),
                      xaxis_title="Workers (lakh)",
                      yaxis=dict(autorange="reversed"), showlegend=False)
    st.plotly_chart(fig, width="stretch")

with f2:
    funnel = go.Figure(go.Funnel(
        y=["Total gig workforce", "Road-exposed segments",
           "Addressable now", "Target at break-even"],
        x=[total_lakh, total_lakh - 23, addressable, 12],
        textinfo="value+percent initial",
        marker_color=["#D6DEDD", "#9BB5B2", "#3E8F87", PRIMARY]))
    funnel.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(funnel, width="stretch")

show = segs.copy()
show["Size"] = show["size_lakh"].map(lambda v: f"{v} lakh")
show = show[["name", "detail", "Size", "decision", "rationale"]]
show.columns = ["Segment", "Detail", "Size", "Decision", "Why"]
st.dataframe(show, width="stretch", hide_index=True)

note("<b>The 12 lakh target is the assumption to attack.</b> It is 29% of the "
     "addressable pool and the whole plan rests on reaching it — the expense "
     "ratio only falls to 21% at that scale. If growth stalls, the response in "
     "the plan is to extend into the 55 lakh bike-taxi and ride-hailing pool "
     "rather than to cut price to buy volume. The Portfolio page models both.")

st.divider()

# ------------------------------------------------------------------ quadrant
st.markdown("### The quadrant nobody else can occupy")
st.markdown(f"<div class='ref'>{SEC['differentiators']}</div>", unsafe_allow_html=True)

q1, q2 = st.columns([1.25, 1])
with q1:
    st.markdown(f"""
    <table class='quadrant' style='border-collapse:collapse;width:100%'>
      <tr>
        <td style='background:#FAFBFB;border:none'></td>
        <td style='background:{PRIMARY_SOFT};font-weight:700;text-align:center'>
            Protects the event</td>
        <td style='background:{PRIMARY_SOFT};font-weight:700;text-align:center'>
            Protects the livelihood</td>
      </tr>
      <tr>
        <td style='background:{PRIMARY_SOFT};font-weight:700;width:110px'>
            Platform owns</td>
        <td>
          <b>Zomato · Swiggy · Zepto group cover</b><br>
          <span style='color:{MUTED}'>Written by ICICI Lombard, Reliance
          General, Acko, Bajaj Allianz. Free, thin, tethered, slow.</span>
        </td>
        <td style='background:#FBFBFA'>
          <b style='color:{MUTED}'>Structurally empty</b><br>
          <span style='color:{MUTED}'>A platform insuring income loss concedes
          responsibility for income continuity — precisely the argument being
          run against it in the Karnataka High Court.</span>
        </td>
      </tr>
      <tr>
        <td style='background:{PRIMARY_SOFT};font-weight:700'>Worker owns</td>
        <td>
          <b>PMSBY · PMJJBY · retail PA</b><br>
          <span style='color:{MUTED}'>Very cheap, very basic. Excludes anyone
          under the 90/120-day threshold.</span>
        </td>
        <td style='background:{PRIMARY};color:#fff'>
          <b>Suraksha — alone here</b><br>
          <span style='opacity:.9'>Worker-owned, portable, priced by the hour,
          and the only product that replaces income while the rider cannot
          work.</span>
        </td>
      </tr>
    </table>""", unsafe_allow_html=True)

with q2:
    st.markdown("**Why the empty quadrant stays empty**")
    st.markdown(
        f"<div style='color:{MUTED};font-size:.9rem;line-height:1.6'>"
        "It is structural, not an oversight. Our strongest product is one our "
        "largest competitor cannot build.<br><br>"
        "<b>Acko's position is a conflict of interest, not a capability gap.</b> "
        "It has real telematics and its own paper, and already covers close to "
        "a million gig workers. But it earns meaningful revenue writing group "
        "cover for Zomato and Swiggy, and cannot simultaneously sell those same "
        "riders a product premised on that cover being inadequate and slow."
        "<br><br>That is what we are attacking. Not their technology.</div>",
        unsafe_allow_html=True)

st.divider()

# ------------------------------------------------------------------ channels
st.markdown("### Distribution access, never group schemes")
st.markdown(f"<div class='ref'>{SEC['marketing_mix']} · Place</div>",
            unsafe_allow_html=True)
st.markdown(
    f"<div style='color:{MUTED};max-width:90ch'>Every channel must produce "
    "individually-owned policies. The partner is a place where we meet "
    "customers, not our customer, and the policy stays with the rider when "
    "they leave.</div>", unsafe_allow_html=True)
st.write("")

d1, d2 = st.columns([1.2, 1])
with d1:
    ch = pd.DataFrame([
        {"Channel": "Fleet & rental depots (Zypp, Yulu, Everest Fleet)",
         "lo": 60, "hi": 120,
         "Note": "Lowest cost, and their hardware telematics validates our model"},
        {"Channel": "Platform onboarding slots", "lo": 80, "hi": 150,
         "Note": "The rider buys and owns the policy, not the platform"},
        {"Channel": "Battery-swap and charging points", "lo": 150, "hi": 250,
         "Note": "Three idle minutes, several times a day — highest intent"},
        {"Channel": "Referral (₹100 each side)", "lo": 200, "hi": 200,
         "Note": "Travels fast through hub WhatsApp groups"},
        {"Channel": "Delivery hubs at shift change", "lo": 400, "hi": 600,
         "Note": "Slow, high-trust, high-conversion"},
        {"Channel": "Paid digital", "lo": 900, "hi": 1200,
         "Note": "Not used — wrong audience, and the EoM cap makes it a breach"},
    ])
    fig2 = go.Figure()
    for _, row in ch.iterrows():
        used = row["Channel"] != "Paid digital"
        fig2.add_trace(go.Scatter(
            x=[row["lo"], row["hi"]], y=[row["Channel"], row["Channel"]],
            mode="lines+markers", line=dict(color=PRIMARY if used else "#C9553D",
                                            width=8),
            marker=dict(size=9), showlegend=False))
    fig2.add_vline(x=350, line_dash="dot", line_color=ACCENT,
                   annotation_text="blended target ₹350")
    fig2.update_layout(height=330, margin=dict(l=0, r=20, t=24, b=0),
                       xaxis_title="Acquisition cost per rider (₹)",
                       yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig2, width="stretch")

with d2:
    st.markdown("**Group cover vs distribution access**")
    st.dataframe(pd.DataFrame([
        {"": "Who buys", "Group cover (avoid)": "The fleet or platform, for everyone",
         "Distribution access (ours)": "Each rider, for themselves"},
        {"": "Whose name is on it", "Group cover (avoid)": "The company's",
         "Distribution access (ours)": "The worker's"},
        {"": "When the rider leaves", "Group cover (avoid)": "Cover ends",
         "Distribution access (ours)": "Cover continues — it is theirs"},
        {"": "When the contract ends", "Group cover (avoid)": "We lose every rider at once",
         "Distribution access (ours)": "We keep every rider"},
    ]), width="stretch", hide_index=True)
    st.caption("Zego built the first kind of business in the UK and exited it "
               "entirely in 2023 to reach profitability faster. Blended CAC of "
               "₹350 against a lifetime value of roughly ₹1,080 — a ratio that "
               "only holds because the policy is portable and tenure is two "
               "years rather than three months.")

st.divider()

# ------------------------------------------------------------------ capital
st.markdown("### Capital and investors")
st.markdown(f"<div class='ref'>{SEC['licence']} · {SEC['investors']}</div>",
            unsafe_allow_html=True)

rounds = pd.DataFrame(CFG["portfolio"]["funding_rounds"])
total_raise = rounds["amount_cr"].sum()

cap1, cap2 = st.columns([1, 1.4])
with cap1:
    figc = go.Figure(go.Bar(
        x=rounds["name"], y=rounds["amount_cr"],
        marker_color=[PRIMARY, "#3E8F87", "#9BB5B2"],
        text=[f"₹{v} cr" for v in rounds["amount_cr"]], textposition="outside"))
    figc.update_layout(height=300, margin=dict(l=0, r=0, t=24, b=0),
                       yaxis_title="₹ crore", xaxis_tickangle=-15)
    st.plotly_chart(figc, width="stretch")
    st.metric("Total equity to break-even", f"₹{total_raise:,.0f} cr")

with cap2:
    rd = rounds[["name", "amount_cr", "investors", "underwriting"]].copy()
    rd["amount_cr"] = rd["amount_cr"].map(lambda v: f"₹{v} cr")
    rd.columns = ["Round", "Size", "Investor types", "What they underwrite"]
    st.dataframe(rd, width="stretch", hide_index=True)

note(f"<b>A discrepancy in the report worth fixing before submission.</b> "
     f"{CFG['portfolio']['funding_note']}")

i1, i2 = st.columns(2)
with i1:
    st.markdown("**Why LeapFrog is the single best fit**")
    st.markdown(
        f"<div style='color:{MUTED};font-size:.9rem;line-height:1.6'>Their "
        "thesis is insurance for emerging consumers in Asia and Africa, they "
        "write cheques large enough to fund a licence, and they are accustomed "
        "to the disclosure an R1 filing demands.<br><br>"
        "The rural and social sector obligation reinforces the case: every "
        "insurer must write a minimum share of business from the unorganised "
        "sector, and where competitors buy their way into compliance at a loss, "
        "<b>our entire book qualifies naturally</b>.</div>",
        unsafe_allow_html=True)
with i2:
    st.markdown("**The trap to avoid**")
    st.markdown(
        f"<div style='color:{MUTED};font-size:.9rem;line-height:1.6'>No equity "
        "from Swiggy, Eternal, Zepto or any single platform. The whole "
        "positioning is that cover follows the worker across every app; the "
        "moment one platform sits on the cap table, every other stops taking "
        "our calls, and the workers who trust us <i>because</i> we are not the "
        "platform stop trusting us.<br><br>"
        "There is a regulatory dimension too — a platform shareholder in an "
        "insurer writing cover for that platform's own workers is a "
        "related-party question IRDAI would examine at R1 and on every share "
        "transfer after. A commercial partnership is fine; equity is not.</div>",
        unsafe_allow_html=True)
