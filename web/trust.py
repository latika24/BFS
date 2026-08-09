"""
Trust and compliance.

A worker being asked to hand over location data and a UPI mandate to a company
they have not heard of needs three questions answered: are you actually allowed
to do this, what happens to my data, and what happens if you go under. This
page answers all three in plain language, and does not pretend the registration
is finished when it is not.
"""
from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from shared import inr
from engine.config import CFG
from web import theme as T, chrome as C
from web.i18n import L
from web.content import SITE, pick

C.utility_bar()

cr = SITE["claims_report"]
sol = CFG["portfolio"]["solvency"]

st.html(T.hero(
    L("Trust", "भरोसा"),
    L("Ask us the three questions you should ask any insurer.",
      "किसी भी बीमा कंपनी से जो तीन सवाल पूछने चाहिए, हमसे पूछिए।"),
    L("Are you allowed to do this. What happens to my data. What happens if you "
      "run out of money. Most insurance marketing answers none of them. Ours "
      "starts with them, including the parts that are still in progress.",
      "क्या आपको इसकी इजाज़त है। मेरे डेटा का क्या होगा। पैसा ख़त्म हो जाए तो "
      "क्या होगा। ज़्यादातर बीमा विज्ञापन इनमें से एक का भी जवाब नहीं देते। हम "
      "इन्हीं से शुरू करते हैं — उन बातों समेत जो अभी अधूरी हैं।"),
    compact=True))

T.spacer(1.2)

# ------------------------------------------------------------------- register
T.heading(L("Where we stand", "हम कहाँ खड़े हैं"),
          L("The compliance register, including what is not done yet",
            "अनुपालन का ब्यौरा, उन चीज़ों समेत जो अभी बाक़ी हैं"))
st.write("")

for item in SITE["compliance"]:
    with st.expander(f"**{pick(item, 'item')}** · {item['status']}"):
        st.write(item["detail"].strip())

st.write("")
T.callout(L(
    "Being honest about the obvious one: GigSure is not yet an authorised "
    "insurer. Registration under the Insurance Act, 1938 runs through Forms R1, "
    "R2 and R3 and takes around eighteen months, and no cover can be sold "
    "before it completes. This site and this app are a working prototype of the "
    "product we intend to file.",
    "साफ़ बात: GigSure अभी अधिकृत बीमा कंपनी नहीं है। बीमा अधिनियम, 1938 के तहत "
    "पंजीकरण फ़ॉर्म R1, R2 और R3 से होकर गुज़रता है और लगभग अठारह महीने लेता है; "
    "उसके पूरा होने से पहले कोई कवर नहीं बेचा जा सकता। यह साइट और यह ऐप उसी "
    "प्रोडक्ट का चालू प्रोटोटाइप है जिसे हम दाख़िल करने जा रहे हैं।"))

T.spacer()

