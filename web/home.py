"""
GigSure.com — the landing page.

Built to be understood by someone who is standing at a hub gate with one hand
on a handlebar, not read like a document. The rule applied throughout: if a
point can be made with a picture, a number or an icon, it does not get a
paragraph.

The page answers five questions in order — what this is, does it work on my
apps, what do I get, what does it cost, what happens when I claim — and every
figure in it comes from the same rating engine and configuration files that
drive the insurer console.
"""
from __future__ import annotations

import streamlit as st

from shared import inr
from engine.config import CFG
from web import theme as T, chrome as C, quote as Q, art as A
from web.i18n import L
from web.content import SITE, pick

C.utility_bar()

cr = SITE["claims_report"]
sp = SITE["settlement_promise"]
band = Q.price("GigSure Plus")["band"]
ben = Q.benefits()

# ------------------------------------------------------------------------ hero
st.html(T.split_hero(
    L("One policy · every app · pay by the hour",
      "एक पॉलिसी · हर ऐप · घंटे के हिसाब से"),
    L("Insurance that belongs to <em>you</em>, not to the app you ride for.",
      "बीमा जो <em>आपका</em> है, उस ऐप का नहीं जिसके लिए आप चलाते हैं।"),
    L("Built for delivery riders, quick-commerce partners and bike-taxi "
      "drivers. Cover follows you, not the app you happen to be logged in to.",
      "डिलीवरी राइडर, क्विक-कॉमर्स पार्टनर और बाइक-टैक्सी ड्राइवर के लिए। कवर "
      "आपके साथ चलता है, उस ऐप के साथ नहीं जिस पर आप लॉग-इन हैं।"),
    [
        L(f"Pay only for hours ridden — from ₹{band['floor_per_hour']:.2f} an hour",
          f"सिर्फ़ चलाए घंटों का पैसा — ₹{band['floor_per_hour']:.2f} प्रति घंटे से"),
        L("Cannot ride after an injury? We pay your income, every day",
          "चोट के बाद न चला सकें? हर दिन की कमाई हम देंगे"),
        L(f"{cr['settlement_ratio']:.0%} of claims paid · median "
          f"{cr['median_turnaround_hours']:.1f} hours to your UPI",
          f"{cr['settlement_ratio']:.0%} क्लेम का भुगतान · औसतन "
          f"{cr['median_turnaround_hours']:.1f} घंटे में UPI में"),
    ],
    A.hero_visual()))

st.write("")
C.cta_row(key="hero")

T.spacer(1.5)

# ------------------------------------------------------- works on every app
w1, w2 = st.columns([1, 1.05], vertical_alignment="center")
with w1:
    T.heading(
        L("Portable by design", "जन्म से ही पोर्टेबल"),
        L("One policy. Every app you earn from.",
          "एक पॉलिसी। हर वह ऐप जिससे आप कमाते हैं।"),
        L("Platform cover switches off the second you log out — and about 40% "
          "of a rider's day is spent between apps. Your GigSure policy does not "
          "know or care which app the order came from. It is live whenever your "
          "shift is on.",
          "प्लेटफ़ॉर्म का कवर लॉग-आउट करते ही बंद हो जाता है — और राइडर का "
          "लगभग 40% दिन ऐप बदलने में जाता है। आपकी GigSure पॉलिसी को यह जानने "
          "की ज़रूरत ही नहीं कि ऑर्डर किस ऐप का था। शिफ़्ट चालू, कवर चालू।"))
    st.write("")
    st.html(A.platform_chips())
    st.write("")
    st.caption(L("Recognised platform names are shown to indicate where riders "
                 "work. GigSure has no commercial tie to any of them — that is "
                 "the point.",
                 "ये नाम सिर्फ़ यह बताने के लिए हैं कि राइडर कहाँ काम करते हैं। "
                 "इनमें से किसी से GigSure का कोई कारोबारी रिश्ता नहीं — यही तो "
                 "बात है।"))
with w2:
    st.html(A.platform_web())

T.spacer(1.2)

# ------------------------------------------------------------ what is covered
T.heading(
    L("What is covered", "क्या-क्या कवर है"),
    L("Everything that goes wrong on a shift.",
      "शिफ़्ट में जो कुछ भी बिगड़ सकता है।"),
    L("Amounts below are calculated for a rider taking home "
      f"{inr(Q.visitor()['earnings'])} a month. They move with your earnings.",
      "नीचे की रकम महीने में "
      f"{inr(Q.visitor()['earnings'])} कमाने वाले राइडर के लिए है। आपकी कमाई के "
      "हिसाब से यह बदलती है।"),
    wide=True)
