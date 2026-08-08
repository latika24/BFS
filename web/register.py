"""
Get covered — the registration funnel.

This is where the website stops being a website. The form writes to the same
`engine.store` the rider app and the insurer console read from, so completing
it issues a real policy in the prototype: it appears under My cover, it appears
in the insurer's in-force book, and it can be claimed on immediately.

Three questions, three consents, ninety seconds. Everything else we can look up
— Aadhaar through DigiLocker, the vehicle through VAHAN, the licence through
Sarathi, earnings through the Account Aggregator framework. Asking a rider to
type what we can fetch is how sign-up funnels die.
"""
from __future__ import annotations

import time

import streamlit as st

from shared import inr
from engine import store
from engine.config import CFG
from web import theme as T, chrome as C, quote as Q
from web.i18n import L

C.utility_bar()

v = Q.visitor()
existing = store.active_policies()

st.html(T.hero(
    L("Get covered", "कवर लें"),
    L("Three questions. Three tick boxes. <em>Ninety seconds.</em>",
      "तीन सवाल। तीन टिक। <em>नब्बे सेकंड।</em>"),
    L("No joining fee, no medical test, no lock-in, and nothing to pay on a day "
      "you do not ride. Cover starts the moment you go on duty — on any app.",
      "न जॉइनिंग फ़ीस, न मेडिकल टेस्ट, न लॉक-इन, और जिस दिन न चलाएँ उस दिन कुछ "
      "नहीं देना। ड्यूटी पर जाते ही कवर शुरू — किसी भी ऐप पर।"),
    compact=True))

T.spacer(1.1)

# --------------------------------------------------------------------- step 1
T.heading(L("Step 1", "क़दम 1"),
          L("Tell us how you work", "बताइए आप कैसे काम करते हैं"),
          L("These four answers set your price and your benefit amounts. "
            "Nothing here is a commitment.",
            "इन चार जवाबों से आपका रेट और आपकी रकम तय होती है। यहाँ कुछ भी "
            "बाध्यकारी नहीं है।"))
st.write("")

f1 = st.columns(4)
name = f1[0].text_input(L("Your name", "आपका नाम"),
                        value=store.rider().name, key="rg_name")
phone = f1[1].text_input(L("Mobile number", "मोबाइल नंबर"),
                         value=store.rider().phone, key="rg_phone")
reg = f1[2].text_input(L("Vehicle number", "गाड़ी नंबर"),
                       value=store.rider().vehicle_reg, key="rg_reg")
v["age"] = f1[3].number_input(L("Age", "उम्र"), 18, 65, int(v["age"]), 1,
                              key="rg_age")

f2 = st.columns(4)
v["hours_pm"] = f2[0].slider(L("Hours you ride a month", "महीने में घंटे"),
                             20, 280, int(v["hours_pm"]), 10, key="rg_hours")
v["city"] = f2[1].selectbox(L("Where you ride", "कहाँ चलाते हैं"),
                            list(CFG["city"].keys()),
                            index=list(CFG["city"]).index(v["city"]), key="rg_city")
v["platform"] = f2[2].selectbox(L("Mostly for", "ज़्यादातर किसके लिए"),
                                list(CFG["platform"].keys()),
                                index=list(CFG["platform"]).index(v["platform"]),
                                key="rg_plat")
v["vehicle"] = f2[3].selectbox(L("Your vehicle", "आपकी गाड़ी"),
                               list(CFG["vehicle"].keys()),
                               index=list(CFG["vehicle"]).index(v["vehicle"]),
                               key="rg_veh")

v["earnings"] = st.slider(
    L("What you take home in a month (₹)", "महीने में हाथ में कितना आता है (₹)"),
    4000, 60000, int(v["earnings"]), 500, key="rg_earn",
    help=L("We verify this through the Account Aggregator framework at sign-up. "
           "It sets your benefit amounts, so an inflated figure here would only "
           "be corrected before the policy is issued.",
           "साइन-अप के समय हम इसे अकाउंट एग्रीगेटर से जाँचते हैं। इसी से आपकी "
           "रकम तय होती है, इसलिए बढ़ा-चढ़ाकर लिखा आँकड़ा पॉलिसी जारी होने से "
           "पहले ही ठीक कर दिया जाएगा।"))

