"""
Synthetic rider and trip generator.

There is no public gig-worker telematics dataset, so the demo runs on
simulated data. Distributions are drawn to match the report:

  - about a quarter of platform workers ride more than eight hours a day
  - about a third work purely in their free time
  - net monthly earnings of Rs 22,000-23,000 for a full-time delivery rider
<<<<<<< HEAD
  - claim frequencies from the burning cost table in section 6.1
=======
  - claim frequencies from the burning cost table in section 4
>>>>>>> 03dbdc9 (Initial commit)

The generator is deliberately visible so the assumptions can be inspected
and challenged rather than taken on trust.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

from .config import CFG, band_for_age, band_for_score
from . import safety_score as ss

TIME_BANDS = ["05:00-11:00", "11:00-16:00", "16:00-19:00", "19:00-23:00", "23:00-05:00"]
# How a typical rider's hours distribute across the day
TIME_BAND_WEIGHTS = [0.15, 0.20, 0.28, 0.27, 0.10]
WEATHER = ["Clear", "Light rain", "Heavy rain", "Fog / low visibility", "Heat index > 42C"]
WEATHER_WEIGHTS = [0.68, 0.14, 0.06, 0.04, 0.08]


def _pick(rng, mapping):
    keys = list(mapping.keys())
    probs = np.array([mapping[k] for k in keys], dtype=float)
    probs = probs / probs.sum()
    return rng.choice(keys, p=probs)


def generate_riders(cfg: dict | None = None, n: int | None = None,
                    seed: int | None = None) -> pd.DataFrame:
    cfg = cfg or CFG
    s = cfg["synthetic"]
    n = n or s["n_riders"]
    rng = np.random.default_rng(seed if seed is not None else s["seed"])

    rows = []
    for i in range(n):
        segment = _pick(rng, s["segment_mix"])
        lo, hi = s["hours_per_month"][segment]
        hours = float(rng.uniform(lo, hi))
        elo, ehi = s["monthly_earnings"][segment]
        earnings = float(rng.uniform(elo, ehi))

        city = _pick(rng, s["city_mix"])
        platform = _pick(rng, s["platform_mix"])
        vehicle = _pick(rng, s["vehicle_mix"])

        # Age: skewed young, which is what drives the 18-21 loading mattering
        age = int(np.clip(rng.normal(28, 7), 18, 58))

        # Safety score: beta-shaped, centred around the high 60s / low 70s
        raw_profile = {
            k: float(np.clip(
                rng.normal(ss.default_inputs("average")[k],
                           ss.default_inputs("average")[k] * 0.55), 0, None))
            for k in ss.SCALES
        }
        score = ss.compute(raw_profile, cfg)["score"]

        # Tenure: heavy churn, so most riders are new
        tenure = int(np.clip(rng.exponential(7), 0, 40))

        night_share = float(np.clip(rng.beta(2, 6) * 100, 0, 80))

        rows.append({
            "rider_id": f"R{i+1:05d}",
            "segment": segment,
            "age": age,
            "age_band": band_for_age(age),
            "city": city,
            "platform": platform,
            "vehicle": vehicle,
            "hours_per_month": round(hours, 1),
            "monthly_net_earnings": round(earnings),
            "daily_net_earnings": round(earnings / 26.0),
            "safety_score": score,
            "safety_band": band_for_score(score),
            "tenure_months": tenure,
            "night_riding_share": round(night_share, 1),
            **{f"tel_{k}": round(v, 2) for k, v in raw_profile.items()},
        })

    return pd.DataFrame(rows)


def generate_trips(riders: pd.DataFrame, cfg: dict | None = None,
                   blocks_per_rider: int = 24,
                   seed: int | None = None) -> pd.DataFrame:
    """
    A sample of 15-minute on-duty blocks per rider, with the conditions that
    drive the exposure multipliers. Used by the Risk Explorer heatmaps.
    """
    cfg = cfg or CFG
    rng = np.random.default_rng((seed if seed is not None
                                 else cfg["synthetic"]["seed"]) + 1)

    n = len(riders)
    rider_ids = np.repeat(riders["rider_id"].values, blocks_per_rider)
    cities = np.repeat(riders["city"].values, blocks_per_rider)
    total = n * blocks_per_rider

    bands = rng.choice(TIME_BANDS, size=total, p=TIME_BAND_WEIGHTS)
    weather = rng.choice(WEATHER, size=total, p=WEATHER_WEIGHTS)
    minutes = rng.uniform(8, 15, size=total)

    m_time = np.array([cfg["time_of_day"][b] for b in bands])
    m_weather = np.array([cfg["weather"][w] for w in weather])
    m_geo = np.array([cfg["city"][c] for c in cities])
    eeu = (minutes / 60.0) * m_time * m_weather * m_geo

    return pd.DataFrame({
        "rider_id": rider_ids,
        "city": cities,
        "time_band": bands,
        "weather": weather,
        "active_minutes": np.round(minutes, 1),
        "m_time": m_time,
        "m_weather": m_weather,
        "m_geo": m_geo,
        "eeu": np.round(eeu, 4),
    })


def simulate_claims(riders: pd.DataFrame, cfg: dict | None = None,
                    seed: int | None = None) -> pd.DataFrame:
    """
    Draw claims for each rider from the burning cost frequencies, scaled by
    exposure. A rider working twice the hours has roughly twice the frequency -
    which is the whole argument for exposure-based pricing.
    """
    cfg = cfg or CFG
    rng = np.random.default_rng((seed if seed is not None
                                 else cfg["synthetic"]["seed"]) + 2)

    full_time_hours = 208.0  # reference: full-time rider, hours per month
    rows = []
    for _, r in riders.iterrows():
        exposure_ratio = r["hours_per_month"] / full_time_hours
        # Riskier riders claim more often
        risk_ratio = cfg["safety_score_bands"][r["safety_band"]]
        for head in cfg["burning_cost"]:
            lam = (head["frequency_per_1000"] / 1000.0) * exposure_ratio * risk_ratio
            count = rng.poisson(lam)
            if count:
                rows.append({
                    "rider_id": r["rider_id"],
                    "head": head["head"],
                    "count": int(count),
                    "amount": int(count * head["average_claim"]),
                })
    return pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=["rider_id", "head", "count", "amount"])
