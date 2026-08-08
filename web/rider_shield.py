"""
Product page — Rider Shield.

The cover on the worker rather than on the vehicle. Its centre of gravity is
the daily income benefit, because that is the loss that actually happens to a
rider: not the hospital bill, but the six weeks afterwards with nothing coming
in. Every amount on this page is computed live by `engine.sum_insured`, from
the earnings the visitor enters, so the page cannot drift from the model.
"""
from __future__ import annotations

import streamlit as st

from shared import inr
from engine.config import CFG
from web import theme as T, chrome as C, quote as Q
from web.i18n import L
from web.content import SITE, pick

C.utility_bar()

si = CFG["sum_insured"]
v = Q.visitor()

st.html(T.hero(
    L("Cover on you", "आप पर कवर"),
    L("If you cannot ride, the money still comes in.",
      "अगर आप न चला सकें, तब भी पैसा आता रहेगा।"),
    L("Rider Shield is the half of the policy that covers you rather than your "
      "bike. It pays a daily income benefit while an injury keeps you off the "
      "road, hospital cash while you are admitted, a fixed amount for a broken "
      "bone, an ambulance paid direct, a panel lawyer if there is an FIR, and a "
      "lump sum to your family in the worst case.",
      "Rider Shield पॉलिसी का वह हिस्सा है जो आपकी गाड़ी नहीं, आपकी सुरक्षा "
      "करता है। चोट के कारण गाड़ी बंद रहने पर रोज़ की आमदनी, भर्ती रहने पर "
      "अस्पताल कैश, हड्डी टूटने पर तय रकम, सीधे भुगतान वाली एम्बुलेंस, FIR होने "
      "पर पैनल वकील, और सबसे बुरी स्थिति में परिवार के लिए एकमुश्त रकम।"),
    badges=[
        L("Part of every plan from Plus upward", "Plus और उससे ऊपर हर प्लान में"),
        L("Amounts sized to what you earn", "रकम आपकी कमाई के हिसाब से"),
        L("Nothing to declare — we observe it", "कुछ घोषित नहीं करना — हम देख लेते हैं"),
    ],
    compact=True))

st.write("")
C.cta_row(key="rs_hero")
T.spacer(1.3)

# ------------------------------------------------------- benefits, sized live
T.heading(
    L("Your amounts", "आपकी रकम"),
    L("Benefits are calculated from your earnings, not chosen from a menu.",
      "रकम आपकी कमाई से तय होती है, किसी सूची में से नहीं चुनी जाती।"),
    L("Gig workers are asked to pick a sum insured they have no way of "
      "choosing well, and then the figure they declared is disputed at claim "
      "time. We take earnings from the Account Aggregator framework instead, so "
      "the amount is already agreed before anything goes wrong.",
      "गिग वर्कर से ऐसी बीमा राशि चुनने को कहा जाता है जिसे सही चुनने का कोई "
      "आधार उनके पास नहीं होता, और फिर क्लेम के वक़्त उसी आँकड़े पर विवाद होता "
      "है। हम इसकी जगह अकाउंट एग्रीगेटर से कमाई देखते हैं, ताकि रकम पहले ही तय "
      "हो — कुछ गलत होने से पहले।"),
    wide=True)
st.write("")

e1, e2 = st.columns([1, 2.1])
with e1:
    v["earnings"] = st.number_input(
        L("What you take home in a month (₹)", "महीने में हाथ में कितना आता है (₹)"),
        4000, 60000, int(v["earnings"]), 500, key="rs_earn")
    st.caption(L("Move this and every amount on the right recalculates.",
                 "इसे बदलिए — दाईं ओर की हर रकम अपने आप बदल जाएगी।"))

ben = Q.benefits(v)
dib = ben["daily_income_benefit"]
ad = ben["accidental_death"]
fx = ben["fixed"]

