"""
Product page — Ride Shield.

The commercial argument here is a single fact most riders do not know: a
privately registered two-wheeler used for delivery is being used commercially,
and every private motor policy in India excludes commercial use. The page leads
with that, because it converts better than any benefit list and it happens to
be true.
"""
from __future__ import annotations

import streamlit as st

from shared import inr
from engine.config import CFG
from web import theme as T, chrome as C, quote as Q, art as A
from web.i18n import L

C.utility_bar()

si = CFG["sum_insured"]
v = Q.visitor()
ben = Q.benefits(v)

st.html(T.split_hero(
    L("Cover on your bike and your work", "आपकी गाड़ी और काम पर कवर"),
    L("Your private bike policy will not pay when you crash <em>at work</em>.",
      "आपकी प्राइवेट बाइक पॉलिसी <em>काम के दौरान</em> हुए एक्सीडेंट पर पैसा नहीं देगी।"),
    L("A privately registered two-wheeler used for delivery is being used "
      "commercially — and every private motor policy in India excludes "
      "commercial use.",
      "डिलीवरी में इस्तेमाल हो रही प्राइवेट रजिस्टर्ड गाड़ी कमर्शियल इस्तेमाल "
      "में है — और भारत की हर प्राइवेट मोटर पॉलिसी उसे बाहर रखती है।"),
    [
        L("On-duty damage to your two-wheeler, paid to a network garage",
          "शिफ़्ट के दौरान गाड़ी का नुक़सान, पैसा नेटवर्क गैरेज को"),
        L("Platform deductions refunded at the amount on your statement",
          "प्लेटफ़ॉर्म की कटौती, स्टेटमेंट की रकम के हिसाब से वापस"),
        L("Consignment loss on an order you were carrying",
          "जो ऑर्डर आप ले जा रहे थे, उसके नुक़सान की भरपाई"),
    ],
    A.product_banner("ride")))

st.write("")
C.cta_row(key="rd_hero")
T.spacer(1.3)

# ---------------------------------------------------------------- the gap
T.heading(
    L("The gap", "वह खाई"),
    L("What your existing policies do and do not do",
      "आपकी मौजूदा पॉलिसियाँ क्या करती हैं और क्या नहीं"),
    wide=True)
st.write("")

T.comparison(
    [L("When it happens", "जब यह हो"),
     L("Your private motor policy", "आपकी प्राइवेट मोटर पॉलिसी"),
     L("Your platform's cover", "आपके प्लेटफ़ॉर्म का कवर"),
     "Ride Shield"],
    [
        [L("You crash while delivering an order",
           "ऑर्डर पहुँचाते समय एक्सीडेंट"),
         L("Excluded — commercial use", "बाहर — कमर्शियल इस्तेमाल"),
         L("Only while logged in to that app", "सिर्फ़ उसी ऐप पर लॉग-इन रहते हुए"),
         L("Covered on any app, any order", "हर ऐप, हर ऑर्डर पर कवर")],
        [L("You crash between two apps, with no order on",
           "दो ऐप के बीच, बिना ऑर्डर के एक्सीडेंट"),
         L("Excluded", "बाहर"),
         L("Not covered — you are logged out", "कवर नहीं — आप लॉग-आउट हैं"),
         L("Covered — your shift is what matters, not the app",
           "कवर — मायने आपकी शिफ़्ट रखती है, ऐप नहीं")],
        [L("The platform deducts for a spilled order",
           "गिरे हुए ऑर्डर का पैसा प्लेटफ़ॉर्म काट ले"),
         L("Not a motor claim at all", "यह मोटर क्लेम है ही नहीं"),
         L("Rarely covered", "बहुत कम कवर"),
         L("Reimbursed at the amount on your statement",
           "स्टेटमेंट में दिखी रकम की भरपाई")],
        [L("An order is lost or spoiled in transit",
           "ले जाते समय ऑर्डर खो जाए या ख़राब हो"),
         L("Not a motor claim at all", "यह मोटर क्लेम है ही नहीं"),
         L("No", "नहीं"),
         L("Consignment loss, reimbursed", "सामान का नुक़सान, भरपाई")],
    ], us_col=3)

st.write("")
T.callout(L(
    "Keep your private motor policy. You are legally required to hold third-"
    "party cover and Ride Shield does not replace it. What Ride Shield replaces "
    "is the own-damage cover that quietly does not apply to you.",
    "अपनी प्राइवेट मोटर पॉलिसी रखिए। थर्ड-पार्टी कवर क़ानूनन ज़रूरी है और "
    "Ride Shield उसकी जगह नहीं लेता। Ride Shield उस ओन-डैमेज कवर की जगह लेता "
    "है जो चुपचाप आप पर लागू ही नहीं होता।"))

T.spacer()

# ---------------------------------------------------------------- what it pays
T.heading(L("Your amounts", "आपकी रकम"),
          L("What Ride Shield pays", "Ride Shield क्या देता है"),
          L("Scheduled benefits and direct payments, deliberately. Cash to a "
            "rider for vehicle damage is where motor insurance gets expensive "
            "for everybody, so we pay the garage instead and keep your hourly "
            "price down.",
            "जानबूझकर तय रकम और सीधा भुगतान। गाड़ी के नुक़सान का नक़द राइडर को "
            "देना वही जगह है जहाँ मोटर बीमा सबके लिए महँगा हो जाता है, इसलिए हम "
            "पैसा गैरेज को देते हैं और आपका घंटा सस्ता रखते हैं।"),
          wide=True)