st.write("")

T.tiles([
    {"icon": "wallet", "hot": True,
     "title": L("Income while you cannot ride", "न चला पाने पर कमाई"),
     "value": inr(ben["daily_income_benefit"]["value"]),
     "sub": L("a day, up to 90 days", "रोज़, 90 दिन तक")},
    {"icon": "heart", "title": L("Your family, worst case", "परिवार, सबसे बुरी स्थिति में"),
     "value": inr(ben["accidental_death"]["value"]),
     "sub": L("8× your yearly earnings", "सालाना कमाई का 8 गुना")},
    {"icon": "hospital", "title": L("Hospital cash", "अस्पताल कैश"),
     "value": inr(ben["fixed"]["hospital_daily_cash"]),
     "sub": L("a day, up to 30 days", "रोज़, 30 दिन तक")},
    {"icon": "bone", "title": L("Broken bone", "हड्डी टूटना"),
     "value": f"{inr(ben['fixed']['fracture_range'][0])}+",
     "sub": L("fixed, by bone", "हड्डी के हिसाब से तय")},
    {"icon": "ambulance", "title": L("Ambulance", "एम्बुलेंस"),
     "value": L("Paid direct", "सीधा भुगतान"),
     "sub": L("never out of your pocket", "आपकी जेब से कभी नहीं")},
    {"icon": "scooter", "hot": True,
     "title": L("Your bike, on shift", "शिफ़्ट में आपकी गाड़ी"),
     "value": inr(ben["vehicle"]["per_event"]),
     "sub": L("per event, paid to the garage", "प्रति घटना, गैरेज को")},
    {"icon": "box", "title": L("Orders deducted from pay", "पे से कटे ऑर्डर"),
     "value": L("Refunded", "वापस"),
     "sub": L("spillage, damage, loss", "गिरना, टूटना, खोना")},
    {"icon": "phone", "title": L("Phone screen", "फ़ोन स्क्रीन"),
     "value": L("Repaired", "मरम्मत"),
     "sub": L("at our network", "हमारे नेटवर्क पर")},
    {"icon": "battery", "title": L("EV battery", "EV बैटरी"),
     "value": L("Covered", "कवर"),
     "sub": L("paid to the OEM", "सीधे OEM को")},
    {"icon": "scales", "title": L("Legal help after an FIR", "FIR के बाद क़ानूनी मदद"),
     "value": L("Included", "शामिल"),
     "sub": L("we send the lawyer", "वकील हम भेजते हैं")},
], cols=5)

T.spacer(1.2)

# ------------------------------------------------------------- two products
T.heading(
    L("Two covers, one policy", "दो कवर, एक पॉलिसी"),
    L("One protects you. One protects what you work with.",
      "एक आपकी रक्षा करता है। दूसरा आपके काम के सामान की।"),
    wide=True)
st.write("")

p1, p2 = st.columns(2, gap="medium")

with p1:
    st.html(T.product(
        "a", L("Cover on you", "आप पर कवर"),
        L("Rider Shield", "Rider Shield"),
        L("The part nobody else covers — the weeks you cannot earn. Amounts "
          "are set from what you actually take home, not a figure you declared.",
          "वह हिस्सा जो और कोई कवर नहीं करता — वे हफ़्ते जब कमाई बंद हो जाती "
          "है। रकम आपकी असली कमाई से तय होती है, किसी घोषित आँकड़े से नहीं।"),
        [
            ("wallet", L("Every day you cannot ride", "हर वह दिन जब न चला सकें"),
             L("after a 3-day wait, up to 90 days", "3 दिन बाद, 90 दिन तक"),
             inr(ben["daily_income_benefit"]["value"])),
            ("heart", L("If the worst happens", "सबसे बुरा होने पर"),
             L("paid to your family", "परिवार को"),
             inr(ben["accidental_death"]["value"])),
            ("hospital", L("Hospital, bones, ambulance", "अस्पताल, हड्डी, एम्बुलेंस"),
             L("fixed amounts, no bill-chasing", "तय रकम, बिल का झंझट नहीं"),
             inr(ben["fixed"]["hospital_daily_cash"])),
        ],
        A.product_banner("rider")))
    st.write("")
    if st.button(L("See Rider Shield in full →", "Rider Shield पूरा देखें →"),
                 key="p1", width="stretch"):
        st.switch_page(C.RIDER)

