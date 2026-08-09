"""
Why GigSure.

The positioning page. It makes one argument: the useful way to sort insurance
for gig workers is by who owns the cover and what the cover protects, and the
quadrant a rider actually needs — owned by the worker, protecting the
livelihood — is empty for structural reasons rather than accidental ones. A
platform cannot sit in it without conceding responsibility for a rider's income
continuity, which is precisely the question being litigated against the
platforms in the Karnataka High Court.
"""
from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from engine.config import CFG
from web import theme as T, chrome as C
from web.i18n import L
from web.content import SITE, pick

C.utility_bar()

st.html(T.hero(
    L("Why GigSure", "GigSure क्यों"),
    L("The cover you have belongs to the app. <em>This one belongs to you.</em>",
      "जो कवर आपके पास है वह ऐप का है। <em>यह आपका है।</em>"),
    L("You are not uninsured. Platforms spend real money on rider cover, and "
      "the state offers PMSBY for ₹20 a year. The problem is not the absence of "
      "insurance — it is four structural failures in the insurance that already "
      "exists, and every one of them lands on the rider rather than on the "
      "company that arranged it.",
      "आप बिना बीमे के नहीं हैं। प्लेटफ़ॉर्म राइडर कवर पर असली पैसा ख़र्च करते "
      "हैं, और सरकार ₹20 सालाना में PMSBY देती है। दिक़्क़त बीमे की कमी नहीं है "
      "— मौजूदा बीमे की चार बुनियादी ख़ामियाँ हैं, और हर एक का बोझ राइडर पर "
      "गिरता है, उस कंपनी पर नहीं जिसने बीमा कराया।"),
    compact=True))

st.write("")
C.cta_row(key="wh_hero")
T.spacer(1.3)

# --------------------------------------------------------------- four failures
T.heading(L("The four failures", "चार ख़ामियाँ"),
          L("What is wrong, and what we did about each one",
            "क्या ग़लत है, और हमने हर एक का क्या किया"),
          wide=True)
st.write("")

for i, f in enumerate(SITE["failures"]):
    a, b = st.columns([1.15, 1])
    with a:
        st.html(f"""
        <div class='gs gs-card sand' style='height:auto'>
          <div class='gs-kicker'>{L('The problem', 'समस्या')} {i + 1}</div>
          <h3>{pick(f, 'title')}</h3>
          <p>{pick(f, 'body')}</p>
        </div>""")
    with b:
        st.html(f"""
        <div class='gs gs-card dark' style='height:auto'>
          <div class='gs-kicker' style='color:#7FE3C4'>{L('What we do', 'हम क्या करते हैं')}</div>
          <p style='font-size:1rem;line-height:1.6;color:#fff;font-weight:600'>
            {pick(f, 'fix')}</p>
        </div>""")
    st.write("")

T.spacer(0.6)

# ------------------------------------------------------------------- the map
T.heading(L("The map", "नक़्शा"),
          L("Who owns the cover, against what the cover protects",
            "कवर किसका है, और कवर किसकी रक्षा करता है"),
          L("Sorted this way, the market makes sense. The top-right quadrant — "
            "cover you own, protecting your livelihood rather than only the "
            "accident — is where a rider actually needs to be, and it is empty.",
            "इस तरह देखने पर बाज़ार समझ आता है। ऊपर-दाएँ का ख़ाना — आपका अपना "
            "कवर, जो सिर्फ़ दुर्घटना नहीं बल्कि आपकी रोज़ी की रक्षा करे — वहीं "
            "राइडर को होना चाहिए, और वह ख़ाली है।"),
          wide=True)
st.write("")

pos = CFG["positioning_map"]
xs = {"The event": 0.28, "The livelihood": 0.74}
ys = {"Platform": 0.28, "Worker": 0.74}

fig = go.Figure()
fig.add_shape(type="rect", x0=0.5, y0=0.5, x1=1.0, y1=1.0,
              fillcolor="#FFEDE4", line=dict(width=0), layer="below")
fig.add_shape(type="line", x0=0.5, y0=0, x1=0.5, y1=1,
              line=dict(color="#D5DEDC", width=1))
fig.add_shape(type="line", x0=0, y0=0.5, x1=1, y1=0.5,
              line=dict(color="#D5DEDC", width=1))

