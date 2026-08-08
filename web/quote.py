"""
The public quoting helper.

A visitor to the website has not signed up, so there is no rider record to
price against. This builds a profile from the four questions a stranger can
answer in ten seconds — how many hours, which city, which kind of work, what
they earn — and runs it through exactly the same `engine.pricing` used by the
insurer console. The site never shows a marketing number that the rating
engine would not stand behind.
"""
from __future__ import annotations

import streamlit as st

from engine import pricing, sum_insured as si_engine
from engine.config import CFG

TIERS = CFG["tiers"]

# What each tier actually contains, in worker language rather than head names.
FEATURES = [
    ("Death and permanent disability", "मृत्यु और स्थायी विकलांगता",
     ["GigSure Basic", "GigSure Plus", "GigSure Pro"]),
    ("Ambulance and first response", "एम्बुलेंस और तुरंत मदद",
     ["GigSure Basic", "GigSure Plus", "GigSure Pro"]),
    ("Broken bone benefit", "हड्डी टूटने पर भुगतान",
     ["GigSure Basic", "GigSure Plus", "GigSure Pro"]),
    ("Daily income while you cannot ride", "काम न कर पाने पर रोज़ की आमदनी",
     ["GigSure Plus", "GigSure Pro"]),
    ("Hospital daily cash", "अस्पताल का रोज़ का कैश",
     ["GigSure Plus", "GigSure Pro"]),
    ("Legal help after an FIR", "FIR के बाद क़ानूनी मदद",
     ["GigSure Plus", "GigSure Pro"]),
    ("Your bike, damaged on shift", "शिफ़्ट में गाड़ी का नुक़सान",
     ["GigSure Pro"]),
    ("Orders you get charged for", "जिन ऑर्डर का पैसा कटता है",
     ["GigSure Pro"]),
    ("Phone screen", "फ़ोन की स्क्रीन", ["GigSure Pro"]),
]

DEFAULTS = dict(hours_pm=120, city="Metro (Mumbai, Delhi, Bengaluru)",
                platform="Food delivery", earnings=22000, age=29,
                vehicle="<=110cc petrol", score=78.0, shift_len=8.0)

# The flat-premium benchmark.
#
# A conventional annual policy has to be priced for the exposure of a full-time
# rider, because the insurer cannot see who is light and who is heavy. The
# reference rider in rating_factors.yaml is exactly that rider — 8 hours a
# shift, 26 shifts a month — so their tier price times those hours is what a
# flat annual premium for this cover would have to be. Comparing against our
# own blended book average instead would flatter us, since that average is
# depressed by part-timers we would not be comparing against.
_REF = CFG["reference_rider"]
FLAT_HOURS_PM = _REF["hours_per_shift"] * _REF["days_per_month"]


def flat_annual(tier: str = "GigSure Plus") -> float:
    """What a flat annual policy for this cover would have to cost."""
    return TIERS[tier]["price_per_hour"] * FLAT_HOURS_PM * 12


def visitor() -> dict:
    """The visitor's answers, held in session so they survive page changes."""
    v = st.session_state.setdefault("gs_visitor", dict(DEFAULTS))
    for k, default in DEFAULTS.items():
        v.setdefault(k, default)
    return v


def price(tier: str = "GigSure Plus", v: dict | None = None,
          time_band: str = "16:00-19:00", weather: str = "Clear") -> dict:
    v = v or visitor()
    days = max(1, round(v["hours_pm"] / v["shift_len"]))
    prof = pricing.RiderProfile(
        age=v["age"], city=v["city"], vehicle=v["vehicle"],
        platform=v["platform"], tenure_months=0, safety_score=v["score"],
        sum_insured=TIERS[tier]["sum_insured_reference"], tier=tier)
    shift = pricing.ShiftContext(hours=v["shift_len"], time_band=time_band,
                                 weather=weather, days_per_month=days)
    q = pricing.quote(prof, shift)
    q["days_per_month"] = days
    return q


def all_tiers(v: dict | None = None) -> dict:
    v = v or visitor()
    return {t: price(t, v) for t in TIERS}


def benefits(v: dict | None = None) -> dict:
    v = v or visitor()
    return si_engine.full_schedule(v["earnings"])