# ----------------------------------------------------------------- your data
d1, d2 = st.columns([1.2, 1])
with d1:
    T.heading(L("Your data", "आपका डेटा"),
              L("Four rules we wrote down before we wrote any code.",
                "चार नियम, जो कोड लिखने से पहले लिखे गए।"),
              L("Location data makes us a data fiduciary under the Digital "
                "Personal Data Protection Act, 2023. That is a legal obligation, "
                "but these rules go further than it requires.",
                "लोकेशन डेटा हमें डिजिटल पर्सनल डेटा प्रोटेक्शन एक्ट, 2023 के "
                "तहत डेटा फ़िड्यूशरी बनाता है। यह क़ानूनी ज़िम्मेदारी है, पर ये "
                "नियम उससे भी आगे जाते हैं।"))
    st.write("")
    T.rows([
        (L("Withdraw consent and keep your cover",
           "सहमति वापस लें, कवर बना रहेगा"),
         L("You move to a flat book rate. Your policy does not lapse, not for a "
           "minute.", "आप फ़्लैट रेट पर आ जाते हैं। पॉलिसी एक मिनट के लिए भी बंद "
           "नहीं होती।"), L("Always", "हमेशा"), ""),
        (L("We never sell your score to a platform",
           "आपका स्कोर किसी प्लेटफ़ॉर्म को कभी नहीं बेचा जाएगा"),
         L("They would deactivate the riders we score as high-risk. That would "
           "be the end of anyone consenting to be measured, and the end of the "
           "product.",
           "वे उन्हीं राइडर को हटा देंगे जिन्हें हम ज़्यादा जोखिम वाला बताएँ। "
           "फिर कोई मापे जाने को राज़ी नहीं होगा, और प्रोडक्ट ख़त्म।"),
         L("Never", "कभी नहीं"), ""),
        (L("We only record while cover is on",
           "रिकॉर्डिंग सिर्फ़ कवर चालू रहते हुए"),
         L("Off duty, the SDK is not collecting. Your evening is not our data.",
           "ड्यूटी ख़त्म, SDK कुछ इकट्ठा नहीं करता। आपकी शाम हमारा डेटा नहीं है।"),
         L("On-shift only", "सिर्फ़ शिफ़्ट में"), ""),
        (L("Aggregate road-risk data may be sold from year five",
           "पाँचवें साल से सामूहिक रोड-रिस्क डेटा बेचा जा सकता है"),
         L("To fleet operators, road-safety bodies and other insurers, in "
           "aggregate form only. Never an individual record, never to a "
           "platform that employs you.",
           "फ़्लीट ऑपरेटर, सड़क-सुरक्षा संस्थाओं और दूसरी बीमा कंपनियों को, "
           "सिर्फ़ सामूहिक रूप में। कभी कोई व्यक्तिगत रिकॉर्ड नहीं, और कभी उस "
           "प्लेटफ़ॉर्म को नहीं जो आपको काम देता है।"),
         L("Aggregate only", "सिर्फ़ सामूहिक"), ""),
    ])

with d2:
    T.cards([
        {"icon": "lock", "title": L("The design rule", "बुनियादी नियम"),
         "body": L("Revoking telematics consent reverts you to a flat book rate "
                   "and never lapses cover. It is written into the product, not "
                   "into a support script — which is why it survives a bad "
                   "quarter.",
                   "टेलीमैटिक्स सहमति वापस लेने पर आप फ़्लैट रेट पर आते हैं और "
                   "कवर कभी बंद नहीं होता। यह प्रोडक्ट में लिखा है, किसी सपोर्ट "
                   "स्क्रिप्ट में नहीं — इसीलिए यह ख़राब तिमाही में भी टिकता है।"),
         "variant": "dark"},
        {"icon": "globe", "title": L("Support in your language",
                                  "आपकी भाषा में सहायता"),
         "body": L("Eight languages, voice-first, because a claim form in "
                   "English is a claim that does not get made.",
                   "आठ भाषाएँ, पहले आवाज़ — क्योंकि अंग्रेज़ी वाला क्लेम फ़ॉर्म "
                   "वह क्लेम है जो कभी होता ही नहीं।"),
         "variant": "cream"},
    ], cols=1)

T.spacer()

# ------------------------------------------------------------------- solvency
T.heading(L("If we run out of money", "अगर हमारे पास पैसा न बचे"),
          L("Solvency, and the throttle we run above the legal minimum",
            "सॉल्वेंसी, और क़ानूनी न्यूनतम से ऊपर हमारी अपनी रोक"),
          L("An insurer that writes more business than its capital supports is "
            "how claims stop being paid. The statutory floor is 150%. We hold a "
            "target of 200% and stop writing new business at 180% rather than "
            "growing into trouble.",
            "जो बीमा कंपनी अपनी पूँजी से ज़्यादा कारोबार लिखती है, वहीं क्लेम "
            "रुकने लगते हैं। क़ानूनी न्यूनतम 150% है। हम 200% का लक्ष्य रखते हैं "
            "और 180% पर नया कारोबार रोक देते हैं।"),
          wide=True)
st.write("")

fig = go.Figure()
for label, val, colour in [
        (L("Statutory minimum", "क़ानूनी न्यूनतम"), sol["statutory_ratio"], "#C9D6D4"),
        (L("Our internal throttle", "हमारी अंदरूनी रोक"), sol["internal_throttle_ratio"], T.ACCENT),
        (L("Our target", "हमारा लक्ष्य"), sol["target_ratio"], T.BRAND)]:
    fig.add_trace(go.Bar(x=[val * 100], y=[label], orientation="h",
                         marker_color=colour, text=[f"{val:.0%}"],
                         textposition="outside", showlegend=False,
                         hovertemplate="%{y}: %{text}<extra></extra>"))