with e2:
    T.rows([
        (L("Every day you cannot ride", "हर वह दिन जब आप न चला सकें"),
         L(f"75% of your daily earnings · starts after {dib['waiting_days']} days · "
           f"up to {dib['max_days']} days a year",
           f"आपकी रोज़ की कमाई का 75% · {dib['waiting_days']} दिन बाद शुरू · "
           f"साल में {dib['max_days']} दिन तक"),
         inr(dib["value"]), L("a day", "रोज़")),
        (L("Most you can receive for one injury", "एक चोट पर अधिकतम"),
         L(f"{dib['max_days']} days at your rate", f"आपके रेट पर {dib['max_days']} दिन"),
         inr(dib["max_annual_payout"]), ""),
        (L("If you die or are permanently disabled",
           "मृत्यु या स्थायी विकलांगता पर"),
         L(f"8× your annual earnings, floor {inr(si['ad_floor'])}, "
           f"ceiling {inr(si['ad_ceiling'])}",
           f"सालाना कमाई का 8 गुना, कम से कम {inr(si['ad_floor'])}, "
           f"अधिकतम {inr(si['ad_ceiling'])}"),
         inr(ad["value"]), L("to your family", "परिवार को")),
        (L("Every day in hospital", "अस्पताल में हर दिन"),
         L(f"minimum 24-hour admission, up to {fx['hospital_cash_max_days']} days",
           f"कम से कम 24 घंटे भर्ती, {fx['hospital_cash_max_days']} दिन तक"),
         inr(fx["hospital_daily_cash"]), L("a day", "रोज़")),
        (L("Broken bone", "हड्डी टूटना"),
         L("fixed amount by bone, X-ray is the only paperwork",
           "हड्डी के हिसाब से तय रकम, सिर्फ़ एक्स-रे चाहिए"),
         f"{inr(fx['fracture_range'][0])}–{inr(fx['fracture_range'][1])}", ""),
        (L("Ambulance and first response", "एम्बुलेंस और तुरंत मदद"),
         L(f"paid direct to the operator, up to {inr(fx['ambulance_network_cap'])} — "
           f"{inr(fx['ambulance_out_of_network_fixed'])} flat if out of network",
           f"सीधे ऑपरेटर को भुगतान, {inr(fx['ambulance_network_cap'])} तक — "
           f"नेटवर्क के बाहर हो तो {inr(fx['ambulance_out_of_network_fixed'])} तय"),
         L("Covered", "कवर"), L("you pay nothing", "आपको कुछ नहीं देना")),
        (L("Legal help after an FIR", "FIR के बाद क़ानूनी मदद"),
         L("we send you a panel lawyer — we never ask you to pay one and claim back",
           "हम पैनल वकील भेजते हैं — पहले आप ख़र्च करें फिर क्लेम करें, ऐसा नहीं"),
         L("Included", "शामिल"), ""),
    ])

st.write("")
T.callout(L(
    f"At {inr(v['earnings'])} a month, six weeks off the road after a fracture "
    f"pays you about <b>{inr(dib['value'] * 39)}</b> — the "
    f"{inr(fx['fracture_range'][1])} fracture benefit sits on top of that. "
    "That is the difference between an accident being a setback and being the "
    "end of your household's income.",
    f"महीने की {inr(v['earnings'])} कमाई पर, हड्डी टूटने के बाद छह हफ़्ते गाड़ी "
    f"बंद रहने पर आपको लगभग <b>{inr(dib['value'] * 39)}</b> मिलते हैं — "
    f"{inr(fx['fracture_range'][1])} का फ्रैक्चर बेनिफ़िट इसके अलावा। यही फ़र्क़ "
    "है एक झटके और घर की कमाई ख़त्म हो जाने के बीच।"), brand=True)

T.spacer()

# ---------------------------------------------------------------- the honesty
T.heading(
    L("The fine print, up front", "शर्तें, शुरू में ही"),
    L("Four things we would rather you knew now than at claim time.",
      "चार बातें जो क्लेम के वक़्त नहीं, अभी जान लेना बेहतर है।"))
st.write("")

