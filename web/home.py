"""
GigSure.com — the landing page.

The job of this page is to answer five questions before a rider scrolls twice:
what we sell, why it is different from the cover their app gives them, what it
costs, what happens when they claim, and how to start. Everything analytical
lives one click away in the Rider app and the Insurer console. Nothing on this
page is about our model; everything is about what the worker gets.
"""
from __future__ import annotations

import streamlit as st

from shared import inr
from engine.config import CFG
from web import theme as T, chrome as C, quote as Q
from web.i18n import L
from web.content import SITE, pick

C.utility_bar()

cr = SITE["claims_report"]
sp = SITE["settlement_promise"]
band = Q.price(  # the reference GigSure Plus rider, priced by the live engine
    "GigSure Plus")["band"]

# ------------------------------------------------------------------------ hero
st.html(T.hero(
    L("One policy · every app · pay by the hour",
      "एक पॉलिसी · हर ऐप · घंटे के हिसाब से"),
    L("Insurance that belongs to <em>you</em>, not to the app you ride for.",
      "ऐसा बीमा जो <em>आपका</em> है, उस ऐप का नहीं जिसके लिए आप चलाते हैं।"),
    L("Cover that stays live across Swiggy, Zomato, Zepto, Blinkit, Rapido — "
      "every app you earn from. You pay only for the hours you actually ride. "
      "If you are hurt and cannot work, we replace your income. Straightforward "
      "claims are settled the same day, straight to your UPI.",
      "स्विगी, ज़ोमैटो, ज़ेप्टो, ब्लिंकिट, रैपिडो — जिस भी ऐप से आप कमाते हैं, "
      "हर जगह कवर चालू। पैसा सिर्फ़ उन घंटों का जो आपने सच में चलाया। चोट लगने "
      "पर जब काम न हो सके, आपकी कमाई की भरपाई हम करते हैं। सीधे क्लेम उसी दिन, "
      "सीधे आपके UPI में।"),
    badges=[
        L(f"From ₹{band['floor_per_hour']:.2f} an hour",
          f"₹{band['floor_per_hour']:.2f} प्रति घंटे से"),
        L("₹0 on a day you do not ride", "जिस दिन न चलाएँ — ₹0"),
        L("No lock-in, no joining fee", "न लॉक-इन, न जॉइनिंग फ़ीस"),
        L("Works across every platform", "हर प्लेटफ़ॉर्म पर चलता है"),
    ],
    note=L("Aadhaar, your vehicle number, a UPI mandate. That is the whole "
           "sign-up — about ninety seconds.",
           "आधार, गाड़ी नंबर, UPI मैंडेट। बस इतना ही — लगभग नब्बे सेकंड।")))

st.write("")
C.cta_row(key="hero")
T.spacer(1.4)

# ----------------------------------------------------------------- proof strip
T.stats([
    (f"₹{band['floor_per_hour']:.2f}",
     L("an hour, where cover starts", "प्रति घंटा, कवर यहाँ से शुरू"),
     L("GigSure Plus, in the best conditions",
       "GigSure Plus, सबसे अच्छी परिस्थिति में")),
    (f"{cr['settlement_ratio']:.1%}",
     L("of claims paid", "क्लेम का भुगतान"),
     L(f"{cr['claims_paid']:,} of {cr['claims_received']:,} in {cr['period']}",
       f"{pick(cr, 'period')} में {cr['claims_received']:,} में से "
       f"{cr['claims_paid']:,}")),
    (f"{cr['median_turnaround_hours']:.1f} {L('hrs', 'घंटे')}",
     L("median time to settle", "निपटारे का औसत समय"),
     L(f"{cr['share_settled_same_day']:.0%} settled the same day",
       f"{cr['share_settled_same_day']:.0%} उसी दिन निपटे")),
    (L("Every app", "हर ऐप"),
     L("your cover stays live", "आपका कवर चालू रहता है"),
     L("including the gap between two apps",
       "दो ऐप के बीच के समय में भी")),
])

T.spacer()

