"""
The premium function.

<<<<<<< HEAD
Business plan reference: section 5.3.
=======
Business plan reference: section 3.3.
>>>>>>> 03dbdc9 (Initial commit)

    P_day = BaseRate x (SI / 100000) x EEU_day
            x M_behaviour x M_age x M_vehicle x M_platform x M_fatigue
            x (1 - D_loyalty) x (1 + Load_expense) x (1 + Load_margin)

The product of the rating multipliers is capped in the band set in
rating_factors.yaml (0.6x to 2.2x). Above the cap we decline or mandate a
safety intervention rather than pricing the worker out of cover.
"""
from __future__ import annotations
from dataclasses import dataclass, field

from .config import CFG, band_for_age, band_for_score, loyalty_discount
from .exposure import eeu_breakdown


@dataclass
class RiderProfile:
    age: int = 27
    city: str = "Metro (Mumbai, Delhi, Bengaluru)"
    vehicle: str = "<=110cc petrol"
    platform: str = "Food delivery"
    tenure_months: int = 0
    safety_score: float = 72.0
    sum_insured: int = 1000000
    tier: str = "Suraksha Plus"


@dataclass
class ShiftContext:
    hours: float = 8.0
    time_band: str = "16:00-19:00"
    weather: str = "Clear"
    continuous_hours: str = "Under 8 continuous hours"
    days_per_month: int = 26


def rating_multipliers(rider: RiderProfile, shift: ShiftContext,
                       cfg: dict | None = None) -> dict:
    """The non-exposure multipliers, with their band labels, for display."""
    cfg = cfg or CFG
    age_band = band_for_age(rider.age)
    score_band = band_for_score(rider.safety_score)
    return {
        "M_behaviour": {"band": score_band,
                        "value": cfg["safety_score_bands"][score_band]},
        "M_age": {"band": age_band, "value": cfg["age"][age_band]},
        "M_vehicle": {"band": rider.vehicle, "value": cfg["vehicle"][rider.vehicle]},
        "M_platform": {"band": rider.platform,
                       "value": cfg["platform"][rider.platform]},
        "M_fatigue": {"band": shift.continuous_hours,
                      "value": cfg["fatigue"][shift.continuous_hours]},
    }


def quote(rider: RiderProfile, shift: ShiftContext, cfg: dict | None = None) -> dict:
    """
    Price one shift, one day and one month for this rider under these
    conditions. Returns every intermediate value so the app can show the
    full derivation rather than just a number.
    """
    cfg = cfg or CFG

    exp = eeu_breakdown(shift.hours, shift.time_band, shift.weather,
                        rider.city, cfg)

    mults = rating_multipliers(rider, shift, cfg)
<<<<<<< HEAD
    raw_product = 1.0
    for m in mults.values():
        raw_product *= m["value"]

    cap = cfg["multiplier_cap"]
    capped_product = max(cap["floor"], min(cap["ceiling"], raw_product))
    was_capped = abs(capped_product - raw_product) > 1e-9
=======
    rating_product = 1.0
    for m in mults.values():
        rating_product *= m["value"]

    exposure_product = exp["combined_exposure_multiplier"]

    # The governance band (§3.3) covers "time of day, weather, traffic, city
    # and behaviour score" - so the cap applies to the exposure and rating
    # factors combined, not to the rating factors alone. That is what makes a
    # Suraksha Plus rider pay between about Rs 1.50 and Rs 5.50 an hour rather
    # than an unbounded amount on a bad night.
    cap = cfg["multiplier_cap"]
    if cap.get("applies_to", "total") == "total":
        raw_product = exposure_product * rating_product
        capped_total = max(cap["floor"], min(cap["ceiling"], raw_product))
        # Split the capped total back out so the waterfall still reconciles:
        # exposure is charged in full up to the cap, the remainder is rating.
        capped_product = capped_total / exposure_product if exposure_product else 0.0
        priced_hours = shift.hours          # exposure is inside the cap
        eeu_for_pricing = shift.hours * exposure_product
    else:
        raw_product = rating_product
        capped_total = max(cap["floor"], min(cap["ceiling"], raw_product))
        capped_product = capped_total
        priced_hours = shift.hours
        eeu_for_pricing = exp["eeu"]

    was_capped = abs(capped_total - raw_product) > 1e-9
>>>>>>> 03dbdc9 (Initial commit)

    disc = loyalty_discount(rider.tenure_months, cfg)
    load_exp = cfg["loadings"]["expense"]
    load_mar = cfg["loadings"]["margin"]

<<<<<<< HEAD
    risk_premium = (cfg["base_rate"]
                    * (rider.sum_insured / 100000.0)
                    * exp["eeu"]
                    * capped_product)
=======
    # Premium is base x SI x hours x (capped total multiplier)
    risk_premium = (cfg["base_rate"]
                    * (rider.sum_insured / 100000.0)
                    * priced_hours
                    * capped_total)
>>>>>>> 03dbdc9 (Initial commit)

    premium_shift = risk_premium * (1 - disc) * (1 + load_exp) * (1 + load_mar)
    premium_per_hour = premium_shift / shift.hours if shift.hours else 0.0
    premium_month = premium_shift * shift.days_per_month
    premium_year = premium_month * 12