T.cards([
    {"icon": "⏳", "title": L(f"A {si['dib_waiting_days']}-day wait on income cover",
                             f"इनकम कवर पर {si['dib_waiting_days']} दिन का इंतज़ार"),
     "body": L("The daily income benefit starts from day four, not day one. A "
               "one-day sprain is not what this is for, and a shorter wait would "
               "make the hourly price meaningfully higher for everyone.",
               "रोज़ की आमदनी वाला लाभ चौथे दिन से शुरू होता है, पहले दिन से "
               "नहीं। एक दिन की मोच के लिए यह नहीं है, और कम इंतज़ार का मतलब "
               "होगा सबके लिए ज़्यादा महँगा घंटा।")},
    {"icon": "📉", "title": L("75% of earnings, not 100%",
                              "कमाई का 75%, 100% नहीं"),
     "body": L("It must never pay better to stay off the road than to ride. "
               "That factor is what keeps the price where it is and keeps "
               "claims payable quickly for everyone.",
               "ऐसा कभी नहीं होना चाहिए कि गाड़ी बंद रखना चलाने से ज़्यादा "
               "फ़ायदेमंद हो। यही अनुपात क़ीमत को क़ाबू में और सबके क्लेम को "
               "तेज़ रखता है।")},
    {"icon": "🩺", "title": L("Injury claims need a doctor, not just a photo",
                              "चोट के क्लेम पर सिर्फ़ फ़ोटो नहीं, डॉक्टर चाहिए"),
     "body": L("An X-ray or a panel-doctor certificate is required for the "
               "fracture and income benefits. That is what lets us pay the "
               "small claims instantly without the book falling over.",
               "फ्रैक्चर और इनकम बेनिफ़िट के लिए एक्स-रे या पैनल डॉक्टर का "
               "प्रमाणपत्र चाहिए। इसी वजह से हम छोटे क्लेम तुरंत चुका पाते हैं।")},
    {"icon": "🚦", "title": L("Cover has to be live at the time",
                              "उस समय कवर चालू होना चाहिए"),
     "body": L("You are covered for the hours you are riding on a declared "
               "shift. Turning cover off saves you money and does exactly what "
               "it says — it is off. The app makes it one tap either way.",
               "आप उन घंटों में कवर हैं जब दर्ज की गई शिफ़्ट पर चला रहे हों। "
               "कवर बंद करने से पैसा बचता है और वह सचमुच बंद रहता है। ऐप में "
               "दोनों तरफ़ एक ही टैप।")},
], cols=4)

T.spacer()

# ------------------------------------------------------------------ tiers
T.heading(L("Where it sits", "यह किन प्लान में है"),
          L("Rider Shield in each plan", "हर प्लान में Rider Shield"),
          L("Basic covers the catastrophes. Plus adds the thing riders actually "
            "claim on — income while you cannot work. Pro adds your bike.",
            "Basic बड़ी दुर्घटनाओं को कवर करता है। Plus वह जोड़ता है जिस पर "
            "राइडर असल में क्लेम करते हैं — काम बंद होने पर कमाई। Pro आपकी "
            "गाड़ी जोड़ता है।"))
st.write("")

qs = Q.all_tiers(v)
rows = []
for feat_en, feat_hi, tiers_with in Q.FEATURES:
    rows.append([L(feat_en, feat_hi)] +
                ["✓" if t in tiers_with else "—" for t in Q.TIERS])
rows.append([L("Your price per hour", "आपका प्रति घंटा रेट")] +
            [f"₹{qs[t]['premium_per_hour']:.2f}" for t in Q.TIERS])
T.comparison([L("What is covered", "क्या कवर है")] +
             [t.replace("GigSure ", "") for t in Q.TIERS], rows, us_col=2)

st.write("")
T.quotes([{"quote": pick(t, "quote"), "name": t["name"], "role": pick(t, "role")}
          for t in SITE["testimonials"][2:4]], cols=2)

T.spacer()
C.closing_cta(key="rs_close")
C.footer()