# ------------------------------------------------------------------- the point
T.heading(
    L("Why this exists", "यह क्यों बना"),
    L("You are not uninsured. You are insured badly.",
      "आप बिना बीमे के नहीं हैं। आपका बीमा ख़राब है।"),
    L("The cover you already have belongs to a platform, switches off when you "
      "log out, will not pay for your bike because it is privately registered, "
      "and takes months to settle. Four failures, and we were built to fix all "
      "four.",
      "जो कवर आपके पास है वह किसी प्लेटफ़ॉर्म का है, लॉग-आउट करते ही बंद हो "
      "जाता है, आपकी प्राइवेट रजिस्टर्ड गाड़ी का पैसा नहीं देता, और निपटने में "
      "महीनों लेता है। चार ख़ामियाँ — और हम चारों को ठीक करने के लिए बने हैं।"),
    wide=True)
st.write("")

T.cards([
    {"icon": "📱", "title": pick(f, "title"), "body": pick(f, "body")}
    for f in SITE["failures"]
], cols=4)

st.write("")
if st.button(L("See the full comparison with platform cover →",
               "प्लेटफ़ॉर्म कवर से पूरी तुलना देखें →"), key="tofix"):
    st.switch_page(C.WHY)

T.spacer()

# ------------------------------------------------------------------- what we sell
T.heading(
    L("What you get", "आपको क्या मिलता है"),
    L("Two covers. One policy. One app.",
      "दो कवर। एक पॉलिसी। एक ऐप।"),
    L("Rider Shield protects you and the money you bring home. Ride Shield "
      "protects the bike, the order and the phone you work with. Take one or "
      "take both — it is a single policy and a single hourly price either way.",
      "Rider Shield आपकी और आपकी कमाई की सुरक्षा करता है। Ride Shield उस गाड़ी, "
      "ऑर्डर और फ़ोन की जिनसे आप काम करते हैं। एक लें या दोनों — पॉलिसी एक ही "
      "रहेगी और घंटे का रेट भी एक ही।"),
    wide=True)
st.write("")

ben = Q.benefits()
p1, p2 = st.columns(2)

with p1:
    st.html(f"""
    <div class='gs gs-card' style='border-width:2px;border-color:#0F5C57'>
      <div class='ic'>🛡️</div>
      <h3>Rider Shield — {L('cover for you', 'आपके लिए कवर')}</h3>
      <p style='margin-bottom:.9rem'>{L(
        'The part nobody else covers: the weeks you cannot earn. Benefits are '
        'sized to what you actually earn, not to a number you declared.',
        'वह हिस्सा जो और कोई कवर नहीं करता: वे हफ़्ते जब कमाई बंद हो जाती है। '
        'रकम आपकी असली कमाई के हिसाब से तय होती है, किसी घोषित आँकड़े से नहीं।')}</p>
      <div class='gs-row' style='padding-left:0;padding-right:0'>
        <div class='l'>{L('Every day you cannot ride', 'हर वह दिन जब आप न चला सकें')}
          <small>{L('after a 3-day wait, up to 90 days a year', '3 दिन के बाद, साल में 90 दिन तक')}</small></div>
        <div class='r'>{inr(ben['daily_income_benefit']['value'])}</div>
      </div>
      <div class='gs-row' style='padding-left:0;padding-right:0'>
        <div class='l'>{L('If the worst happens, for your family', 'सबसे बुरा हो, तो आपके परिवार के लिए')}
          <small>{L('8× your observed annual earnings', 'आपकी सालाना कमाई का 8 गुना')}</small></div>
        <div class='r'>{inr(ben['accidental_death']['value'])}</div>
      </div>
      <div class='gs-row' style='padding-left:0;padding-right:0;border-bottom:none'>
        <div class='l'>{L('Hospital cash, broken bones, ambulance, legal help', 'अस्पताल कैश, हड्डी टूटना, एम्बुलेंस, क़ानूनी मदद')}
          <small>{L('ambulance paid direct — you never pay and claim back', 'एम्बुलेंस का पैसा सीधे — आपको पहले जेब से नहीं देना')}</small></div>
        <div class='r'>{inr(ben['fixed']['hospital_daily_cash'])}<small>{L('a day', 'रोज़')}</small></div>
      </div>
    </div>""")
    st.write("")
    if st.button(L("What Rider Shield pays →", "Rider Shield क्या देता है →"),
                 key="p1", width="stretch"):
        st.switch_page(C.RIDER)

