"""
Pricing.

Two things have to happen on this page. A rider has to be able to find their
own number in about ten seconds, and a sceptic has to be able to audit it. So
the calculator is first and the full filed rating basis is published below it —
every multiplier, the governance band, and the loads. An insurer that prices by
the hour and will not show the factors is just an insurer with a slider.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from shared import light, inr
from engine import pricing
from engine.config import CFG
from web import theme as T, chrome as C, quote as Q
from web.i18n import L
from web.content import SITE, pick

C.utility_bar()

v = Q.visitor()
band = pricing.price_band(
    pricing.RiderProfile(sum_insured=Q.TIERS["GigSure Plus"]["sum_insured_reference"]))

st.html(T.hero(
    L("Pricing", "क़ीमत"),
    L("₹1.50 to ₹5.50 an hour. You see <em>why</em>, before you pay it.",
      "₹1.50 से ₹5.50 प्रति घंटा। भुगतान से पहले आप <em>वजह</em> देखते हैं।"),
    L("Premium follows exposure, not the calendar. Every fifteen minutes you "
      "ride becomes a unit of exposure — weighted for the time of day, the "
      "weather, the traffic where you are, and how you ride. One unit is an "
      "hour of ordinary daytime riding in fair weather. An hour at 10pm in "
      "heavy Bengaluru rain is about 2.2 units. Nothing is hidden and nothing "
      "is rounded in our favour.",
      "प्रीमियम कैलेंडर से नहीं, जोखिम से चलता है। आपके चलाए हर पंद्रह मिनट एक "
      "एक्सपोज़र यूनिट बनते हैं — समय, मौसम, ट्रैफ़िक और आपके चलाने के तरीक़े "
      "के हिसाब से। एक यूनिट यानी साफ़ मौसम में दिन का एक सामान्य घंटा। बेंगलुरु "
      "की तेज़ बारिश में रात 10 बजे का एक घंटा लगभग 2.2 यूनिट है। न कुछ छुपा "
      "है, न कुछ हमारे फ़ायदे में गोल किया गया है।"),
    badges=[
        L(f"Floor ₹{band['floor_per_hour']:.2f} · ceiling ₹{band['ceiling_per_hour']:.2f}",
          f"न्यूनतम ₹{band['floor_per_hour']:.2f} · अधिकतम ₹{band['ceiling_per_hour']:.2f}"),
        L("₹0 on a day you do not ride", "जिस दिन न चलाएँ — ₹0"),
        L("Debited each evening by UPI Autopay", "हर शाम UPI ऑटोपे से कटौती"),
        L("Cancel in two taps", "दो टैप में बंद"),
    ],
    compact=True))

st.write("")
T.spacer(0.9)

# ------------------------------------------------------------------ calculator
T.heading(L("Your price", "आपका रेट"),
          L("Answer four questions. This is the live rating engine.",
            "चार सवालों के जवाब दीजिए। यह असली रेटिंग इंजन है।"),
          L("The same function prices our entire in-force book. No marketing "
            "estimate sits between you and the number.",
            "यही फ़ंक्शन हमारी पूरी चालू बुक की क़ीमत तय करता है। आपके और इस "
            "आँकड़े के बीच कोई विज्ञापन वाला अनुमान नहीं है।"))
st.write("")

c = st.columns(4)
v["hours_pm"] = c[0].slider(L("Hours a month", "महीने में घंटे"), 20, 280,
                            int(v["hours_pm"]), 10, key="pr_hours")
v["city"] = c[1].selectbox(L("Where you ride", "कहाँ चलाते हैं"),
                           list(CFG["city"].keys()),
                           index=list(CFG["city"]).index(v["city"]), key="pr_city")
v["platform"] = c[2].selectbox(L("Mostly for", "ज़्यादातर किसके लिए"),
                               list(CFG["platform"].keys()),
                               index=list(CFG["platform"]).index(v["platform"]),
                               key="pr_plat")
v["vehicle"] = c[3].selectbox(L("Your vehicle", "आपकी गाड़ी"),
                              list(CFG["vehicle"].keys()),
                              index=list(CFG["vehicle"]).index(v["vehicle"]),
                              key="pr_veh")

c2 = st.columns(4)
tband = c2[0].selectbox(L("When you mostly ride", "ज़्यादातर कब चलाते हैं"),
                        list(CFG["time_of_day"].keys()), index=2, key="pr_time")
wx = c2[1].selectbox(L("Weather", "मौसम"), list(CFG["weather"].keys()),
                     index=0, key="pr_wx")
v["score"] = c2[2].slider(L("Your riding score", "आपका राइडिंग स्कोर"), 30, 100,
                          int(v["score"]), 1, key="pr_score",
                          help=L("Built from braking, cornering, speed and "
                                 "screen-on-while-moving. Everyone starts at 78.",
                                 "ब्रेक, मोड़, रफ़्तार और चलते समय स्क्रीन से "
                                 "बनता है। सब 78 से शुरू करते हैं।"))
v["shift_len"] = c2[3].slider(L("Typical shift length", "आम शिफ़्ट कितनी लंबी"),
                              3.0, 12.0, float(v["shift_len"]), 0.5, key="pr_shift")

qs = {t: Q.price(t, v, time_band=tband, weather=wx) for t in Q.TIERS}
plus = qs["GigSure Plus"]

st.write("")
pc = st.columns(len(qs) + 1)
for i, (tier, q) in enumerate(qs.items()):
    with pc[i]:
        st.html(f"""
        <div class='gs gs-card {'accent' if tier == 'GigSure Plus' else ''}'>
          <div style='font-size:.72rem;font-weight:800;letter-spacing:.1em;
                      text-transform:uppercase;color:#FF6A35;height:1rem'>
            {L('Most riders', 'ज़्यादातर राइडर') if tier == 'GigSure Plus' else ''}</div>
          <h3 style='margin-top:.35rem'>{tier.replace('GigSure ', '')}</h3>
          <div class='amt'>₹{q['premium_per_hour']:.2f}
            <small>{L('an hour', 'प्रति घंटा')}</small></div>
          <p><b>{inr(q['premium_month'])}</b> {L('a month', 'महीना')} ·
             {inr(q['premium_year'])} {L('a year', 'साल')}<br>
             {L('Cover up to', 'कवर')}
             {inr(Q.TIERS[tier]['sum_insured_reference'])}</p>
        </div>""")

sp = CFG["shift_pass"]
with pc[-1]:
    st.html(f"""
    <div class='gs gs-card sand'>
      <div style='height:1rem'></div>
      <h3 style='margin-top:.35rem'>Shift Pass</h3>
      <div class='amt'>₹{sp['price']}
        <small>{L('one shift', 'एक शिफ़्ट')}</small></div>
      <p>{L(f"{sp['hours']} hours of Basic cover, bought for a single shift. For "
            "riders who work in their free time and cannot commit to a month.",
            f"{sp['hours']} घंटे का Basic कवर, सिर्फ़ एक शिफ़्ट के लिए। उन "
            "राइडर के लिए जो खाली समय में चलाते हैं।")}</p>
    </div>""")

st.write("")
C.cta_row(key="pr_calc")
T.spacer(1.2)

# ------------------------------------------------------------- flat comparison
fc1, fc2 = st.columns([1.15, 1])
with fc1:
    T.heading(L("Against a flat policy", "फ़्लैट पॉलिसी के मुक़ाबले"),
              L("Where usage pricing wins, and where it does not.",
                "यूज़-आधारित क़ीमत कहाँ फ़ायदे में है, कहाँ नहीं।"))
    flat = Q.flat_annual("GigSure Plus")
    hours_axis = list(range(20, 281, 10))
    usage = []
    for h in hours_axis:
        vv = dict(v, hours_pm=h)
        usage.append(Q.price("GigSure Plus", vv, time_band=tband,
                             weather=wx)["premium_year"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours_axis, y=[flat] * len(hours_axis), mode="lines",
        name=L("A flat annual policy", "फ़्लैट सालाना पॉलिसी"),
        line=dict(color="#9FB5B2", width=2, dash="dash")))
    fig.add_trace(go.Scatter(
        x=hours_axis, y=usage, mode="lines",
        name=L("GigSure Plus, by the hour", "GigSure Plus, घंटे के हिसाब से"),
        line=dict(color=T.BRAND, width=3)))
    fig.add_trace(go.Scatter(
        x=[v["hours_pm"]], y=[plus["premium_year"]], mode="markers+text",
        marker=dict(size=13, color=T.ACCENT, line=dict(color="#fff", width=2)),
        text=[L(f"  you · {inr(plus['premium_year'])}",
                f"  आप · {inr(plus['premium_year'])}")],
        textposition="middle right", textfont=dict(size=12, color=T.INK),
        showlegend=False))
    fig.update_layout(
        height=300, margin=dict(l=0, r=0, t=30, b=0),
        yaxis_title=L("A year of cover (₹)", "साल भर के कवर का ख़र्च (₹)"),
        xaxis_title=L("Hours ridden a month", "महीने में चलाए गए घंटे"),
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=1.16, x=0))
    st.plotly_chart(light(fig), use_container_width=True,
                    theme=None)
    st.caption(L(
        f"A flat annual policy has to be priced for a full-time rider — about "
        f"{Q.FLAT_HOURS_PM} hours a month — because the insurer cannot tell who "
        "is light and who is heavy. Everyone to the left of the crossing point "
        "is subsidising everyone to the right, which is why light riders never "
        "buy annual cover and why the riders who do buy it are the expensive "
        "ones. Usage pricing removes the subsidy in both directions.",
        f"फ़्लैट सालाना पॉलिसी को पूरे समय चलाने वाले राइडर — लगभग "
        f"{Q.FLAT_HOURS_PM} घंटे महीना — के हिसाब से क़ीमत तय करनी पड़ती है, "
        "क्योंकि कंपनी को पता ही नहीं चलता कौन कम चलाता है। कटान बिंदु के बाएँ "
        "हर कोई दाएँ वालों की सब्सिडी भर रहा है — इसीलिए कम चलाने वाले सालाना "
        "कवर कभी नहीं ख़रीदते। यूज़-आधारित क़ीमत यह सब्सिडी दोनों तरफ़ से हटा "
        "देती है।"))

with fc2:
    T.heading("", L("Where your rate can go", "आपका रेट कहाँ तक जा सकता है"))
    g = go.Figure(go.Indicator(
        mode="gauge+number", value=plus["premium_per_hour"],
        number={"prefix": "₹", "suffix": "/hr", "font": {"size": 34}},
        gauge={"axis": {"range": [0, band["ceiling_per_hour"] * 1.08],
                        "tickprefix": "₹"},
               "bar": {"color": T.BRAND, "thickness": 0.75},
               "steps": [
                   {"range": [0, band["floor_per_hour"]], "color": "#EEF3F2"},
                   {"range": [band["floor_per_hour"], band["base_per_hour"]],
                    "color": "#DDEBE9"},
                   {"range": [band["base_per_hour"], band["ceiling_per_hour"]],
                    "color": "#FFEDE4"}]}))
    g.update_layout(height=245, margin=dict(l=20, r=20, t=10, b=0))
    st.plotly_chart(light(g), use_container_width=True,
                    theme=None)
    st.caption(L(
        f"Whatever the conditions, GigSure Plus never charges more than "
        f"₹{band['ceiling_per_hour']:.2f} an hour. On the worst night of the "
        "monsoon we absorb the rest rather than pricing you out of cover.",
        f"मौसम कैसा भी हो, GigSure Plus कभी ₹{band['ceiling_per_hour']:.2f} "
        "प्रति घंटे से ज़्यादा नहीं लेता। बारिश की सबसे ख़राब रात में बाक़ी "
        "बोझ हम उठाते हैं, आपको कवर से बाहर नहीं करते।"))

if plus["was_capped"]:
    T.callout(L(
        "These conditions have pushed your risk past the governance band, so "
        "your price has been <b>capped</b>. This is a filed control, not a "
        "goodwill gesture — we are not permitted to price outside the band.",
        "इन परिस्थितियों में आपका जोखिम गवर्नेंस बैंड से बाहर चला गया, इसलिए "
        "आपका रेट <b>सीमित</b> कर दिया गया है। यह दर्ज नियम है, कोई एहसान नहीं "
        "— बैंड के बाहर क़ीमत तय करने की हमें इजाज़त ही नहीं।"))

T.spacer()

# ------------------------------------------------------------ how it is built
T.heading(L("How the number is built", "यह आँकड़ा कैसे बनता है"),
          L("Three layers, and then a limit", "तीन परतें, और फिर एक सीमा"))
st.write("")

exp = plus["exposure"]
T.cards([
    {"icon": "clock", "title": L("1 · The hour you rode", "1 · आपने जो घंटा चलाया"),
     "amount": f"×{exp['combined_exposure_multiplier']:.2f}",
     "amount_note": L("on your inputs", "आपके इनपुट पर"),
     "body": L(f"Time of day ×{exp['m_time']:.2f}, weather ×{exp['m_weather']:.2f}, "
               f"city ×{exp['m_geo']:.2f}. Measured in fifteen-minute blocks, "
               "so a short evening shift is not charged as a long one.",
               f"समय ×{exp['m_time']:.2f}, मौसम ×{exp['m_weather']:.2f}, शहर "
               f"×{exp['m_geo']:.2f}। पंद्रह-पंद्रह मिनट के हिसाब से, ताकि छोटी "
               "शाम की शिफ़्ट पर लंबी का पैसा न लगे।")},
    {"icon": "gauge", "title": L("2 · How you ride", "2 · आप कैसे चलाते हैं"),
     "amount": f"×{plus['multipliers']['M_behaviour']['value']:.2f}",
     "amount_note": L(f"score {v['score']:.0f}", f"स्कोर {v['score']:.0f}"),
     "body": L("Harsh braking, cornering, speeding and screen-on-while-moving. "
               "A score above 90 earns a 20% discount. This is the only factor "
               "you can move this week.",
               "तेज़ ब्रेक, मोड़, रफ़्तार और चलते समय स्क्रीन। 90 से ऊपर स्कोर "
               "पर 20% छूट। इसी एक चीज़ को आप इसी हफ़्ते बदल सकते हैं।")},
    {"icon": "doc", "title": L("3 · Who you are", "3 · आप कौन हैं"),
     "amount": f"×{plus['rating_product'] / plus['multipliers']['M_behaviour']['value']:.2f}",
     "amount_note": L("age, vehicle, work type", "उम्र, गाड़ी, काम का प्रकार"),
     "body": L("Age band, engine size, and what you deliver — ten-minute "
               "grocery work carries 25% more risk than food delivery, and the "
               "price says so.",
               "उम्र, इंजन का आकार, और आप क्या पहुँचाते हैं — दस-मिनट वाली "
               "ग्रॉसरी डिलीवरी में फ़ूड डिलीवरी से 25% ज़्यादा जोखिम है, और "
               "क़ीमत यही कहती है।")},
    {"icon": "shield", "title": L("4 · The governance band", "4 · गवर्नेंस बैंड"),
     "amount": f"{CFG['multiplier_cap']['floor']:.1f}× – {CFG['multiplier_cap']['ceiling']:.1f}×",
     "amount_note": L("a filed limit", "दर्ज सीमा"),
     "body": L("Everything above multiplies together and is then held inside "
               "this band. Beyond it we do not charge more — we offer a safety "
               "intervention or decline, because pricing a worker out of cover "
               "defeats the purpose.",
               "ऊपर की सब चीज़ें गुणा होती हैं और फिर इसी बैंड के अंदर रोक दी "
               "जाती हैं। उससे आगे हम ज़्यादा नहीं लेते — सेफ़्टी सलाह देते हैं "
               "या मना करते हैं, क्योंकि किसी को क़ीमत से कवर से बाहर करना "
               "पूरा मक़सद ही ख़त्म कर देता है।")},
], cols=4)

st.write("")
st.caption(L(
    "Premium = base rate × (sum insured ÷ ₹1,00,000) × hours × capped total "
    "multiplier × (1 − loyalty discount) × (1 + expense load) × (1 + margin "
    f"load).  Expense load {CFG['loadings']['expense']:.0%}, margin load "
    f"{CFG['loadings']['margin']:.0%}, loyalty up to "
    f"{max(CFG['loyalty_discount'].values()):.0%} after two years.",
    "प्रीमियम = बेस रेट × (बीमा राशि ÷ ₹1,00,000) × घंटे × सीमित कुल मल्टिप्लायर "
    f"× (1 − वफ़ादारी छूट) × (1 + ख़र्च लोड) × (1 + मार्जिन लोड)।  ख़र्च लोड "
    f"{CFG['loadings']['expense']:.0%}, मार्जिन लोड {CFG['loadings']['margin']:.0%}, "
    f"दो साल बाद {max(CFG['loyalty_discount'].values()):.0%} तक वफ़ादारी छूट।"))

T.spacer()

# ------------------------------------------------------- the published factors
T.heading(L("Published in full", "पूरा प्रकाशित"),
          L("Every factor we use, and its exact value",
            "हम जो भी फ़ैक्टर इस्तेमाल करते हैं, उसका ठीक-ठीक मान"),
          L("An insurer that prices dynamically and will not publish its "
            "factors is asking you to trust a black box. These are ours.",
            "जो बीमा कंपनी रेट बदलती रहे और अपने फ़ैक्टर न छापे, वह आपसे एक "
            "बंद डिब्बे पर भरोसा माँग रही है। ये हमारे हैं।"))
st.write("")


def factor_table(title: str, mapping: dict, note: str = ""):
    df = pd.DataFrame({L("Band", "श्रेणी"): list(mapping.keys()),
                       L("Multiplier", "मल्टिप्लायर"): [f"×{x:.2f}" for x in mapping.values()]})
    st.markdown(f"**{title}**")
    st.dataframe(df, hide_index=True, width="stretch")
    if note:
        st.caption(note)


f1, f2, f3 = st.columns(3)
with f1:
    factor_table(L("Time of day", "समय"), CFG["time_of_day"])
    factor_table(L("Weather", "मौसम"), CFG["weather"])
with f2:
    factor_table(L("City", "शहर"), CFG["city"])
    factor_table(L("Riding score", "राइडिंग स्कोर"), CFG["safety_score_bands"],
                 L("Above 90 is a 20% discount. Below 50 we would rather coach "
                   "you than charge you — you get a free safety module first.",
                   "90 से ऊपर 20% छूट। 50 से नीचे हम क़ीमत बढ़ाने से पहले आपको "
                   "मुफ़्त सेफ़्टी मॉड्यूल देते हैं।"))
with f3:
    factor_table(L("Age", "उम्र"), CFG["age"])
    factor_table(L("Vehicle", "गाड़ी"), CFG["vehicle"])

f4, f5, f6 = st.columns(3)
with f4:
    factor_table(L("What you deliver", "आप क्या पहुँचाते हैं"), CFG["platform"])
with f5:
    factor_table(L("Hours ridden without a break", "बिना ब्रेक चलाए घंटे"),
                 CFG["fatigue"])
with f6:
    factor_table(L("Loyalty discount", "वफ़ादारी छूट"),
                 {f"{k} {L('months', 'महीने')}": 1 - x
                  for k, x in CFG["loyalty_discount"].items()},
                 L("Shown as a multiplier for consistency: 0.95 is a 5% "
                   "discount.", "एकरूपता के लिए मल्टिप्लायर में: 0.95 यानी 5% छूट।"))

T.spacer()

# ---------------------------------------------------------------------- FAQ
T.heading(L("Questions", "सवाल"),
          L("What riders ask about the price", "क़ीमत पर राइडर क्या पूछते हैं"))
st.write("")
for f in SITE["faqs"][:5]:
    with st.expander(pick(f, "q")):
        st.write(pick(f, "a"))

T.spacer()
C.closing_cta(key="pr_close")
C.footer()