with p2:
    st.html(T.product(
        "b", L("Cover on your bike", "आपकी गाड़ी पर कवर"),
        L("Ride Shield", "Ride Shield"),
        L("Your private two-wheeler policy excludes commercial use — every one "
          "of them does. This is the cover that pays when you crash on a "
          "delivery.",
          "आपकी प्राइवेट दोपहिया पॉलिसी कमर्शियल इस्तेमाल को बाहर रखती है — हर "
          "एक रखती है। डिलीवरी के दौरान एक्सीडेंट पर पैसा यही कवर देता है।"),
        [
            ("scooter", L("Your bike, damaged on shift", "शिफ़्ट में गाड़ी का नुक़सान"),
             L("paid straight to a network garage", "सीधे नेटवर्क गैरेज को"),
             inr(ben["vehicle"]["per_event"])),
            ("box", L("An order deducted from your pay", "पे से कटा ऑर्डर"),
             L("spillage, damage, undelivered", "गिरना, टूटना, न पहुँचना"),
             L("Refunded", "वापस")),
            ("phone", L("Phone screen and EV battery", "फ़ोन स्क्रीन और EV बैटरी"),
             L("repaired at our network, never cash", "नेटवर्क पर मरम्मत, नक़द नहीं"),
             L("Covered", "कवर")),
        ],
        A.product_banner("ride")))
    st.write("")
    if st.button(L("See Ride Shield in full →", "Ride Shield पूरा देखें →"),
                 key="p2", width="stretch"):
        st.switch_page(C.RIDE)

T.spacer(1.3)

# ----------------------------------------------------------- usage analytics
T.heading(
    L("Usage-based pricing", "उपयोग-आधारित क़ीमत"),
    L("The app knows what an hour is worth. So do you.",
      "ऐप को पता है एक घंटे की क़ीमत क्या है। आपको भी।"),
    L("Every fifteen minutes you ride is scored for the time of day, the "
      "weather and the traffic where you are, and combined with how you ride. "
      "You see the whole calculation in the app — the same one the insurer's "
      "rating engine runs.",
      "आपके चलाए हर पंद्रह मिनट को समय, मौसम और वहाँ के ट्रैफ़िक के हिसाब से "
      "आँका जाता है, और उसमें आपके चलाने का तरीक़ा जुड़ता है। पूरा हिसाब ऐप में "
      "दिखता है — वही जो कंपनी का रेटिंग इंजन चलाता है।"),
    wide=True)
st.write("")

a1, a2 = st.columns([1, 1.35], vertical_alignment="center")
with a1:
    st.html(f"<div style='max-width:290px'>{A.phone_score()}</div>")
with a2:
    T.cards([
        {"icon": "clock", "title": L("Charged by the hour, not the year",
                                     "साल का नहीं, घंटे का हिसाब"),
         "amount": L("₹0", "₹0"),
         "amount_note": L("on a day off", "छुट्टी वाले दिन"),
         "body": L("Cover switches on with your shift and off when you stop. "
                   "Debited each evening by UPI Autopay, never as a lump sum.",
                   "शिफ़्ट के साथ कवर चालू, रुकते ही बंद। हर शाम UPI ऑटोपे से "
                   "कटौती, कभी एकमुश्त नहीं।")},
        {"icon": "gauge", "title": L("Ride well, pay less", "अच्छा चलाइए, कम दीजिए"),
         "amount": L("−20%", "−20%"),
         "amount_note": L("at a score above 90", "90 से ऊपर स्कोर पर"),
         "body": L("Harsh braking, cornering, speeding and screen-on-while-"
                   "moving. The one factor you can change this week.",
                   "तेज़ ब्रेक, मोड़, रफ़्तार और चलते समय स्क्रीन। यही एक चीज़ "
                   "है जिसे आप इसी हफ़्ते बदल सकते हैं।")},
        {"icon": "shield", "title": L("A cap you can rely on", "एक भरोसेमंद सीमा"),
         "amount": f"₹{band['ceiling_per_hour']:.2f}",
         "amount_note": L("the most, ever", "अधिकतम, कभी भी"),
         "body": L("However bad the night gets, the price stops here. Beyond "
                   "the band we do not charge more — a filed control, not a "
                   "favour.",
                   "रात कितनी भी ख़राब हो, रेट यहीं रुक जाता है। बैंड के बाहर "
                   "हम ज़्यादा नहीं लेते — यह दर्ज नियम है, एहसान नहीं।")},
        {"icon": "lock", "title": L("Your data stays yours", "आपका डेटा आपका ही"),
         "amount": L("Never sold", "कभी नहीं बिकेगा"),
         "amount_note": L("to any platform", "किसी प्लेटफ़ॉर्म को"),
         "body": L("Withdraw consent any time and your cover does not lapse — "
                   "you move to a flat rate. We record only while cover is on.",
                   "कभी भी सहमति वापस लें, कवर बंद नहीं होगा — आप फ़्लैट रेट पर "
                   "आ जाएँगे। रिकॉर्डिंग सिर्फ़ कवर चालू रहते हुए।")},
    ], cols=2)