with p2:
    st.html(f"""
    <div class='gs gs-card' style='border-width:2px;border-color:#FF6A35'>
      <div class='ic' style='background:#FFEDE4'>🛵</div>
      <h3>Ride Shield — {L('cover for your bike and your work', 'आपकी गाड़ी और काम के लिए कवर')}</h3>
      <p style='margin-bottom:.9rem'>{L(
        'Your private two-wheeler policy excludes commercial use. Every one of '
        'them does. This is the cover that actually pays when you crash on a '
        'delivery.',
        'आपकी प्राइवेट दोपहिया पॉलिसी कमर्शियल इस्तेमाल को बाहर रखती है। हर एक '
        'रखती है। डिलीवरी के दौरान एक्सीडेंट पर असल में यही कवर पैसा देता है।')}</p>
      <div class='gs-row' style='padding-left:0;padding-right:0'>
        <div class='l'>{L('Your bike, damaged on shift', 'शिफ़्ट में गाड़ी का नुक़सान')}
          <small>{L('paid straight to a network garage', 'पैसा सीधे नेटवर्क गैरेज को')}</small></div>
        <div class='r'>{inr(ben['vehicle']['per_event'])}<small>{L('per event', 'प्रति घटना')}</small></div>
      </div>
      <div class='gs-row' style='padding-left:0;padding-right:0'>
        <div class='l'>{L('An order the platform deducts from your pay', 'जिस ऑर्डर का पैसा प्लेटफ़ॉर्म काट लेता है')}
          <small>{L('spillage, damage, undelivered consignment', 'गिरना, टूटना, ऑर्डर न पहुँचना')}</small></div>
        <div class='r'>{L('The exact amount', 'पूरी रकम')}</div>
      </div>
      <div class='gs-row' style='padding-left:0;padding-right:0;border-bottom:none'>
        <div class='l'>{L('Phone screen and EV battery', 'फ़ोन स्क्रीन और EV बैटरी')}
          <small>{L('repaired at our network, never cash', 'हमारे नेटवर्क पर मरम्मत, नक़द नहीं')}</small></div>
        <div class='r'>{L('Covered', 'कवर')}</div>
      </div>
    </div>""")
    st.write("")
    if st.button(L("What Ride Shield pays →", "Ride Shield क्या देता है →"),
                 key="p2", width="stretch"):
        st.switch_page(C.RIDE)

T.spacer()

# ------------------------------------------------------------------ price teaser
T.heading(
    L("Pricing", "क़ीमत"),
    L("You pay for hours ridden. Not for a year you did not use.",
      "आप चलाए गए घंटों का पैसा देते हैं। पूरे साल का नहीं।"),
    L("Move the slider to your own hours. This is the same rating engine that "
      "prices our book — not a marketing estimate.",
      "स्लाइडर को अपने घंटों पर ले जाइए। यह वही रेटिंग इंजन है जो हमारी पूरी "
      "बुक की क़ीमत तय करता है — कोई अनुमान नहीं।"))

v = Q.visitor()
cc = st.columns([1.5, 1.3, 1.3])
v["hours_pm"] = cc[0].slider(
    L("Hours you ride in a month", "महीने में कितने घंटे चलाते हैं"),
    20, 280, int(v["hours_pm"]), 10, key="home_hours")
v["city"] = cc[1].selectbox(L("Where you ride", "कहाँ चलाते हैं"),
                            list(CFG["city"].keys()),
                            index=list(CFG["city"]).index(v["city"]),
                            key="home_city")
v["platform"] = cc[2].selectbox(L("Mostly for", "ज़्यादातर किसके लिए"),
                                list(CFG["platform"].keys()),
                                index=list(CFG["platform"]).index(v["platform"]),
                                key="home_plat")

qs = Q.all_tiers(v)
flat = Q.flat_annual("GigSure Plus")
plus = qs["GigSure Plus"]

st.write("")
pc = st.columns(len(qs))
for i, (tier, q) in enumerate(qs.items()):
    name = tier.replace("GigSure ", "")
    with pc[i]:
        st.html(f"""
        <div class='gs gs-card {'accent' if tier == 'GigSure Plus' else ''}'
             style='background:#fff'>
          <div style='font-size:.72rem;font-weight:800;letter-spacing:.1em;
                      text-transform:uppercase;color:#FF6A35;height:1rem'>
            {L('Most riders', 'ज़्यादातर राइडर') if tier == 'GigSure Plus' else ''}</div>
          <h3 style='margin-top:.35rem'>{name}</h3>
          <div class='amt'>₹{q['premium_per_hour']:.2f}
            <small>{L('an hour', 'प्रति घंटा')}</small></div>
          <p><b>{inr(q['premium_month'])}</b> {L('a month at', 'महीने में, अगर आप')}
             {v['hours_pm']} {L('hours', 'घंटे चलाते हैं')} ·
             {L('about', 'लगभग')} ₹{q['premium_month'] / q['days_per_month']:.0f}
             {L('on a working day', 'एक कामकाजी दिन')}</p>
        </div>""")