<<<<<<< HEAD
    return {
        "exposure": exp,
        "multipliers": mults,
        "raw_multiplier_product": raw_product,
        "capped_multiplier_product": capped_product,
=======
    band = price_band(rider, cfg)

    return {
        "exposure": exp,
        "multipliers": mults,
        "exposure_product": exposure_product,
        "rating_product": rating_product,
        "raw_multiplier_product": raw_product,
        "capped_multiplier_product": capped_product,
        "capped_total_multiplier": capped_total,
        "eeu_for_pricing": eeu_for_pricing,
        "band": band,
>>>>>>> 03dbdc9 (Initial commit)
        "was_capped": was_capped,
        "loyalty_discount": disc,
        "load_expense": load_exp,
        "load_margin": load_mar,
        "base_rate": cfg["base_rate"],
<<<<<<< HEAD
=======
        "sum_insured": rider.sum_insured,
>>>>>>> 03dbdc9 (Initial commit)
        "risk_premium_shift": risk_premium,
        "premium_shift": premium_shift,
        "premium_per_hour": premium_per_hour,
        "premium_day": premium_shift,
        "premium_month": premium_month,
        "premium_year": premium_year,
        "eeu_month": exp["eeu"] * shift.days_per_month,
        "eeu_year": exp["eeu"] * shift.days_per_month * 12,
    }


<<<<<<< HEAD
=======
def price_band(rider: RiderProfile, cfg: dict | None = None) -> dict:
    """
    The floor and ceiling hourly price for this rider's tier under the
    governance band (§3.3). For Suraksha Plus this should be about
    Rs 1.50 to Rs 5.50 an hour.
    """
    cfg = cfg or CFG
    cap = cfg["multiplier_cap"]
    unit = (cfg["base_rate"] * (rider.sum_insured / 100000.0)
            * (1 + cfg["loadings"]["expense"]) * (1 + cfg["loadings"]["margin"]))
    return {
        "floor_per_hour": unit * cap["floor"],
        "base_per_hour": unit,
        "ceiling_per_hour": unit * cap["ceiling"],
        "cap_floor": cap["floor"],
        "cap_ceiling": cap["ceiling"],
    }


>>>>>>> 03dbdc9 (Initial commit)
def waterfall(q: dict) -> list[dict]:
    """
    Build the step-by-step derivation for the waterfall chart on the quote page.
    Each step shows the running premium after applying one factor.
    """
    steps: list[dict] = []
<<<<<<< HEAD
    running = q["base_rate"] * (q["exposure"]["raw_hours"])  # notional start

    # Rebuild from the base so the chart matches the formula exactly.
    si_factor = q["risk_premium_shift"] / (
        q["base_rate"] * q["exposure"]["eeu"] * q["capped_multiplier_product"]
    ) if q["exposure"]["eeu"] else 0.0

    base = q["base_rate"] * si_factor * q["exposure"]["raw_hours"]
    steps.append({"label": "Base rate x SI x hours", "value": base})

    after_time = base * q["exposure"]["m_time"]
    steps.append({"label": f"Time of day (x{q['exposure']['m_time']:.2f})",
                  "value": after_time})

    after_weather = after_time * q["exposure"]["m_weather"]
    steps.append({"label": f"Weather (x{q['exposure']['m_weather']:.2f})",
                  "value": after_weather})

    after_geo = after_weather * q["exposure"]["m_geo"]
    steps.append({"label": f"City (x{q['exposure']['m_geo']:.2f})",
                  "value": after_geo})

    running = after_geo
    for name, m in q["multipliers"].items():
        running *= m["value"]
        pretty = name.replace("M_", "").replace("_", " ").title()
        steps.append({"label": f"{pretty} (x{m['value']:.2f})", "value": running})

    if q["loyalty_discount"]:
        running *= (1 - q["loyalty_discount"])
        steps.append({"label": f"Loyalty (-{q['loyalty_discount']:.0%})",
                      "value": running})

    running *= (1 + q["load_expense"])
    steps.append({"label": f"Expense load (+{q['load_expense']:.0%})", "value": running})

    running *= (1 + q["load_margin"])
    steps.append({"label": f"Margin load (+{q['load_margin']:.0%})", "value": running})
=======

    # Base: what this shift would cost at multiplier 1.0, before loadings.
    base = (q["base_rate"] * (q["sum_insured"] / 100000.0)
            * q["exposure"]["raw_hours"])
    running = base
    steps.append({"label": "Base rate × SI × hours", "value": running})

    for label, key in [("Time of day", "m_time"), ("Weather", "m_weather"),
                       ("City", "m_geo")]:
        running *= q["exposure"][key]
        steps.append({"label": f"{label} (×{q['exposure'][key]:.2f})",
                      "value": running})

    for name, m in q["multipliers"].items():
        running *= m["value"]
        pretty = name.replace("M_", "").replace("_", " ").title()
        steps.append({"label": f"{pretty} (×{m['value']:.2f})", "value": running})

    # Governance band, applied to the total.
    if q["was_capped"]:
        running = base * q["capped_total_multiplier"]
        steps.append({
            "label": f"Governance band (capped at ×{q['capped_total_multiplier']:.2f})",
            "value": running,
        })

    if q["loyalty_discount"]:
        running *= (1 - q["loyalty_discount"])
        steps.append({"label": f"Loyalty (−{q['loyalty_discount']:.0%})",
                      "value": running})

    running *= (1 + q["load_expense"])
    steps.append({"label": f"Expense load (+{q['load_expense']:.0%})",
                  "value": running})

    running *= (1 + q["load_margin"])
    steps.append({"label": f"Margin load (+{q['load_margin']:.0%})",
                  "value": running})
>>>>>>> 03dbdc9 (Initial commit)

    return steps