st.write("")
st.html(f"<div class='gs gs-media mint'>{A.day_strip()}</div>")

st.write("")
v = Q.visitor()
cc = st.columns([1.4, 1.2, 2.4], vertical_alignment="bottom")
v["hours_pm"] = cc[0].slider(
    L("Hours you ride a month", "महीने में कितने घंटे"),
    20, 280, int(v["hours_pm"]), 10, key="home_hours")
v["city"] = cc[1].selectbox(L("Where you ride", "कहाँ चलाते हैं"),
                            list(CFG["city"].keys()),
                            index=list(CFG["city"]).index(v["city"]),
                            key="home_city")

qs = Q.all_tiers(v)
plus = qs["GigSure Plus"]
flat = Q.flat_annual("GigSure Plus")
saving = flat - plus["premium_year"]

with cc[2]:
    st.html(f"""
    <div class='gs' style='display:flex;gap:.8rem;align-items:stretch'>
      <div class='gs-card' style='flex:1;padding:1rem 1.15rem'>
        <div style='font-size:.75rem;font-weight:800;letter-spacing:.1em;
                    text-transform:uppercase;color:#6E807D'>
          {L('Your rate', 'आपका रेट')}</div>
        <div class='amt' style='font-size:1.9rem'>₹{plus['premium_per_hour']:.2f}
          <small>{L('an hour', 'प्रति घंटा')}</small></div>
        <p style='font-size:.85rem'>{inr(plus['premium_month'])}
          {L('a month on GigSure Plus', 'महीना, GigSure Plus पर')}</p>
      </div>
      <div class='gs-card {'cream' if saving > 0 else 'sand'}'
           style='flex:1;padding:1rem 1.15rem'>
        <div style='font-size:.75rem;font-weight:800;letter-spacing:.1em;
                    text-transform:uppercase;color:#6E807D'>
          {L('Against a flat yearly policy', 'फ़्लैट सालाना पॉलिसी के मुक़ाबले')}</div>
        <div class='amt' style='font-size:1.9rem;color:{T.ACCENT_DEEP if saving > 0 else T.MUTED}'>
          {inr(abs(saving))}</div>
        <p style='font-size:.85rem'>{
          L('less a year, because you are not paying for a full-timer&rsquo;s risk',
            'सालाना कम, क्योंकि आप पूरे समय चलाने वाले का जोखिम नहीं भर रहे')
          if saving > 0 else
          L('more a year — you ride more than a full-timer, and are covered for it',
            'सालाना ज़्यादा — आप पूरे समय वाले से भी ज़्यादा चलाते हैं, और उसी का कवर है')}</p>
      </div>
    </div>""")

st.write("")
if st.button(L("See every rating factor we use →",
               "हम जो भी फ़ैक्टर इस्तेमाल करते हैं, देखें →"), key="topricing"):
    st.switch_page(C.PRICING)

T.spacer(1.3)

# ---------------------------------------------------------------------- claims
T.heading(
    L("Claims", "क्लेम"),
    L("Paid the same day. Straight to your UPI.",
      "उसी दिन भुगतान। सीधे आपके UPI में।"),
    L("A claim settled in four months is not a claim settled — not for someone "
      "who earns daily.",
      "चार महीने में निपटा क्लेम, निपटा हुआ नहीं है — कम से कम उसके लिए तो नहीं "
      "जो रोज़ कमाता है।"),
    wide=True)
st.write("")