T.spacer(1.1)

# --------------------------------------------------------------------- step 2
T.heading(L("Step 2", "क़दम 2"),
          L("Choose your plan", "अपना प्लान चुनें"))
st.write("")

qs = Q.all_tiers(v)
ben = Q.benefits(v)
if "rg_tier" not in st.session_state:
    st.session_state["rg_tier"] = "GigSure Plus"

pc = st.columns(len(qs))
for i, (tier, q) in enumerate(qs.items()):
    sel = st.session_state["rg_tier"] == tier
    feats = "".join(
        f"<div style='font-size:.85rem;line-height:1.75;"
        f"color:{'#3B4B48' if tier in tw else '#AEB9B7'}'>"
        f"{'✓' if tier in tw else '—'} {L(en, hi)}</div>"
        for en, hi, tw in Q.FEATURES)
    with pc[i]:
        st.html(f"""
        <div class='gs gs-card {'accent' if sel else ''}'>
          <h3>{tier.replace('GigSure ', '')}</h3>
          <div class='amt'>₹{q['premium_per_hour']:.2f}
            <small>{L('an hour', 'प्रति घंटा')}</small></div>
          <p style='margin-bottom:.7rem'><b>{inr(q['premium_month'])}</b>
             {L('a month at', 'महीना, अगर')} {v['hours_pm']}
             {L('hours', 'घंटे')} · {L('cover up to', 'कवर')}
             {inr(Q.TIERS[tier]['sum_insured_reference'])}</p>
          {feats}
        </div>""")
        if st.button(L("Selected", "चुना गया") if sel else L("Choose", "चुनें"),
                     key=f"rg_pick_{tier}", width="stretch",
                     type="primary" if sel else "secondary"):
            st.session_state["rg_tier"] = tier
            st.rerun()

tier = st.session_state["rg_tier"]
q = qs[tier]

st.write("")
ac = st.columns(3)
addons = []
if ac[0].checkbox(L("Family top-up — hospital cash and life cover for your "
                    "spouse and children (+₹0.40/hr)",
                    "फ़ैमिली टॉप-अप — पत्नी/पति और बच्चों के लिए अस्पताल कैश "
                    "और जीवन कवर (+₹0.40/घंटा)"), key="rg_a1"):
    addons.append("Family top-up")
if ac[1].checkbox(L("Phone screen and theft (+₹0.25/hr)",
                    "फ़ोन स्क्रीन और चोरी (+₹0.25/घंटा)"),
                  value=(tier == "GigSure Pro"), key="rg_a2"):
    addons.append("Phone screen")
if ac[2].checkbox(L("EV battery cover (+₹0.35/hr)",
                    "EV बैटरी कवर (+₹0.35/घंटा)"), key="rg_a3"):
    addons.append("EV battery")

addon_rate = (0.40 * ("Family top-up" in addons)
              + 0.25 * ("Phone screen" in addons and tier != "GigSure Pro")
              + 0.35 * ("EV battery" in addons))
final_hr = q["premium_per_hour"] + addon_rate
# Derive the month from the engine's own monthly figure rather than
# re-multiplying the hourly rate, so the order summary cannot disagree with
# the price on the plan card above it.
final_month = q["premium_month"] + addon_rate * v["hours_pm"]

T.spacer(1.1)

# --------------------------------------------------------------------- step 3
T.heading(L("Step 3", "क़दम 3"),
          L("Confirm and activate", "पुष्टि करके चालू करें"))
st.write("")

s1, s2 = st.columns([1, 1.15])