st.write("")

T.rows([
    (L("On-duty damage to your two-wheeler", "शिफ़्ट के दौरान गाड़ी का नुक़सान"),
     L(f"scheduled benefit, paid to a network garage · up to "
       f"{inr(ben['vehicle']['annual_aggregate'])} across a year",
       f"तय रकम, नेटवर्क गैरेज को भुगतान · साल भर में "
       f"{inr(ben['vehicle']['annual_aggregate'])} तक"),
     inr(ben["vehicle"]["per_event"]), L("per event", "प्रति घटना")),
    (L("Consignment loss", "सामान का नुक़सान"),
     L(f"spillage, damage, an order that never arrives · capped at "
       f"{inr(si['consignment_per_event_cap'])} an event",
       f"गिरना, टूटना, ऑर्डर न पहुँचना · प्रति घटना "
       f"{inr(si['consignment_per_event_cap'])} तक"),
     inr(ben["consignment"]["per_event"]), L("per event", "प्रति घटना")),
    (L("Platform deductions", "प्लेटफ़ॉर्म की कटौती"),
     L("the exact amount the platform took off your payout statement",
       "प्लेटफ़ॉर्म ने आपके पेआउट से जो रकम काटी, ठीक उतनी"),
     L("Refunded", "वापस"), L("in full", "पूरी")),
    (L("Goods in transit", "ले जाते समय सामान"),
     L("capped at the 95th percentile of your trailing order value",
       "आपके पिछले ऑर्डर मूल्य के 95वें प्रतिशत तक"),
     L("Covered", "कवर"), ""),
    (L("Phone screen and EV battery", "फ़ोन स्क्रीन और EV बैटरी"),
     L("optional add-ons, repaired at our network — never paid as cash",
       "वैकल्पिक ऐड-ऑन, हमारे नेटवर्क पर मरम्मत — नक़द कभी नहीं"),
     L("Add-on", "ऐड-ऑन"), L("+₹0.25–0.35/hr", "+₹0.25–0.35/घंटा")),
], )

T.spacer()

# ---------------------------------------------------------------- how it works
T.heading(L("How a bike claim runs", "गाड़ी का क्लेम कैसे चलता है"),
          L("Photographed on day one, so nobody argues on day two hundred.",
            "पहले दिन फ़ोटो, ताकि दो सौवें दिन बहस न हो।"))
st.write("")
T.steps([
    {"title": L("Baseline photos at sign-up", "साइन-अप पर शुरुआती फ़ोटो"),
     "body": L("Four photos of your bike when the policy starts. This is the "
               "single thing that makes fast settlement possible later.",
               "पॉलिसी शुरू होते समय गाड़ी की चार फ़ोटो। बाद में तेज़ निपटारे "
               "की असली वजह यही एक चीज़ है।"),
     "time": L("60 seconds, once", "60 सेकंड, एक बार")},
    {"title": L("The impact is already recorded", "टक्कर पहले से दर्ज है"),
     "body": L("Your phone's accelerometer logs the impact signature and the "
               "time. You do not have to prove that something happened.",
               "आपके फ़ोन का सेंसर टक्कर और समय दर्ज कर लेता है। कुछ हुआ था, यह "
               "साबित करना आपका काम नहीं।"),
     "time": L("Automatic", "अपने आप")},
    {"title": L("Ride to a network garage", "नेटवर्क गैरेज तक ले जाएँ"),
     "body": L("We show you the nearest one in the app and send the approval "
               "to them. You do not pay and claim back.",
               "ऐप में सबसे नज़दीक वाला दिखता है और मंज़ूरी सीधे उन्हें जाती "
               "है। पहले आप भरें फिर क्लेम करें, ऐसा नहीं।"),
     "time": L("Same day", "उसी दिन")},
    {"title": L("We settle with the garage", "हम गैरेज से हिसाब करते हैं"),
     "body": L("The scheduled amount goes to the garage. Anything above it is "
               "yours to decide on before the work starts, never after.",
               "तय रकम गैरेज को जाती है। उससे ऊपर का ख़र्च काम शुरू होने से "
               "पहले आपको तय करना है, बाद में कभी नहीं।"),
     "time": L("No cash out of your pocket", "आपकी जेब से कुछ नहीं")},
])

T.spacer()

qs = Q.all_tiers(v)
pro = qs["GigSure Pro"]
plus = qs["GigSure Plus"]
T.callout(L(
    f"Ride Shield comes with GigSure Pro. At {v['hours_pm']} hours a month that "
    f"is <b>₹{pro['premium_per_hour']:.2f} an hour</b> against "
    f"₹{plus['premium_per_hour']:.2f} on Plus — about "
    f"<b>{inr(pro['premium_month'] - plus['premium_month'])} more a month</b> "
    "for your bike, your orders and your phone.",
    f"Ride Shield, GigSure Pro के साथ आता है। महीने में {v['hours_pm']} घंटे पर "
    f"यह <b>₹{pro['premium_per_hour']:.2f} प्रति घंटा</b> है, जबकि Plus पर "
    f"₹{plus['premium_per_hour']:.2f} — यानी गाड़ी, ऑर्डर और फ़ोन के लिए लगभग "
    f"<b>{inr(pro['premium_month'] - plus['premium_month'])} महीना ज़्यादा</b>।"),
    brand=True)

T.spacer()
C.closing_cta(key="rd_close")
C.footer()