st.write("")
saving = flat - plus["premium_year"]
if saving > 0:
    T.callout(L(
        f"A flat annual policy has to be priced for a full-time rider — "
        f"{Q.FLAT_HOURS_PM} hours a month — because the insurer cannot see who "
        f"is light and who is heavy. That is about <b>{inr(flat)} a year</b>. "
        f"You ride {v['hours_pm']} hours, so you pay "
        f"<b>{inr(plus['premium_year'])}</b> — <b>{inr(saving)} less</b>, "
        "because you are not carrying someone else's exposure.",
        f"फ़्लैट सालाना पॉलिसी को पूरे समय चलाने वाले राइडर के हिसाब से — महीने "
        f"में {Q.FLAT_HOURS_PM} घंटे — क़ीमत तय करनी पड़ती है, क्योंकि कंपनी को "
        f"पता नहीं चलता कौन कम चलाता है और कौन ज़्यादा। यानी क़रीब "
        f"<b>{inr(flat)} सालाना</b>। आप {v['hours_pm']} घंटे चलाते हैं, इसलिए "
        f"आप <b>{inr(plus['premium_year'])}</b> देते हैं — <b>{inr(saving)} कम</b>।"))
else:
    T.callout(L(
        f"You ride more than the full-time rider a flat annual policy is priced "
        f"for, so usage pricing costs you <b>{inr(-saving)} more</b> — and "
        "covers you properly for the exposure you actually carry. This is the "
        "honest half of usage-based pricing: it is cheaper for most riders "
        "precisely because it is not cheaper for everyone.",
        f"जिस पूर्णकालिक राइडर के हिसाब से फ़्लैट पॉलिसी की क़ीमत तय होती है, आप "
        f"उससे भी ज़्यादा चलाते हैं — इसलिए यूज़-आधारित क़ीमत आपको "
        f"<b>{inr(-saving)} ज़्यादा</b> पड़ती है, और आपके असली जोखिम को ठीक से "
        "कवर करती है। यूज़-आधारित क़ीमत का ईमानदार पक्ष यही है: यह ज़्यादातर "
        "राइडर के लिए इसीलिए सस्ती है क्योंकि हर किसी के लिए सस्ती नहीं है।"))

st.write("")
if st.button(L("See every rating factor, in full →",
               "हर रेटिंग फ़ैक्टर, पूरा देखें →"), key="topricing"):
    st.switch_page(C.PRICING)

T.spacer()

# ---------------------------------------------------------------------- claims
T.heading(
    L("Claims", "क्लेम"),
    L("A claim paid in four months is not a claim paid.",
      "चार महीने बाद मिला पैसा, पैसा नहीं है।"),
    L("Speed of settlement is not a service feature for a gig worker — it is "
      "the product. Everything here is built to make a claim payable within a "
      "day.", "गिग वर्कर के लिए जल्दी भुगतान कोई सुविधा नहीं — वही असली प्रोडक्ट "
      "है। यहाँ सब कुछ इसी के लिए बना है कि क्लेम एक दिन में चुकाया जा सके।"),
    wide=True)
st.write("")