with s1:
    st.html(f"""
    <div class='gs gs-rows'>
      <div class='gs-row'><div class='l'>{L('Plan', 'प्लान')}</div>
        <div class='r'>{tier.replace('GigSure ', '')}</div></div>
      <div class='gs-row'><div class='l'>{L('Add-ons', 'ऐड-ऑन')}</div>
        <div class='r' style='font-size:.86rem'>{', '.join(addons) if addons else '—'}</div></div>
      <div class='gs-row'><div class='l'>{L('Your rate', 'आपका रेट')}
        <small>{L('only while you are riding', 'सिर्फ़ चलाते समय')}</small></div>
        <div class='r'>₹{final_hr:.2f}<small>{L('an hour', 'प्रति घंटा')}</small></div></div>
      <div class='gs-row'><div class='l'>{L('Roughly, in a month', 'महीने में लगभग')}
        <small>{L('at', 'अगर')} {v['hours_pm']} {L('hours a month', 'घंटे महीना')}</small></div>
        <div class='r'>{inr(final_month)}</div></div>
      <div class='gs-row'><div class='l'>{L('If you cannot ride', 'न चला पाने पर')}
        <small>{L('per day, after 3 days', 'रोज़, 3 दिन बाद')}</small></div>
        <div class='r'>{inr(ben['daily_income_benefit']['value'])}</div></div>
      <div class='gs-row'><div class='l'>{L('For your family', 'परिवार के लिए')}
        <small>{L('accidental death or permanent disability', 'दुर्घटना में मृत्यु या स्थायी विकलांगता')}</small></div>
        <div class='r'>{inr(ben['accidental_death']['value'])}</div></div>
      <div class='gs-row'><div class='l'>{L('Lock-in', 'लॉक-इन')}</div>
        <div class='r' style='color:#1F8A5B'>{L('None', 'कोई नहीं')}</div></div>
    </div>""")

with s2:
    st.markdown(f"**{L('Three consents, and one that is optional', 'तीन सहमतियाँ, और एक वैकल्पिक')}**")
    k1 = st.checkbox(L("Aadhaar KYC through DigiLocker",
                       "DigiLocker से आधार KYC"), value=True, key="rg_k1")
    k2 = st.checkbox(L(f"Vehicle {reg} and licence confirmed from VAHAN and Sarathi",
                       f"गाड़ी {reg} और लाइसेंस VAHAN और सारथी से पुष्ट"),
                     value=True, key="rg_k2")
    k3 = st.checkbox(L("UPI Autopay mandate — up to ₹60 a day, cancel any time",
                       "UPI ऑटोपे मैंडेट — रोज़ ₹60 तक, कभी भी बंद करें"),
                     value=False, key="rg_k3")
    k4 = st.checkbox(L("Share riding data so my price reflects how I actually "
                       "ride — I can withdraw this any time and keep my cover",
                       "राइडिंग डेटा साझा करें ताकि रेट मेरे चलाने के हिसाब से "
                       "हो — मैं इसे कभी भी वापस ले सकता/सकती हूँ और कवर बना रहेगा"),
                     value=True, key="rg_k4")

    ready = k1 and k2 and k3
    if not ready:
        st.caption(L("Tick the first three to activate.",
                     "चालू करने के लिए पहले तीन पर टिक करें।"))

    if st.button(L(f"Activate {tier.replace('GigSure ', '')} — ₹{final_hr:.2f}/hr",
                   f"{tier.replace('GigSure ', '')} चालू करें — ₹{final_hr:.2f}/घंटा"),
                 type="primary", width="stretch", disabled=not ready,
                 key="rg_go"):
        with st.status(L("Issuing your policy…", "आपकी पॉलिसी जारी हो रही है…"),
                       expanded=True) as status:
            st.write(L("Verifying identity and vehicle…",
                       "पहचान और गाड़ी की जाँच…"))
            time.sleep(0.4)
            st.write(L("Reading your earnings through the Account Aggregator…",
                       "अकाउंट एग्रीगेटर से आपकी कमाई पढ़ी जा रही है…"))
            time.sleep(0.4)
            st.write(L("Registering the UPI Autopay mandate…",
                       "UPI ऑटोपे मैंडेट दर्ज हो रहा है…"))
            time.sleep(0.4)

            rider = store.rider()
            rider.name = name or rider.name
            rider.phone = phone or rider.phone
            rider.vehicle_reg = reg or rider.vehicle_reg
            rider.age = int(v["age"])
            rider.city = v["city"]
            rider.platform = v["platform"]
            rider.vehicle = v["vehicle"]
            rider.monthly_net_earnings = int(v["earnings"])
            rider.telematics_consent = bool(k4)
            rider.kyc_done = True
            p = store.buy_policy(tier, addons)

            status.update(label=L(f"Policy {p.policy_id} is live",
                                  f"पॉलिसी {p.policy_id} चालू है"),
                          state="complete")
        st.balloons()
        st.session_state["rg_issued"] = p.policy_id

