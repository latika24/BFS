"""
Refer a rider.

Referral is not a growth hack bolted onto the side here — it is a costed
acquisition channel in the plan, at ₹100 each side against a blended CAC of
₹350 and a lifetime value of ₹1,080. The page is written for the rider doing
the referring, and the unit economics are shown rather than hidden, because a
worker who understands why we pay ₹100 refers more confidently than one who
suspects a catch.
"""
from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from shared import inr
from web import theme as T, chrome as C
from web.i18n import L
from web.content import SITE, pick

C.utility_bar()

r = SITE["referral"]

st.html(T.hero(
    L("Refer a rider", "किसी राइडर को जोड़िए"),
    L(f"₹{r['reward_each_side']} to you. ₹{r['reward_each_side']} to them. "
      "<em>Every time.</em>",
      f"₹{r['reward_each_side']} आपको। ₹{r['reward_each_side']} उन्हें। "
      "<em>हर बार।</em>"),
    L(f"Riders trust riders. Send your code to your hub's WhatsApp group. When "
      f"the rider you sent it to has ridden {r['qualify_after_hours']} covered "
      f"hours, ₹{r['reward_each_side']} lands in your UPI and "
      f"₹{r['reward_each_side']} lands in theirs. Up to "
      f"₹{r['monthly_cap_per_rider']:,} a month, with no limit on how many "
      "people you tell.",
      f"राइडर, राइडर पर भरोसा करते हैं। अपने हब के WhatsApp ग्रुप में कोड "
      f"भेजिए। जिस राइडर को आपने भेजा, वह {r['qualify_after_hours']} कवर वाले "
      f"घंटे चला ले — ₹{r['reward_each_side']} आपके UPI में और "
      f"₹{r['reward_each_side']} उनके UPI में। महीने में "
      f"₹{r['monthly_cap_per_rider']:,} तक, और कितने लोगों को बताएँ इसकी कोई "
      "सीमा नहीं।"),
    badges=[
        L("Paid to UPI, not to a wallet", "UPI में, किसी वॉलेट में नहीं"),
        L("No cap on referrals", "रेफ़रल की कोई सीमा नहीं"),
        L("They get a lower first month too", "उनका पहला महीना भी सस्ता"),
    ],
    compact=True))

st.write("")
C.cta_row(L("Get covered, then refer", "पहले कवर लें, फिर रेफ़र करें"),
          C.REGISTER, L("How the price works", "क़ीमत कैसे बनती है"),
          C.PRICING, key="rf_hero")

T.spacer(1.3)

# ------------------------------------------------------------------ calculator
T.heading(L("What it adds up to", "कुल कितना बनता है"),
          L("Most riders know twenty other riders.",
            "ज़्यादातर राइडर बीस और राइडर को जानते हैं।"))
st.write("")

cc = st.columns([1, 1, 2])
n = cc[0].slider(L("Riders you refer in a year", "साल भर में कितने राइडर जोड़ेंगे"),
                 0, 40, 12, 1, key="rf_n")
take = cc[1].slider(L("How many actually sign up and ride",
                      "इनमें से कितने सचमुच जुड़ेंगे और चलाएँगे"),
                    0, 100, 45, 5, key="rf_take", format="%d%%")

converted = int(round(n * take / 100))
earned = min(converted * r["reward_each_side"], r["monthly_cap_per_rider"] * 12)

with cc[2]:
    T.rows([
        (L("Riders who sign up", "कितने जुड़ेंगे"),
         L(f"{take}% of {n}", f"{n} में से {take}%"), f"{converted}", ""),
        (L("What you earn", "आपकी कमाई"),
         L(f"₹{r['reward_each_side']} each, credited to UPI",
           f"हर एक पर ₹{r['reward_each_side']}, UPI में"),
         inr(earned), L("a year", "साल में")),
        (L("What they earn between them", "उन सबकी कुल कमाई"),
         L("the same amount, on their side", "उतनी ही रकम, उनकी तरफ़"),
         inr(converted * r["reward_each_side"]), ""),
    ])

st.write("")
T.callout(L(
    f"To put that in perspective: {inr(earned)} is roughly "
    f"{earned / 2.5:.0f} hours of GigSure Plus cover, paid for by telling "
    "people something you would probably have told them anyway.",
    f"तुलना के लिए: {inr(earned)} का मतलब है लगभग {earned / 2.5:.0f} घंटे का "
    "GigSure Plus कवर — वह भी सिर्फ़ यह बताकर जो आप शायद यूँ भी बता देते।"),
    brand=True)

T.spacer()

# -------------------------------------------------------------------- how
T.heading(L("How it works", "यह कैसे काम करता है"),
          L("Four steps, and you only do the first one.",
            "चार क़दम, और पहला ही आपको उठाना है।"))
