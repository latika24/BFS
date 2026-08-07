"""Loads the rating configuration. Every number the model uses comes from here."""
from __future__ import annotations
from pathlib import Path
import yaml

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "rating_factors.yaml"


def load_config(path: Path | str | None = None) -> dict:
    """Read rating_factors.yaml into a dict."""
    p = Path(path) if path else CONFIG_PATH
    with open(p, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


CFG = load_config()


def band_for_score(score: float, cfg: dict | None = None) -> str:
    """Map a 0-100 safety score to its premium band label."""
    if score >= 90:
        return "90-100"
    if score >= 70:
        return "70-89"
    if score >= 50:
        return "50-69"
    return "Below 50"


def band_for_age(age: int) -> str:
    if age <= 21:
        return "18-21"
    if age <= 30:
        return "22-30"
    if age <= 45:
        return "31-45"
    return "46+"


def loyalty_discount(tenure_months: int, cfg: dict | None = None) -> float:
    """Step function on tenure. Returns the discount as a decimal."""
    cfg = cfg or CFG
    steps = sorted(cfg["loyalty_discount"].items())
    d = 0.0
    for months, disc in steps:
        if tenure_months >= months:
            d = disc
    return d
