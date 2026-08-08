"""
Claims and settlement.

The plan treats speed of settlement as the product rather than a service level
(§1.1), and monthly published claims data as the primary trust instrument
(§3.3). This page is where both of those promises are made in public: what we
commit to, what we actually did last month, and — the part insurers normally
leave out — every reason we said no.
"""
from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from shared import inr
from web import theme as T, chrome as C
from web.i18n import L
from web.content import SITE, pick

C.utility_bar()

cr = SITE["claims_report"]
sp = SITE["settlement_promise"]

st.html(T.hero(
    L("Claims", "क्लेम"),
    L("A claim paid in four months is <em>not</em> a claim paid.",
      "चार महीने बाद मिला पैसा, पैसा <em>नहीं</em> है।"),
    L("Unions in Telangana and Karnataka have documented injured delivery "
      "partners waiting months for platform insurance to settle. For someone "
      "who earns daily, that is the same as no cover at all. Everything in this "
      "product — the evidence we collect up front, the scheduled benefits, the "
      "direct payments — exists to make a claim payable inside a day.",
      "तेलंगाना और कर्नाटक की यूनियनों ने दर्ज किया है कि घायल डिलीवरी पार्टनर "
      "महीनों तक प्लेटफ़ॉर्म बीमे का इंतज़ार करते हैं। जो रोज़ कमाता है, उसके "
      "लिए यह कवर न होने जैसा ही है। इस प्रोडक्ट की हर चीज़ — पहले से जुटाया "
      "सबूत, तय रकम, सीधा भुगतान — इसीलिए है कि क्लेम एक दिन में चुकाया जा सके।"),
    badges=[
        L(f"{cr['settlement_ratio']:.1%} of claims paid",
          f"{cr['settlement_ratio']:.1%} क्लेम का भुगतान"),
        L(f"Median {cr['median_turnaround_hours']:.1f} hours",
          f"औसतन {cr['median_turnaround_hours']:.1f} घंटे"),
        L(f"{cr['share_settled_instantly']:.0%} settled with no human involved",
          f"{cr['share_settled_instantly']:.0%} बिना किसी इंसान के निपटे"),
        L("₹0 to make a claim", "क्लेम करने का ख़र्च ₹0"),
    ],
    compact=True))

st.write("")
cta = st.columns([1.5, 1.4, 3])
if cta[0].button(L("Get covered", "कवर लें"), type="primary", width="stretch",
                 key="cl_a"):
    st.switch_page(C.REGISTER)
if cta[1].button(L("Try a claim in the app", "ऐप में क्लेम आज़माएँ"),
                 width="stretch", key="cl_b"):
    st.switch_page("views/rider_claims.py")

T.spacer(1.3)

# ---------------------------------------------------------------- the promise
T.heading(L("Our promise", "हमारा वादा"),
          L("Deadlines we publish, and pay for missing.",
            "समय-सीमा जो हम छापते हैं, और चूकने पर भरते हैं।"),
          L("These are not internal targets. They are on this page, they are in "
            "your policy document, and there is a penalty attached to the first "
            "one.", "ये अंदरूनी लक्ष्य नहीं हैं। ये इस पेज पर हैं, आपके पॉलिसी "
            "दस्तावेज़ में हैं, और पहले वाले पर जुर्माना भी लगा है।"))
st.write("")

T.cards([
    {"icon": "⚡", "title": L("Ambulance, phone, order deductions",
                             "एम्बुलेंस, फ़ोन, ऑर्डर कटौती"),
     "amount": L(f"{sp['instant_heads_minutes']} min",
                 f"{sp['instant_heads_minutes']} मिनट"),
     "body": L("Decided by machine against your ride data. No adjuster, no "
               "phone call, no branch visit.",
               "आपके राइड डेटा से मशीन तय करती है। न सर्वेयर, न फ़ोन कॉल, न "
               "ब्रांच के चक्कर।")},
    {"icon": "🕐", "title": L("Hospital cash, fractures, bike damage",
                             "अस्पताल कैश, फ्रैक्चर, गाड़ी का नुक़सान"),
     "amount": L(f"{sp['standard_head_hours']} hrs",
                 f"{sp['standard_head_hours']} घंटे"),
     "body": L("A panel doctor or a network garage confirms, and the money "
               "moves the same working day.",
               "पैनल डॉक्टर या नेटवर्क गैरेज पुष्टि करता है, और पैसा उसी "
               "कामकाजी दिन चला जाता है।")},
    {"icon": "🔍", "title": L("Disputed or high-value claims",
                             "विवादित या बड़ी रकम के क्लेम"),
     "amount": L(f"{sp['investigation_head_days']} days",
                 f"{sp['investigation_head_days']} दिन"),
     "body": L("A human reviews it. You are told on day one that it is under "
               "review, by whom, and when you will hear back.",
               "इंसान जाँचता है। पहले ही दिन आपको बताया जाता है कि जाँच चल रही "
               "है, कौन कर रहा है, और जवाब कब मिलेगा।")},
    {"icon": "🤍", "title": L("Death claims — advance to the family",
                             "मृत्यु क्लेम — परिवार को अग्रिम"),
     "amount": inr(sp["advance_on_death_claim_amount"]),
     "amount_note": L(f"within {sp['advance_on_death_claim_hours']} hours",
                      f"{sp['advance_on_death_claim_hours']} घंटे में"),
     "body": L("Released before any investigation finishes. A family that has "
               "just lost its earner cannot wait for our process.",
               "जाँच पूरी होने से पहले जारी। जिस परिवार ने अभी-अभी कमाने वाला "
               "खोया है, वह हमारी प्रक्रिया का इंतज़ार नहीं कर सकता।"),
     "variant": "dark"},
], cols=4)