for p in pos:
    is_us = p["player"] == "Us"
    label = L("GigSure", "GigSure") if is_us else p["player"]
    fig.add_trace(go.Scatter(
        x=[xs[p["protects"]]], y=[ys[p["owner"]]], mode="markers+text",
        marker=dict(size=26 if is_us else 17,
                    color=T.ACCENT if is_us else "#8EA5A2",
                    line=dict(color="#fff", width=2)),
        text=[f"<b>{label}</b>" if is_us else label],
        textposition="middle right" if xs[p["protects"]] < 0.5 else "middle left",
        textfont=dict(size=13 if is_us else 11.5,
                      color=T.INK if is_us else "#5C6E6B"),
        hovertext=p["note"], hoverinfo="text", showlegend=False))

fig.update_layout(
    height=420, margin=dict(l=10, r=10, t=32, b=10),
    plot_bgcolor="#FBFCFC",
    xaxis=dict(range=[0, 1], showgrid=False, zeroline=False,
               tickvals=[0.25, 0.75],
               ticktext=[L("Protects the accident", "दुर्घटना की रक्षा"),
                         L("Protects your livelihood", "आपकी रोज़ी की रक्षा")],
               tickfont=dict(size=12.5, color="#3B4B48")),
    yaxis=dict(range=[0, 1], showgrid=False, zeroline=False,
               tickvals=[0.25, 0.75],
               ticktext=[L("Owned by the platform", "प्लेटफ़ॉर्म का"),
                         L("Owned by you", "आपका अपना")],
               tickfont=dict(size=12.5, color="#3B4B48")))
st.plotly_chart(fig, use_container_width=True)

T.callout(L(
    "The empty quadrant is structural, not an oversight. A platform that "
    "insures riders against loss of income has conceded that it is responsible "
    "for their income continuity — which is the argument being run against "
    "Swiggy, Zomato and Zepto in the Karnataka High Court. Our strongest "
    "product is one our largest competitors cannot build without arguing "
    "against themselves.",
    "यह ख़ाली ख़ाना संयोग नहीं, ढाँचे की वजह से ख़ाली है। जो प्लेटफ़ॉर्म राइडर "
    "को आमदनी के नुक़सान का बीमा देता है, वह मान लेता है कि उनकी आमदनी की "
    "निरंतरता की ज़िम्मेदारी उसकी है — और यही दलील कर्नाटक हाई कोर्ट में स्विगी, "
    "ज़ोमैटो और ज़ेप्टो के ख़िलाफ़ चल रही है। हमारा सबसे मज़बूत प्रोडक्ट वही है "
    "जो हमारे सबसे बड़े प्रतिद्वंद्वी अपने ही ख़िलाफ़ बोले बिना नहीं बना सकते।"))

T.spacer()

# ------------------------------------------------------------ side by side
T.heading(L("Side by side", "आमने-सामने"),
          L("Against everything else you could hold",
            "बाक़ी हर विकल्प के मुक़ाबले"))
st.write("")

T.comparison(
    ["", L("Your platform's cover", "प्लेटफ़ॉर्म का कवर"),
     L("PMSBY / a retail accident policy", "PMSBY / रिटेल दुर्घटना पॉलिसी"),
     "GigSure"],
    [
        [L("Who owns it", "किसका है"),
         L("The platform. It ends when you stop riding for them.",
           "प्लेटफ़ॉर्म का। उनके लिए चलाना बंद, कवर ख़त्म।"),
         L("You", "आपका"),
         L("You. It moves with you across every app.",
           "आपका। हर ऐप पर आपके साथ चलता है।")],
        [L("When it is live", "कब चालू रहता है"),
         L("Only while logged in to that one app", "सिर्फ़ उसी एक ऐप पर लॉग-इन रहते हुए"),
         L("Always, but only for death and disability",
           "हमेशा, पर सिर्फ़ मृत्यु और विकलांगता के लिए"),
         L("Every hour you declare a shift, on any app",
           "हर उस घंटे जब आप शिफ़्ट दर्ज करें, किसी भी ऐप पर")],
        [L("Replaces lost income", "गई हुई कमाई की भरपाई"),
         L("Rarely, and thinly", "बहुत कम, और मामूली"),
         L("No", "नहीं"),
         L("Yes — 75% of your observed daily earnings, up to 90 days",
           "हाँ — आपकी रोज़ की कमाई का 75%, 90 दिन तक")],
        [L("Covers your bike on a delivery", "डिलीवरी के दौरान गाड़ी का कवर"),
         L("No", "नहीं"),
         L("No", "नहीं"),
         L("Yes, on GigSure Pro", "हाँ, GigSure Pro पर")],
        [L("What it costs you", "आपका ख़र्च"),
         L("Nothing — and you get what you pay for",
           "कुछ नहीं — और जितना दिया उतना ही मिलता है"),
         L("₹20 a year", "₹20 सालाना"),
         L("₹1.50–₹5.50 an hour ridden, ₹0 on a day off",
           "चलाए गए घंटे पर ₹1.50–₹5.50, छुट्टी वाले दिन ₹0")],
        [L("Speed of settlement", "निपटारे की रफ़्तार"),
         L("Weeks to months, documented by rider unions",
           "हफ़्तों से महीने, यूनियनों ने दर्ज किया है"),
         L("Bank-led, slow, needs paperwork you may not have",
           "बैंक के ज़रिए, धीमा, ऐसे काग़ज़ माँगे जो शायद न हों"),
         L("Median 4.2 hours. Most heads settle with nobody involved.",
           "औसतन 4.2 घंटे। ज़्यादातर मामले बिना किसी की दख़ल के निपटते हैं।")],
        [L("If you switch platform", "प्लेटफ़ॉर्म बदलने पर"),
         L("Cover ends that day", "उसी दिन कवर ख़त्म"),
         L("Unaffected", "कोई फ़र्क़ नहीं"),
         L("Unaffected — nothing to re-apply for", "कोई फ़र्क़ नहीं — दोबारा कुछ नहीं करना")],
    ], us_col=3)