issued = st.session_state.get("rg_issued")
if issued:
    st.success(L(
        f"**You are covered.** Policy {issued} is active from now. Cover "
        "switches on the moment you start riding — on any app.",
        f"**आप कवर हैं।** पॉलिसी {issued} अभी से चालू है। जैसे ही आप चलाना "
        "शुरू करेंगे कवर ऑन हो जाएगा — किसी भी ऐप पर।"))
    dc = st.columns([1.5, 1.5, 3])
    if dc[0].button(L("Open my cover →", "मेरा कवर खोलें →"), type="primary",
                    width="stretch", key="rg_open"):
        st.switch_page("views/rider_policies.py")
    if dc[1].button(L("Refer a rider, earn ₹100 →", "राइडर जोड़ें, ₹100 पाएँ →"),
                    width="stretch", key="rg_ref"):
        st.switch_page(C.REFERRAL)
elif existing:
    st.info(L(
        f"You already hold {len(existing)} active "
        f"{'policy' if len(existing) == 1 else 'policies'} in this demo. "
        "Activating another one is fine — it will appear in the rider app and "
        "in the insurer's in-force book alongside the first.",
        f"इस डेमो में आपके पास पहले से {len(existing)} चालू पॉलिसी है। एक और "
        "चालू करना ठीक है — यह राइडर ऐप और इंश्योरर की बुक, दोनों में दिखेगी।"))

T.spacer()

# ------------------------------------------------------------------ reassurance
T.cards([
    {"icon": "wallet", "title": L("Nothing to pay today", "आज कुछ नहीं देना"),
     "body": L("The UPI mandate authorises a daily debit for hours ridden. If "
               "you do not ride, nothing is taken. If you cancel, the mandate "
               "goes with it.",
               "UPI मैंडेट सिर्फ़ चलाए गए घंटों की रोज़ाना कटौती की इजाज़त देता "
               "है। न चलाएँ तो कुछ नहीं कटेगा। बंद करने पर मैंडेट भी ख़त्म।")},
    {"icon": "hospital", "title": L("No medical test", "कोई मेडिकल टेस्ट नहीं"),
     "body": L("Benefits are sized from observed earnings rather than a "
               "declared sum insured, so there is nothing to underwrite about "
               "you personally at sign-up.",
               "रकम देखी गई कमाई से तय होती है, किसी घोषित बीमा राशि से नहीं — "
               "इसलिए साइन-अप पर आपकी निजी जाँच की ज़रूरत ही नहीं।")},
    {"icon": "check", "title": L("Cancel in two taps", "दो टैप में बंद"),
     "body": L("From the app, any time, with no exit fee and no notice period. "
               "You are charged for the hours you already rode and nothing more.",
               "ऐप से, कभी भी, न एग्ज़िट फ़ीस न नोटिस। जितने घंटे चला चुके हैं "
               "बस उतना ही, उससे ज़्यादा कुछ नहीं।")},
], cols=3)

T.spacer()
C.footer()