st.write("")
T.callout(pick(sp, "late_payment_penalty_note"))

T.spacer()

# ------------------------------------------------------------ published report
T.heading(L(f"Published record · {cr['period']}",
            f"प्रकाशित रिकॉर्ड · {pick(cr, 'period')}"),
          L("What we actually did last month.",
            "पिछले महीने हमने असल में क्या किया।"),
          L("Published every month whether it flatters us or not. If the "
            "settlement ratio falls, it falls here first.",
            "हर महीने प्रकाशित — चाहे हमारे पक्ष में हो या नहीं। अगर सेटलमेंट "
            "अनुपात गिरेगा, तो सबसे पहले यहीं दिखेगा।"))
st.write("")

T.stats([
    (f"{cr['claims_received']:,}", L("claims received", "क्लेम मिले"),
     L(f"{cr['claims_paid']:,} paid", f"{cr['claims_paid']:,} का भुगतान")),
    (f"{cr['settlement_ratio']:.1%}", L("settlement ratio", "सेटलमेंट अनुपात"),
     L(f"{cr['repudiation_rate']:.1%} declined, all reasons published below",
       f"{cr['repudiation_rate']:.1%} अस्वीकृत, सभी कारण नीचे")),
    (f"{cr['median_turnaround_hours']:.1f} {L('hrs', 'घंटे')}",
     L("median time to settle", "निपटारे का औसत समय"),
     L(f"{cr['share_settled_same_day']:.0%} same day", f"{cr['share_settled_same_day']:.0%} उसी दिन")),
    (inr(cr["total_paid_rupees"]), L("paid out", "कुल भुगतान"),
     L(f"largest single settlement {inr(cr['largest_single_settlement'])}",
       f"सबसे बड़ा एक भुगतान {inr(cr['largest_single_settlement'])}")),
])

st.write("")
g1, g2 = st.columns([1.15, 1])

