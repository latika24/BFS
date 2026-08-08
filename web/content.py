"""
Loads config/site_content.yaml — every number and claim the website makes.

`rating_factors.yaml` governs the risk model; this governs the marketing. Both
are data, neither is hard-coded in a page, and `pick()` resolves the bilingual
fields so a page never has to know which language is active.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from .i18n import is_hi

PATH = Path(__file__).resolve().parent.parent / "config" / "site_content.yaml"

with open(PATH, "r", encoding="utf-8") as fh:
    SITE = yaml.safe_load(fh)


def pick(d: dict, key: str, default: str = "") -> str:
    """
    Return d[key_hi] in Hindi mode when it exists, else d[key].

    Keeps every page free of `if is_hi()` branching around content.
    """
    if is_hi():
        v = d.get(f"{key}_hi")
        if v:
            return str(v).strip()
    return str(d.get(key, default)).strip()