T.steps([
    {"title": L("Tap once in the app", "ऐप में एक बार टैप करें"),
     "body": L("Pick what happened from a list. No forms, no branch, no agent. "
               "Voice input in your language if you would rather speak.",
               "सूची में से चुनें कि क्या हुआ। न फ़ॉर्म, न ब्रांच, न एजेंट। "
               "चाहें तो अपनी भाषा में बोलकर बताएँ।"),
     "time": L("30 seconds", "30 सेकंड")},
    {"title": L("We already have the evidence", "सबूत हमारे पास पहले से है"),
     "body": L("Your ride data shows where you were, how fast, and whether "
               "there was an impact. You are not asked to prove what we can "
               "already see.",
               "आपका राइड डेटा बताता है कि आप कहाँ थे, कितनी रफ़्तार पर, और "
               "टक्कर हुई या नहीं। जो हम देख सकते हैं, उसका सबूत आपसे नहीं माँगा जाता।"),
     "time": L("Automatic", "अपने आप")},
    {"title": L("Decision, with a reason", "फ़ैसला, कारण के साथ"),
     "body": L("Ambulance, phone and order claims are decided by machine in "
               "minutes. Injury claims get a panel doctor. Either way you get "
               "the reason in writing, in your language.",
               "एम्बुलेंस, फ़ोन और ऑर्डर के क्लेम मशीन कुछ मिनटों में तय करती "
               "है। चोट के क्लेम पर पैनल डॉक्टर देखता है। कारण आपको लिखित में, "
               "आपकी भाषा में मिलता है।"),
     "time": L(f"{sp['instant_heads_minutes']} min – {sp['standard_head_hours']} hrs",
               f"{sp['instant_heads_minutes']} मिनट – {sp['standard_head_hours']} घंटे")},
    {"title": L("Money in your UPI", "पैसा आपके UPI में"),
     "body": L("Paid to your UPI, not by cheque, not to a garage you have to "
               "argue with. On a death claim we release ₹1,00,000 to the family "
               "within 48 hours, before any investigation finishes.",
               "पैसा आपके UPI में — न चेक, न किसी गैरेज से बहस। मृत्यु के क्लेम "
               "पर परिवार को 48 घंटे में ₹1,00,000 जारी कर देते हैं, जाँच पूरी "
               "होने से पहले।"),
     "time": L("Same day", "उसी दिन")},
])

st.write("")
T.callout(pick(sp, "late_payment_penalty_note"))
st.write("")
if st.button(L("Read our published claims record →",
               "हमारा प्रकाशित क्लेम रिकॉर्ड पढ़ें →"), key="toclaims"):
    st.switch_page(C.CLAIMS)

T.spacer()

# ---------------------------------------------------------------- testimonials
T.heading(L("Riders", "राइडर"),
          L("What riders say it changed", "राइडर कहते हैं क्या बदला"),
          L("Composite riders drawn from the segments we serve.",
            "जिन वर्गों के लिए हम काम करते हैं, उनसे बने प्रतिनिधि उदाहरण।"))
st.write("")
T.quotes([{"quote": pick(t, "quote"), "name": t["name"], "role": pick(t, "role")}
          for t in SITE["testimonials"][:3]], cols=3)

T.spacer()

# ------------------------------------------------------------------- referral
r = SITE["referral"]
rc1, rc2 = st.columns([1.55, 1])
with rc1:
    T.heading(L("Referral", "रेफ़रल"),
              L(f"₹{r['reward_each_side']} to you, ₹{r['reward_each_side']} to them",
                f"₹{r['reward_each_side']} आपको, ₹{r['reward_each_side']} उन्हें"),
              L("Riders trust riders more than they trust any advertisement, so "
                "this is where most of our growth comes from. Share your code in "
                "your hub's WhatsApp group. When they have ridden "
                f"{r['qualify_after_hours']} covered hours, both of you are paid "
                "to UPI.",
                "राइडर किसी विज्ञापन से ज़्यादा दूसरे राइडर पर भरोसा करते हैं, "
                "इसलिए हमारी ज़्यादातर बढ़त यहीं से आती है। अपने हब के WhatsApp "
                f"ग्रुप में कोड भेजें। जब वे {r['qualify_after_hours']} कवर वाले "
                "घंटे चला लें, दोनों को UPI में पैसा मिलेगा।"))
    st.write("")
    if st.button(L("How referral works →", "रेफ़रल कैसे काम करता है →"), key="toref"):
        st.switch_page(C.REFERRAL)
with rc2:
    T.cards([{"icon": "🤝", "title": L("No cap on who you can refer",
                                       "किसे रेफ़र करें, कोई पाबंदी नहीं"),
              "body": L(f"Up to ₹{r['monthly_cap_per_rider']:,} a month. Depot "
                        "riders get the reward and a lower base rate.",
                        f"महीने में ₹{r['monthly_cap_per_rider']:,} तक। डिपो "
                        "राइडर को इनाम के साथ कम बेस रेट भी।"),
              "variant": "cream"}], cols=1)

T.spacer()

C.closing_cta(key="home_close")
C.footer()