fig.update_layout(height=210, margin=dict(l=0, r=60, t=8, b=0), barmode="group",
                  xaxis=dict(showticklabels=False), plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, use_container_width=True)

st.write("")
T.stats([
    (inr(CFG["portfolio"]["solvency"]["rsm_floor_cr"] * 1e7),
     L("minimum capital held", "न्यूनतम पूँजी"),
     L("required solvency margin floor", "आवश्यक सॉल्वेंसी मार्जिन की तली")),
    ("₹100 cr", L("paid-up equity required", "आवश्यक चुकता पूँजी"),
     L("Section 6, Insurance Act 1938", "धारा 6, बीमा अधिनियम 1938")),
    (f"{CFG['portfolio']['quota_share_cession']:.0%}",
     L("of risk reinsured", "जोखिम का पुनर्बीमा"),
     L("a quota-share treaty, so a bad month is not your problem",
       "कोटा-शेयर संधि, ताकि ख़राब महीना आपकी समस्या न बने")),
    (f"{cr['ombudsman_complaints']}",
     L("ombudsman complaints last month", "पिछले महीने लोकपाल शिकायतें"),
     L("published with every claims report", "हर क्लेम रिपोर्ट के साथ प्रकाशित")),
])

T.spacer()

# -------------------------------------------------------------------- who
T.heading(L("Who is behind this", "इसके पीछे कौन है"),
          L("An academic prototype, stated plainly.",
            "एक अकादमिक प्रोटोटाइप, साफ़-साफ़।"))
st.write("")
T.cards([
    {"icon": "people", "title": L("Built at IIM Ahmedabad",
                              "IIM अहमदाबाद में बना"),
     "body": L("Group 6, Banking and Financial Services, PGP-II Term IV, under "
               "Prof. Balagopal Gopalakrishnan. The business plan behind every "
               "number on this site is a course submission, August 2026.",
               "ग्रुप 6, बैंकिंग एंड फ़ाइनेंशियल सर्विसेज़, PGP-II टर्म IV, "
               "प्रो. बालगोपाल गोपालकृष्णन के अंतर्गत। इस साइट के हर आँकड़े के "
               "पीछे का बिज़नेस प्लान अगस्त 2026 का कोर्स सबमिशन है।")},
    {"icon": "chart", "title": L("The numbers are auditable",
                              "आँकड़े जाँचे जा सकते हैं"),
     "body": L("Every rating factor, benefit formula and financial assumption "
               "sits in two configuration files rather than in the code. The "
               "insurer console shows the same book the website sells from.",
               "हर रेटिंग फ़ैक्टर, लाभ का फ़ॉर्मूला और वित्तीय अनुमान कोड में "
               "नहीं, दो कॉन्फ़िगरेशन फ़ाइलों में है। इंश्योरर कंसोल वही बुक "
               "दिखाता है जिससे वेबसाइट बेचती है।")},
    {"icon": "gauge", "title": L("The book is synthetic",
                              "बुक कृत्रिम है"),
     "body": L("There is no public gig-worker telematics dataset, so the "
               "5,000-rider book is generated from distributions that match the "
               "plan. Nothing here is fitted to real loss experience, and the "
               "claims report is modelled steady state.",
               "गिग वर्कर टेलीमैटिक्स का कोई सार्वजनिक डेटासेट नहीं है, इसलिए "
               "5,000 राइडर की बुक प्लान से मेल खाते वितरण से बनाई गई है। यहाँ "
               "कुछ भी असली नुक़सान के अनुभव पर आधारित नहीं है।")},
], cols=3)

st.write("")
tc = st.columns([1.6, 1.6, 3])
if tc[0].button(L("See the insurer console →", "इंश्योरर कंसोल देखें →"),
                width="stretch", key="tr_ops"):
    st.switch_page("views/ops_portfolio.py")
if tc[1].button(L("See the claims record →", "क्लेम रिकॉर्ड देखें →"),
                width="stretch", key="tr_cl"):
    st.switch_page(C.CLAIMS)

T.spacer()
C.closing_cta(key="tr_close")
C.footer()
