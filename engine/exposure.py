"""
Effective Exposure Unit (EEU) - the exposure base for the whole pricing model.

Business plan reference: section 1.2.

    EEU_b = (active_minutes_b / 60) x M_time(b) x M_weather(b) x M_geo(b)
    EEU_total = sum over blocks b

One EEU is "one hour of ordinary daytime riding in fair weather on a tier-1
city road." An hour at 10pm in heavy rain in a metro is roughly 2.2 EEU.
"""
from __future__ import annotations
from dataclasses import dataclass

from .config import CFG


@dataclass
class Block:
    """A 15-minute slice of on-duty riding."""
    active_minutes: float
    time_band: str
    weather: str
    city: str

    def multipliers(self, cfg: dict | None = None) -> dict:
        cfg = cfg or CFG
        return {
            "time": cfg["time_of_day"][self.time_band],
            "weather": cfg["weather"][self.weather],
            "geo": cfg["city"][self.city],
        }

    def eeu(self, cfg: dict | None = None) -> float:
        m = self.multipliers(cfg)
        return (self.active_minutes / 60.0) * m["time"] * m["weather"] * m["geo"]


def eeu_total(blocks: list[Block], cfg: dict | None = None) -> float:
    """Sum EEU across a list of blocks."""
    return sum(b.eeu(cfg) for b in blocks)


def eeu_simple(hours: float, time_band: str, weather: str, city: str,
               cfg: dict | None = None) -> float:
    """
    Convenience wrapper: treat `hours` as a single homogeneous stretch of
    riding. Used by the quote page, where the user sets one set of conditions.
    """
    return Block(hours * 60.0, time_band, weather, city).eeu(cfg)


def eeu_breakdown(hours: float, time_band: str, weather: str, city: str,
                  cfg: dict | None = None) -> dict:
    """Return the EEU and each contributing multiplier, for display."""
    cfg = cfg or CFG
    b = Block(hours * 60.0, time_band, weather, city)
    m = b.multipliers(cfg)
    return {
        "raw_hours": hours,
        "m_time": m["time"],
        "m_weather": m["weather"],
        "m_geo": m["geo"],
        "combined_exposure_multiplier": m["time"] * m["weather"] * m["geo"],
        "eeu": b.eeu(cfg),
    }
