"""
Shared furniture for every site page: the utility bar at the top, the primary
call-to-action row, and the footer.

Navigation itself is the native top bar produced by `st.navigation(position=
"top")` in app.py — there is no sidebar anywhere in the product now. What lives
here is the commercial chrome that sits inside the page: the trust line, the
language switch, and the two buttons that carry a visitor from understanding
to registration.
"""
from __future__ import annotations

import streamlit as st

from . import theme as T
from .i18n import L, toggle
from .content import SITE, pick

# Route constants — one place to change if a page is renamed.
HOME      = "web/home.py"
RIDER     = "web/rider_shield.py"
RIDE      = "web/ride_shield.py"
PRICING   = "web/pricing.py"
CLAIMS    = "web/claims.py"
WHY       = "web/why.py"
REGISTER  = "web/register.py"
REFERRAL  = "web/referral.py"
TRUST     = "web/trust.py"
APP_HOME  = "views/rider_home.py"
APP_BUY   = "views/rider_buy.py"


def utility_bar(right_note: str = ""):
    """
    Thin strip above the fold: what we are, and the language switch.

    The claims line is deliberately the first thing on the page. The plan makes
    published settlement data the primary trust instrument (§3.3), and a gig
    worker's first question about any insurer is whether it actually pays.

    This also boots the stylesheet, so a page can never render unstyled by
    forgetting to call `theme.boot()`.
    """
    T.boot()
    cr = SITE["claims_report"]
    note = right_note or L(
        f"{cr['settlement_ratio']:.1%} of claims paid · "
        f"median {cr['median_turnaround_hours']:.1f} hours to settle",
        f"{cr['settlement_ratio']:.1%} क्लेम का भुगतान · "
        f"औसतन {cr['median_turnaround_hours']:.1f} घंटे में निपटारा")

    c1, c2 = st.columns([5, 1.25], vertical_alignment="center")
    with c1:
        st.html(
            "<div class='gs gs-util' style='border:none;margin:0;padding:.1rem 0'>"
            "<div class='tag'><span class='dot'></span>"
            f"{L('Usage-based insurance for India&rsquo;s gig workers', 'भारत के गिग वर्कर्स के लिए यूज़-आधारित बीमा')}"
            f"</div><div class='meta'>{note}</div></div>")
    with c2:
        toggle()
    st.html("<div style='border-top:1px solid #E3EAE8;margin:.15rem 0 1.15rem'></div>")


def cta_row(primary_label: str | None = None, primary_page: str = REGISTER,
            secondary_label: str | None = None, secondary_page: str = PRICING,
            key: str = "cta"):
    """The two-button conversion path. Present on every page, always the same."""
    p = primary_label or L("Get covered in 90 seconds", "90 सेकंड में कवर पाएँ")
    s = secondary_label or L("See what it costs me", "मेरा ख़र्च देखें")
    c = st.columns([1.5, 1.4, 3])
    if c[0].button(p, type="primary", width="stretch", key=f"{key}_p"):
        st.switch_page(primary_page)
    if c[1].button(s, width="stretch", key=f"{key}_s"):
        st.switch_page(secondary_page)


def closing_cta(key: str = "close"):
    """The band at the bottom of every page, plus the buttons under it."""
    cr = SITE["claims_report"]
    T.cta_band(
        L("Your policy. Not the app&rsquo;s.",
          "पॉलिसी आपकी। ऐप की नहीं।"),
        L("No joining fee, no lock-in, nothing to pay on a day you do not ride. "
          "Aadhaar, your vehicle number and a UPI mandate — that is the whole "
          "sign-up.",
          "कोई जॉइनिंग फ़ीस नहीं, कोई लॉक-इन नहीं, जिस दिन न चलाएँ उस दिन कुछ "
          "नहीं देना। आधार, गाड़ी नंबर और UPI मैंडेट — बस इतना ही।"),
        L("₹1.50", "₹1.50"),
        L("per hour, where cover starts", "प्रति घंटा से कवर शुरू"))
    st.write("")
    cta_row(key=key)


def footer():
    cr = SITE["claims_report"]
    st.write("")
    st.html(f"""
    <div class='gs gs-foot'>
      <div class='cols'>
        <div>
          <div class='lg'>GigSure</div>
          <p>{L('Insurance that belongs to you, not to the app you ride for. One portable, usage-priced cover that stays live across every platform you earn from, replaces your income when you cannot ride, and settles a claim within a day.', 'ऐसा बीमा जो आपका है, उस ऐप का नहीं जिसके लिए आप चलाते हैं। एक पोर्टेबल, उपयोग-आधारित कवर — हर प्लेटफ़ॉर्म पर चालू, न चला पाने पर कमाई की भरपाई, और एक दिन में क्लेम का निपटारा।')}</p>
        </div>
        <div>
          <h5>{L('Cover', 'कवर')}</h5>
          <ul>
            <li>{L('Rider Shield — you', 'Rider Shield — आप')}</li>
            <li>{L('Ride Shield — your bike', 'Ride Shield — आपकी गाड़ी')}</li>
            <li>{L('Shift Pass — one shift', 'Shift Pass — एक शिफ़्ट')}</li>
            <li>{L('Family top-up', 'फ़ैमिली टॉप-अप')}</li>
          </ul>
        </div>
        <div>
          <h5>{L('Straight answers', 'सीधी बात')}</h5>
          <ul>
            <li>{L('What a claim costs you: nothing', 'क्लेम पर आपका ख़र्च: शून्य')}</li>
            <li>{L('Cancel any time, two taps', 'कभी भी बंद करें, दो टैप')}</li>
            <li>{L('Withdraw data consent, keep cover', 'डेटा सहमति वापस लें, कवर चालू')}</li>
            <li>{L('Complaints published monthly', 'शिकायतें हर महीने प्रकाशित')}</li>
          </ul>
        </div>
        <div>
          <h5>{L('Talk to us', 'हमसे बात करें')}</h5>
          <ul>
            <li>{L('Voice support, 8 languages', 'वॉइस सपोर्ट, 8 भाषाएँ')}</li>
            <li>{L('WhatsApp, 24 hours', 'WhatsApp, 24 घंटे')}</li>
            <li>{L('At your hub, at shift change', 'आपके हब पर, शिफ़्ट बदलते समय')}</li>
            <li>{L('Grievance officer', 'शिकायत अधिकारी')}</li>
          </ul>
        </div>
      </div>
      <div class='rule'></div>
      <div class='fine'>
        {L('GigSure is a prototype built for an academic business plan (IIM Ahmedabad, BFS, Term IV, Group 6). It is not an authorised insurer and no cover is being sold. Registration with the IRDAI under the Insurance Act, 1938 is a precondition of writing any business.', 'GigSure एक अकादमिक बिज़नेस प्लान (IIM अहमदाबाद, BFS, टर्म IV, ग्रुप 6) के लिए बनाया गया प्रोटोटाइप है। यह अधिकृत बीमा कंपनी नहीं है और कोई कवर नहीं बेचा जा रहा। बीमा अधिनियम, 1938 के तहत IRDAI पंजीकरण अनिवार्य है।')}<br>
        {L('Claims figures shown are the modelled steady-state book for', 'दिखाए गए क्लेम आँकड़े मॉडल किए गए स्थिर बुक के हैं —')} {cr['period']}, {L('not live experience. Every rating factor is published in full on the Pricing page.', 'वास्तविक अनुभव नहीं। हर रेटिंग फ़ैक्टर प्राइसिंग पेज पर पूरा प्रकाशित है।')}
      </div>
    </div>""")