st.write("")
T.callout(L(
    "Keep the platform cover. It is free and it is worth having. Keep PMSBY "
    "too — ₹20 a year is the best value in Indian insurance. Neither of them "
    "pays your rent for the six weeks your wrist is in a cast, and that is the "
    "gap we exist to fill.",
    "प्लेटफ़ॉर्म का कवर रखिए। मुफ़्त है और रखने लायक़ है। PMSBY भी रखिए — ₹20 "
    "सालाना भारतीय बीमे का सबसे अच्छा सौदा है। पर इनमें से कोई उन छह हफ़्तों "
    "का किराया नहीं देता जब आपकी कलाई प्लास्टर में है — और हम उसी खाई को भरने "
    "के लिए हैं।"), brand=True)

T.spacer()

# ------------------------------------------------------- who we take money from
wc1, wc2 = st.columns([1.25, 1])
with wc1:
    T.heading(L("A promise about our own cap table",
                "अपने ही निवेशकों के बारे में एक वादा"),
              L("We will never take investment from a delivery platform.",
                "हम किसी डिलीवरी प्लेटफ़ॉर्म से निवेश कभी नहीं लेंगे।"),
              L("The entire proposition is that the cover follows the worker "
                "across every app. The moment one platform sits on our cap "
                "table, every other platform stops taking our calls — and the "
                "riders who trust us precisely because we are not the platform "
                "stop trusting us. A commercial partnership is fine. Equity is "
                "not, and the regulator would ask the same question at "
                "registration.",
                "पूरा प्रस्ताव यही है कि कवर हर ऐप पर वर्कर के साथ चलता है। जिस "
                "दिन एक प्लेटफ़ॉर्म हमारा हिस्सेदार बना, बाक़ी सब हमसे बात करना "
                "बंद कर देंगे — और जो राइडर हम पर इसीलिए भरोसा करते हैं कि हम "
                "प्लेटफ़ॉर्म नहीं हैं, वे भरोसा छोड़ देंगे। कारोबारी साझेदारी "
                "ठीक है। हिस्सेदारी नहीं — और नियामक भी पंजीकरण के वक़्त यही "
                "सवाल पूछेगा।"))
with wc2:
    T.cards([
        {"icon": "doc", "title": L("Our own licence, not a partner's paper",
                                  "अपना लाइसेंस, किसी और का काग़ज़ नहीं"),
         "body": L("We are pursuing IRDAI registration in our own name rather "
                   "than broking risk onto someone else's balance sheet. It is "
                   "slower and far more expensive, and it is the only way the "
                   "rating basis can change as fast as the road does.",
                   "हम किसी और की बैलेंस शीट पर जोखिम भेजने के बजाय अपने नाम से "
                   "IRDAI पंजीकरण कर रहे हैं। यह धीमा और कहीं महँगा रास्ता है, "
                   "और यही एकमात्र तरीक़ा है जिससे रेटिंग का आधार सड़क जितनी "
                   "तेज़ी से बदल सके।"), "variant": "cream"}], cols=1)
    st.write("")
    if st.button(L("See how we are regulated →", "हम किस नियम के तहत हैं →"),
                 key="wh_trust", width="stretch"):
        st.switch_page(C.TRUST)

T.spacer()
C.closing_cta(key="wh_close")
C.footer()