T.steps([
    {"title": L("Tap once in the app", "ऐप में एक टैप"),
     "body": L("Pick what happened from a list, or say it out loud in your "
               "language. No forms, no branch, no agent.",
               "सूची में से चुनें कि क्या हुआ, या अपनी भाषा में बोल दें। न "
               "फ़ॉर्म, न ब्रांच, न एजेंट।"),
     "time": L("30 seconds", "30 सेकंड")},
    {"title": L("We already have the proof", "सबूत हमारे पास है"),
     "body": L("Your ride data shows where you were and whether there was an "
               "impact. You do not prove what we can already see.",
               "आपका राइड डेटा बताता है कि आप कहाँ थे और टक्कर हुई या नहीं। जो "
               "हम देख सकते हैं, वह आपको साबित नहीं करना।"),
     "time": L("Automatic", "अपने आप")},
    {"title": L("A decision, with the reason", "फ़ैसला, कारण के साथ"),
     "body": L("Ambulance, phone and order claims are decided by machine in "
               "minutes. Injury claims see a panel doctor.",
               "एम्बुलेंस, फ़ोन और ऑर्डर के क्लेम मशीन मिनटों में तय करती है। "
               "चोट के क्लेम पैनल डॉक्टर देखता है।"),
     "time": L(f"{sp['instant_heads_minutes']} min – {sp['standard_head_hours']} hrs",
               f"{sp['instant_heads_minutes']} मिनट – {sp['standard_head_hours']} घंटे")},
    {"title": L("Money in your UPI", "पैसा आपके UPI में"),
     "body": L("On a death claim we release ₹1,00,000 to the family within 48 "
               "hours, before any investigation finishes.",
               "मृत्यु के क्लेम पर परिवार को 48 घंटे में ₹1,00,000 — जाँच पूरी "
               "होने से पहले।"),
     "time": L("Same day", "उसी दिन")},
])

st.write("")
T.stats([
    (f"{cr['settlement_ratio']:.1%}", L("of claims paid", "क्लेम का भुगतान"),
     L(f"{cr['claims_paid']:,} of {cr['claims_received']:,} in {cr['period']}",
       f"{pick(cr, 'period')} में {cr['claims_received']:,} में से "
       f"{cr['claims_paid']:,}")),
    (f"{cr['median_turnaround_hours']:.1f} {L('hrs', 'घंटे')}",
     L("median settlement time", "निपटारे का औसत समय"),
     L(f"{cr['share_settled_same_day']:.0%} settled the same day",
       f"{cr['share_settled_same_day']:.0%} उसी दिन निपटे")),
    (f"{cr['share_settled_instantly']:.0%}",
     L("settled with no human involved", "बिना किसी इंसान के निपटे"),
     L("ambulance, phone and order claims", "एम्बुलेंस, फ़ोन और ऑर्डर के क्लेम")),
    ("₹0", L("to make a claim", "क्लेम करने का ख़र्च"),
     L("free appeal, free ombudsman route", "अपील मुफ़्त, लोकपाल तक भी मुफ़्त")),
])

st.write("")
if st.button(L("Read our published claims record →",
               "हमारा प्रकाशित क्लेम रिकॉर्ड पढ़ें →"), key="toclaims"):
    st.switch_page(C.CLAIMS)

T.spacer(1.3)

# ---------------------------------------------------------------- testimonials
T.heading(L("Riders", "राइडर"),
          L("What changed for them", "उनके लिए क्या बदला"),
          L("Composite riders drawn from the segments we serve.",
            "जिन वर्गों के लिए हम काम करते हैं, उनसे बने प्रतिनिधि उदाहरण।"))
st.write("")
T.quotes([{"quote": pick(t, "quote"), "name": t["name"], "role": pick(t, "role")}
          for t in SITE["testimonials"][:3]], cols=3)

T.spacer(1.2)

# ------------------------------------------------------------------- referral
r = SITE["referral"]
rc1, rc2 = st.columns([1.5, 1], vertical_alignment="center")
with rc1:
    T.heading(L("Referral", "रेफ़रल"),
              L(f"₹{r['reward_each_side']} to you. ₹{r['reward_each_side']} to them.",
                f"₹{r['reward_each_side']} आपको। ₹{r['reward_each_side']} उन्हें।"),
              L("Riders trust riders. Share your code in your hub's WhatsApp "
                f"group; once they have ridden {r['qualify_after_hours']} covered "
                "hours, both of you are paid to UPI.",
                "राइडर, राइडर पर भरोसा करते हैं। अपने हब के WhatsApp ग्रुप में "
                f"कोड भेजिए; जब वे {r['qualify_after_hours']} कवर वाले घंटे चला "
                "लें, दोनों को UPI में पैसा।"))
    st.write("")
    if st.button(L("How referral works →", "रेफ़रल कैसे काम करता है →"), key="toref"):
        st.switch_page(C.REFERRAL)
with rc2:
    T.tiles([
        {"icon": "people", "title": L("Refer a rider", "राइडर जोड़ें"),
         "value": f"₹{r['reward_each_side']}", "sub": L("to each of you", "दोनों को")},
        {"icon": "rupee", "hot": True, "title": L("Every month, up to", "हर महीने, तक"),
         "value": f"₹{r['monthly_cap_per_rider']:,}", "sub": L("no referral limit", "रेफ़रल की सीमा नहीं")},
    ], cols=2)

T.spacer(1.2)

C.closing_cta(key="home_close")
C.footer()
