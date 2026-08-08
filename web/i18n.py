"""
Language handling for the commercial site.

The plan commits to vernacular and voice-first distribution in eight languages
(§3.3), on the argument that our customer does not read English marketing. A
site that claims that and then ships English-only is not credible, so the
switch is real and the Hindi is written rather than machine-translated.

Copy lives next to the layout that uses it, via `L(english, hindi)`, rather
than in a central dictionary. With nine pages that is easier to keep honest:
you cannot add an English line and forget the Hindi, because they sit on the
same line.
"""
from __future__ import annotations

import streamlit as st

LANGS = {"en": "English", "hi": "हिन्दी"}
KEY = "gs_lang"


def lang() -> str:
    return st.session_state.get(KEY, "en")


def is_hi() -> bool:
    return lang() == "hi"


def L(en: str, hi: str | None = None) -> str:
    """Pick a string for the active language, falling back to English."""
    return hi if (is_hi() and hi) else en


def toggle(key: str = "langsel"):
    """The switch itself. Renders as a two-option segmented control."""
    current = lang()
    choice = st.segmented_control(
        "Language", options=list(LANGS.keys()),
        format_func=lambda k: LANGS[k],
        default=current, key=key, label_visibility="collapsed")
    if choice and choice != current:
        st.session_state[KEY] = choice
        st.rerun()
