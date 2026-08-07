"""
Rider Safety Score (0-100) from smartphone telematics.

Business plan reference: section 5.2, Layer B.

Each behavioural input is normalised to a 0-100 sub-score where 100 is safest,
then combined using the weights in rating_factors.yaml. The worker sees this
score and exactly which inputs are dragging it down.
"""
from __future__ import annotations
from .config import CFG, band_for_score

# (worst_value, best_value) for each input. Values are clipped to this range
# before normalising. "worst" scores 0, "best" scores 100.
SCALES = {
    "harsh_braking":          (25.0, 0.0),   # events per 100 km
    "harsh_acceleration":     (25.0, 0.0),   # events per 100 km
    "cornering_severity":     (10.0, 0.0),   # severe cornering events per 100 km
    "over_speeding":          (30.0, 0.0),   # % of distance above limit
    "screen_on_while_moving": (20.0, 0.0),   # % of moving time
    "night_riding_share":     (60.0, 0.0),   # % of hours after 11pm
    "fatigue_events":         (12.0, 0.0),   # sessions >4hrs without break, per month
    "deliveries_per_hour":    (5.0, 1.5),    # rushing proxy
}

LABELS = {
    "harsh_braking": "Harsh braking / 100 km",
    "harsh_acceleration": "Harsh acceleration / 100 km",
    "cornering_severity": "Cornering severity / 100 km",
    "over_speeding": "Over-speeding (% of distance)",
    "screen_on_while_moving": "Screen-on while moving (% of time)",
    "night_riding_share": "Night riding share (%)",
    "fatigue_events": "Fatigue events / month",
    "deliveries_per_hour": "Deliveries per active hour",
}


def _normalise(key: str, value: float) -> float:
    """Map a raw telematics value to a 0-100 sub-score (100 = safest)."""
    worst, best = SCALES[key]
    lo, hi = min(worst, best), max(worst, best)
    v = max(lo, min(hi, value))
    if worst == best:
        return 100.0
    return 100.0 * (worst - v) / (worst - best)


def compute(inputs: dict, cfg: dict | None = None) -> dict:
    """
    inputs: raw telematics values keyed as in SCALES.
    Returns the overall score, the band, the premium multiplier, and the
    per-input contribution so the app can show what to improve.
    """
    cfg = cfg or CFG
    weights = cfg["safety_score_weights"]

    subs, contributions = {}, {}
    total = 0.0
    for key, weight in weights.items():
        raw = inputs.get(key, 0.0)
        sub = _normalise(key, raw)
        subs[key] = sub
        contributions[key] = {
            "label": LABELS[key],
            "raw": raw,
            "sub_score": sub,
            "weight": weight,
            "weighted": sub * weight,
            # points lost against a perfect score - what to fix first
            "points_lost": (100.0 - sub) * weight,
        }
        total += sub * weight

    score = round(total, 1)
    band = band_for_score(score)
    return {
        "score": score,
        "band": band,
        "multiplier": cfg["safety_score_bands"][band],
        "contributions": contributions,
        "biggest_opportunity": max(
            contributions.values(), key=lambda c: c["points_lost"]
        )["label"],
    }


def default_inputs(profile: str = "average") -> dict:
    """Preset telematics profiles for the demo."""
    presets = {
        "safe": dict(harsh_braking=3, harsh_acceleration=2, cornering_severity=1,
                     over_speeding=4, screen_on_while_moving=2,
                     night_riding_share=8, fatigue_events=1, deliveries_per_hour=2.0),
        "average": dict(harsh_braking=9, harsh_acceleration=8, cornering_severity=3.5,
                        over_speeding=12, screen_on_while_moving=7,
                        night_riding_share=22, fatigue_events=4, deliveries_per_hour=2.8),
        "risky": dict(harsh_braking=18, harsh_acceleration=17, cornering_severity=7,
                      over_speeding=24, screen_on_while_moving=15,
                      night_riding_share=45, fatigue_events=9, deliveries_per_hour=4.2),
    }
    return presets.get(profile, presets["average"])