with g1:
    st.markdown(f"**{L('Where the money went', 'पैसा कहाँ गया')}**")
    heads = SITE["claims_report"]["paid_by_head"]
    fig = go.Figure(go.Bar(
        x=[h["amount"] for h in heads],
        y=[pick(h, "head") for h in heads],
        orientation="h", marker_color=T.BRAND,
        text=[f"{inr(h['amount'])}  ·  {h['count']:,}" for h in heads],
        textposition="outside",
        hovertemplate="%{y}<br>%{text}<extra></extra>"))
    fig.update_layout(height=310, margin=dict(l=0, r=120, t=6, b=0),
                      xaxis=dict(showticklabels=False), yaxis=dict(autorange="reversed"),
                      plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
    st.caption(L(
        "The largest single line is income replacement, not hospital bills. "
        "That is the whole thesis of the product showing up in the loss data.",
        "सबसे बड़ी लाइन अस्पताल के बिल नहीं, कमाई की भरपाई है। प्रोडक्ट की "
        "पूरी सोच यही, नुक़सान के आँकड़ों में दिखती हुई।"))

with g2:
    st.markdown(f"**{L('Why we said no', 'हमने क्यों मना किया')}**")
    rej = cr["rejection_reasons"]
    fig2 = go.Figure(go.Bar(
        x=[r["share"] for r in rej], y=[pick(r, "reason") for r in rej],
        orientation="h", marker_color="#E2653A",
        text=[f"{r['share']:.0%}" for r in rej], textposition="outside"))
    fig2.update_layout(height=310, margin=dict(l=0, r=44, t=6, b=0),
                       xaxis=dict(showticklabels=False, range=[0, 0.55]),
                       yaxis=dict(autorange="reversed"),
                       plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig2, use_container_width=True)
    st.caption(L(
        f"{cr['repudiation_rate']:.1%} of settled claims were declined. Nearly "
        "half of those were riders who had not turned cover on. That is a "
        "product problem as much as a claims one, and it is why the app nags "
        "you when it sees you riding uncovered.",
        f"निपटे क्लेम में से {cr['repudiation_rate']:.1%} अस्वीकृत हुए। इनमें "
        "क़रीब आधे वे थे जिन्होंने कवर चालू ही नहीं किया था। यह क्लेम जितनी "
        "प्रोडक्ट की भी समस्या है — इसीलिए ऐप आपको टोकता है जब वह बिना कवर के "
        "चलते हुए देखता है।"))

T.spacer()

# ------------------------------------------------------------ what we need
T.heading(L("What we need from you", "आपसे क्या चाहिए"),
          L("Three things, and two of them are collected before anything goes wrong.",
            "तीन चीज़ें — और दो तो कुछ गलत होने से पहले ही ले ली जाती हैं।"))
st.write("")
T.cards([
    {"icon": "📸", "title": L("Four photos of your bike, at sign-up",
                              "साइन-अप पर गाड़ी की चार फ़ोटो"),
     "body": L("Taken once, when nothing is wrong. This is what removes the "
               "argument about pre-existing damage later.",
               "एक बार, जब सब ठीक हो। बाद में पुराने नुक़सान पर होने वाली बहस "
               "यही ख़त्म करती है।")},
    {"icon": "🛰️", "title": L("Cover switched on while you ride",
                              "चलाते समय कवर चालू"),
     "body": L("One tap when you start a shift. This is the single most common "
               "reason a claim fails, so the app reminds you when it detects "
               "riding with cover off.",
               "शिफ़्ट शुरू करते समय एक टैप। क्लेम फ़ेल होने की सबसे आम वजह यही "
               "है, इसलिए बिना कवर चलते देखकर ऐप याद दिलाता है।")},
    {"icon": "🩻", "title": L("Medical evidence, for injury claims only",
                              "सिर्फ़ चोट के क्लेम पर मेडिकल सबूत"),
     "body": L("An X-ray or a panel-doctor note. Nothing else — no FIR for a "
               "fracture, no estimate for a bike repair, no witness statement.",
               "एक्स-रे या पैनल डॉक्टर का पर्चा। और कुछ नहीं — फ्रैक्चर पर FIR "
               "नहीं, गाड़ी की मरम्मत का एस्टीमेट नहीं, गवाही नहीं।")},
], cols=3)

T.spacer()

# ------------------------------------------------------------------- appeals
a1, a2 = st.columns([1.3, 1])
with a1:
    T.heading(L("If we say no", "अगर हम मना करें"),
              L("You get the reason, the evidence, and a free appeal.",
                "आपको कारण, सबूत और मुफ़्त अपील — तीनों मिलते हैं।"),
              L("A decline arrives in writing in your language, with the ride "
                "data we relied on attached. You can appeal at no cost. If we "
                "get it wrong again, escalation to the Insurance Ombudsman is "
                "also free and we tell you exactly how to do it — including "
                "where our own decision was weak.",
                "अस्वीकृति आपकी भाषा में लिखित में आती है, साथ में वह राइड डेटा "
                "जिस पर हमने भरोसा किया। अपील मुफ़्त है। अगर हम फिर भी ग़लत हों "
                "तो बीमा लोकपाल तक जाना भी मुफ़्त है, और हम आपको ठीक-ठीक बताते "
                "हैं कि कैसे — यह भी कि हमारा फ़ैसला कहाँ कमज़ोर था।"))
with a2:
    T.cards([
        {"icon": "⚖️", "title": L("Ombudsman complaints last month",
                                  "पिछले महीने लोकपाल शिकायतें"),
         "amount": f"{cr['ombudsman_complaints']}",
         "amount_note": L(f"of {cr['claims_received']:,} claims",
                          f"{cr['claims_received']:,} क्लेम में से"),
         "body": L("Published with the claims report every month, alongside how "
                   "long each one has been open.",
                   "हर महीने क्लेम रिपोर्ट के साथ प्रकाशित, यह भी कि हर शिकायत "
                   "कितने दिन से खुली है।"), "variant": "cream"}], cols=1)

T.spacer()
C.closing_cta(key="cl_close")
C.footer()