st.write("")
T.steps([
    {"title": L("Share your code", "अपना कोड भेजें"),
     "body": L("From the app, in one tap. It sends your code with a voice note "
               "in your language, because that is what actually gets listened "
               "to in a hub group.",
               "ऐप से, एक टैप में। कोड के साथ आपकी भाषा में वॉइस नोट जाता है — "
               "हब ग्रुप में असल में यही सुना जाता है।"),
     "time": L("10 seconds", "10 सेकंड")},
    {"title": L("They sign up", "वे जुड़ते हैं"),
     "body": L("Aadhaar, vehicle number, UPI mandate. About ninety seconds, and "
               "they can start on a single Shift Pass if they are not sure.",
               "आधार, गाड़ी नंबर, UPI मैंडेट। लगभग नब्बे सेकंड — और अगर पक्का "
               "मन न हो तो वे एक Shift Pass से शुरू कर सकते हैं।"),
     "time": L("90 seconds", "90 सेकंड")},
    {"title": L(f"They ride {r['qualify_after_hours']} covered hours",
                f"वे {r['qualify_after_hours']} कवर वाले घंटे चलाते हैं"),
     "body": L("Roughly three shifts. The threshold exists so the reward goes "
               "to real riders rather than to sign-ups that never switch cover "
               "on.",
               "क़रीब तीन शिफ़्ट। यह शर्त इसलिए है कि इनाम असली राइडर को मिले, "
               "उन साइन-अप को नहीं जो कभी कवर चालू ही नहीं करते।"),
     "time": L("Usually within a week", "आमतौर पर एक हफ़्ते में")},
    {"title": L("Both of you are paid", "दोनों को पैसा"),
     "body": L(f"₹{r['reward_each_side']} to each UPI, automatically. No claim "
               "form, no coupon, no expiry.",
               f"हर एक के UPI में ₹{r['reward_each_side']}, अपने आप। न कोई "
               "फ़ॉर्म, न कूपन, न कोई मियाद।"),
     "time": L("Within 24 hours", "24 घंटे के अंदर")},
])

T.spacer()

# ------------------------------------------------------------------- channels
ch1, ch2 = st.columns([1, 1.25])
with ch1:
    T.heading(L("Where riders find us", "राइडर हमें कहाँ पाते हैं"),
              L("Three places that work", "तीन जगहें जो काम करती हैं"))
    st.write("")
    T.cards([{"icon": "💬", "title": pick(c, "name"), "body": pick(c, "note")}
             for c in r["channels"]], cols=1)

with ch2:
    T.heading(L("Why we pay you rather than an ad network",
                "हम विज्ञापन के बजाय आपको पैसा क्यों देते हैं"),
              L("It is the cheapest honest channel we have.",
                "यह हमारा सबसे सस्ता और सबसे ईमानदार रास्ता है।"))
    st.write("")
    d = SITE["distribution"]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[(c["cac_low"] + c["cac_high"]) / 2 for c in d],
        y=[pick(c, "channel") for c in d], orientation="h",
        marker_color=[T.ACCENT if "referral" in c["channel"].lower() else "#9FB5B2"
                      for c in d],
        text=[f"₹{c['cac_low']}–{c['cac_high']}" if c['cac_low'] != c['cac_high']
              else f"₹{c['cac_low']}" for c in d],
        textposition="outside", showlegend=False,
        hovertext=[c["note"] for c in d], hoverinfo="text"))
    fig.add_vline(x=r["blended_cac"], line_dash="dot", line_color="#5C6E6B",
                  annotation_text=L(f"blended ₹{r['blended_cac']}",
                                    f"औसत ₹{r['blended_cac']}"),
                  annotation_position="top")
    fig.update_layout(height=290, margin=dict(l=0, r=70, t=26, b=0),
                      xaxis=dict(showticklabels=False),
                      yaxis=dict(autorange="reversed"),
                      plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
    st.caption(L(
        f"Cost of acquiring one rider, by channel. Referral costs us "
        f"₹{r['reward_each_side'] * 2} against a lifetime value of about "
        f"₹{r['lifetime_value']:,}. We deliberately do not buy paid digital — "
        "our customer is not on those channels, and IRDAI's Expenses of "
        "Management regulations cap what an insurer may spend as a share of "
        "premium, so uncontrolled spend is a breach rather than merely a waste.",
        f"एक राइडर जोड़ने की लागत, चैनल के हिसाब से। रेफ़रल पर हमें "
        f"₹{r['reward_each_side'] * 2} लगते हैं, जबकि जीवनकाल मूल्य लगभग "
        f"₹{r['lifetime_value']:,} है। हम जानबूझकर डिजिटल विज्ञापन नहीं ख़रीदते "
        "— हमारा ग्राहक वहाँ है ही नहीं, और IRDAI के नियम प्रीमियम के अनुपात "
        "में ख़र्च की सीमा तय करते हैं।"))

T.spacer()

T.callout(L(
    f"The honest caveat: the reward is capped at ₹{r['monthly_cap_per_rider']:,} "
    "a month per rider. Not because we do not want the growth, but because an "
    "uncapped referral programme turns into a small number of people farming "
    "sign-ups that never ride — which costs the riders who do.",
    f"ईमानदार शर्त: इनाम हर राइडर के लिए महीने में "
    f"₹{r['monthly_cap_per_rider']:,} तक सीमित है। इसलिए नहीं कि हमें बढ़त नहीं "
    "चाहिए, बल्कि इसलिए कि बिना सीमा वाला रेफ़रल कुछ ही लोगों को ऐसे साइन-अप "
    "जुटाने में लगा देता है जो कभी चलाते ही नहीं — और उसका बोझ असली राइडर पर "
    "पड़ता है।"))

T.spacer()
C.closing_cta(key="rf_close")
C.footer()
