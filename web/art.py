"""
Illustrations, icons and device mockups for the commercial site.

Everything here is hand-built SVG rather than bitmap assets, for three reasons.
It stays sharp on any screen, it recolours itself from the brand palette, and —
the practical one — the numbers inside the illustrations are interpolated from
the same rating engine that prices the book, so a screenshot of the app on the
website cannot drift from the app.

A gig worker is the subject of every drawing. Not a car, not an office, not an
abstract shield: a rider, a two-wheeler, a delivery box and a phone.

If you would rather use a photograph in the hero, drop one at
`assets/hero.jpg` — `hero_visual()` picks it up automatically and falls back to
the illustration when it is not there.
"""
from __future__ import annotations

from pathlib import Path

from . import theme as T

ASSETS = Path(__file__).resolve().parent.parent / "assets"


def _img(svg: str, style: str = "width:100%;display:block", alt: str = "") -> str:
    """
    Wrap an SVG document as a data-URI <img>.

    Streamlit sanitises the HTML passed to `st.html` and strips <svg> elements
    outright, so inline vector markup silently disappears. An <img> whose src is
    a base64 data URI survives sanitisation intact and renders identically. The
    one trade-off is that an SVG inside an <img> cannot fetch a webfont, which
    is why the illustrations above use a system font stack.

    Comments are stripped before encoding. An SVG in an <img> is parsed as
    strict XML, and XML forbids a double hyphen inside a comment — so the
    `<!-- ---- section ---- -->` rules that make the source readable would
    otherwise silently break the whole drawing.
    """
    import base64
    import re
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    b64 = base64.b64encode(svg.strip().encode("utf-8")).decode("ascii")
    return (f"<img src='data:image/svg+xml;base64,{b64}' alt='{alt}' "
            f"style='{style}'/>")

BRAND = T.BRAND
DEEP = T.BRAND_DEEP
MINT = T.MINT
ACCENT = T.ACCENT
SIGNAL = T.SIGNAL


# --------------------------------------------------------------------- icons
# A single stroked line-icon set. Emoji were the previous approach; they render
# as empty boxes on the Linux image Streamlit Community Cloud uses, and they
# cannot take the brand colour.
_ICONS = {
    "shield": "M12 3l7 2.6v5.6c0 4.2-2.9 7.3-7 8.8-4.1-1.5-7-4.6-7-8.8V5.6L12 3z",
    "scooter": "M5 17a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zm14 0a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zM7.5 14.5h9M14 6h3l2 6M6 9h4l3 5.5",
    "wallet": "M3 8a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8zm13 4.5h3M3 8l11-3",
    "clock": "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 7v5l3 2",
    "bolt": "M13 2L4 14h6l-1 8 9-12h-6l1-8z",
    "heart": "M12 20s-7-4.4-7-9.3A3.9 3.9 0 0 1 12 8a3.9 3.9 0 0 1 7 2.7C19 15.6 12 20 12 20z",
    "hospital": "M4 21V8l8-5 8 5v13M9 21v-6h6v6M12 9v4M10 11h4",
    "bone": "M7 17l10-10M6.5 14a2.2 2.2 0 1 0 0 4.4 2.2 2.2 0 0 0 4.4 0M17.5 10a2.2 2.2 0 1 0 0-4.4 2.2 2.2 0 0 0-4.4 0",
    "ambulance": "M3 16V9h11v7H3zm11-4h3.5l2.5 3v1H14M6 19a1.6 1.6 0 1 0 0-3.2A1.6 1.6 0 0 0 6 19zm11 0a1.6 1.6 0 1 0 0-3.2 1.6 1.6 0 0 0 0 3.2zM7 11h3M8.5 9.5v3",
    "scales": "M12 4v16M7 20h10M6 8h12M6 8l-3 6h6L6 8zm12 0l-3 6h6l-3-6z",
    "phone": "M8 3h8a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1zm2.5 15h3",
    "box": "M3 8l9-4 9 4-9 4-9-4zm0 0v8l9 4 9-4V8",
    "battery": "M3 9h13v6H3V9zm16 2v2M6 12h4",
    "gauge": "M12 20a8 8 0 1 1 8-8M12 12l5-3",
    "chart": "M4 20V10M10 20V4M16 20v-7M22 20H2",
    "people": "M9 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm-6 9a6 6 0 0 1 12 0M17 11a3 3 0 1 0 0-6M16 20h5a5 5 0 0 0-3-4.6",
    "lock": "M6 11h12v9H6v-9zm3 0V8a3 3 0 0 1 6 0v3",
    "globe": "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM3 12h18M12 3c2.5 2.6 2.5 15 0 18-2.5-3-2.5-15.4 0-18z",
    "rupee": "M7 5h10M7 9h10M16 5c0 3-2.2 4-5 4H7l7 10",
    "doc": "M7 3h7l4 4v14H7V3zm7 0v4h4",
    "check": "M4 12.5l5 5L20 6.5",
    "sun": "M12 17a5 5 0 1 0 0-10 5 5 0 0 0 0 10zM12 2v2m0 16v2M2 12h2m16 0h2M4.9 4.9l1.5 1.5m11.2 11.2l1.5 1.5M19.1 4.9l-1.5 1.5M6.4 17.6l-1.5 1.5",
    "rain": "M6 13a4 4 0 0 1 .8-7.9 5.5 5.5 0 0 1 10.4 1.8A3.6 3.6 0 0 1 17 13H6zm2 3l-1 3m5-3l-1 3m5-3l-1 3",
}


def icon(name: str, colour: str = BRAND, size: int = 22, stroke: float = 1.7) -> str:
    """One inline SVG icon, coloured from the palette."""
    d = _ICONS.get(name, _ICONS["check"])
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{size}' "
           f"height='{size}' viewBox='0 0 24 24' fill='none' stroke='{colour}' "
           f"stroke-width='{stroke}' stroke-linecap='round' "
           f"stroke-linejoin='round'><path d='{d}'/></svg>")
    return _img(svg, f"width:{size}px;height:{size}px;display:block")


# ------------------------------------------------------- platform lockups
# App-icon lockups: a rounded tile in the platform's own colour carrying a
# simple original glyph, then the platform name.
#
# The glyphs are drawn here rather than copied from each company's brand
# assets. Their real logos are registered trademarks and this is an academic
# prototype with no commercial relationship to any of them — using simple
# original marks in their colours reads the same at this size and keeps
# somebody else's artwork out of the repository.
PLATFORMS = [
    ("Swiggy",    "#FC8019", "M8 22 Q17 6 25 14 Q17 24 24 30"),
    ("Zomato",    "#E23744", "M10 10h18l-18 20h18"),
    ("Zepto",     "#7B2FF7", "M11 9h16l-9 11h8L13 31l3-11h-7z"),
    ("Blinkit",   "#E0B321", "M19 8l-8 13h6l-2 11 10-14h-6z"),
    ("Flipkart",  "#2874F0", "M11 14h18v16H11zM15 14a4 4 0 0 1 8 0"),
    ("Amazon",    "#FF9900", "M9 24q10 7 21 0M27 22l3 4-5 1"),
    ("Rapido",    "#D8A400", "M12 26a4 4 0 1 0 0-8 4 4 0 0 0 0 8m14 0a4 4 0 1 0 0-8 4 4 0 0 0 0 8M15 22h9M22 12h4l3 8"),
    ("BigBasket", "#6FA31C", "M9 16h22l-3 14H12zM15 16l3-6M25 16l-3-6"),
    ("Uber",      "#101010", "M12 12v9a7 7 0 0 0 14 0v-9"),
    ("Dunzo",     "#00A874", "M9 20l22-9-8 20-4-8z"),
]


def brand_mark(name: str, colour: str, glyph: str, size: int = 30) -> str:
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{size}' "
           f"height='{size}' viewBox='0 0 40 40'>"
           f"<rect width='40' height='40' rx='10' fill='{colour}'/>"
           f"<path d='{glyph}' fill='none' stroke='#ffffff' stroke-width='3.4' "
           f"stroke-linecap='round' stroke-linejoin='round'/></svg>")
    return _img(svg, f"width:{size}px;height:{size}px;display:block", name)


def platform_lockups(items=None) -> str:
    """The row of apps a rider earns from — icon plus name, like a phone home screen."""
    out = ""
    for name, colour, glyph in (items or PLATFORMS):
        out += (f"<span class='gs-brand'>{brand_mark(name, colour, glyph)}"
                f"<span class='nm'>{name}</span></span>")
    return f"<div class='gs gs-brands'>{out}</div>"


# Kept so any page still calling the old name keeps working.
platform_chips = platform_lockups


# ------------------------------------------------------------------- hero art
def _rider_svg() -> str:
    """
    A delivery rider on a scooter, mid-shift, with cover switched on.

    Drawn as a scooter rather than a bicycle on purpose: step-through frame,
    front leg shield, floorboard, top box on a rear rack. That silhouette is
    what our customer rides and what they recognise themselves in.
    """
    return f"""
<svg viewBox="0 0 560 420" xmlns="http://www.w3.org/2000/svg" width="100%"
     role="img" aria-label="A delivery rider on a scooter, covered">
  <defs>
    <linearGradient id="halo" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ffffff" stop-opacity=".16"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="topbox" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{ACCENT}"/>
      <stop offset="100%" stop-color="#D94E1F"/>
    </linearGradient>
  </defs>

  <circle cx="404" cy="120" r="104" fill="url(#halo)"/>
  <circle cx="404" cy="120" r="58" fill="{MINT}" opacity=".20"/>

  <!-- skyline -->
  <g opacity=".18" fill="#ffffff">
    <rect x="34"  y="206" width="40" height="92" rx="4"/>
    <rect x="82"  y="176" width="32" height="122" rx="4"/>
    <rect x="122" y="222" width="28" height="76" rx="4"/>
    <rect x="392" y="192" width="36" height="106" rx="4"/>
    <rect x="436" y="216" width="28" height="82" rx="4"/>
    <rect x="472" y="184" width="40" height="114" rx="4"/>
  </g>

  <!-- road -->
  <rect x="0" y="352" width="560" height="68" fill="#ffffff" opacity=".07"/>
  <g stroke="#ffffff" stroke-opacity=".45" stroke-width="5" stroke-linecap="round">
    <line x1="24"  y1="386" x2="80"  y2="386"/>
    <line x1="112" y1="386" x2="168" y2="386"/>
    <line x1="392" y1="386" x2="448" y2="386"/>
    <line x1="478" y1="386" x2="534" y2="386"/>
  </g>

  <!-- speed -->
  <g stroke="{MINT}" stroke-width="5" stroke-linecap="round" opacity=".7">
    <line x1="30" y1="262" x2="96" y2="262"/>
    <line x1="14" y1="292" x2="66" y2="292"/>
    <line x1="44" y1="320" x2="86" y2="320"/>
  </g>

  <!-- ---------------------------------------------------------- scooter -->
  <!-- wheels -->
  <circle cx="176" cy="322" r="40" fill="#0A211E"/>
  <circle cx="176" cy="322" r="40" fill="none" stroke="#ffffff"
          stroke-opacity=".5" stroke-width="5"/>
  <circle cx="176" cy="322" r="13" fill="#E8F1EF"/>
  <circle cx="398" cy="322" r="40" fill="#0A211E"/>
  <circle cx="398" cy="322" r="40" fill="none" stroke="#ffffff"
          stroke-opacity=".5" stroke-width="5"/>
  <circle cx="398" cy="322" r="13" fill="#E8F1EF"/>

  <!-- rear cowl and seat -->
  <path d="M150 286 q-6 -46 46 -50 h58 l6 50z" fill="{MINT}"/>
  <rect x="176" y="228" width="104" height="24" rx="12" fill="#0A211E"/>
  <rect x="176" y="228" width="104" height="24" rx="12" fill="none"
        stroke="#ffffff" stroke-opacity=".4" stroke-width="2"/>

  <!-- floorboard, step-through -->
  <path d="M258 286 h74 v-14 h-74z" fill="#ffffff"/>
  <path d="M262 272 q10 -34 44 -40" fill="none" stroke="#ffffff"
        stroke-width="7" stroke-linecap="round"/>

  <!-- front leg shield -->
  <path d="M330 292 q4 -70 40 -96 l26 -16 q10 46 4 78 q-4 22 -22 34z"
        fill="#ffffff"/>
  <path d="M356 214 q18 -12 34 -14" fill="none" stroke="{MINT}"
        stroke-width="6" stroke-linecap="round"/>

  <!-- front fork + mudguard -->
  <path d="M392 200 L400 296" stroke="#ffffff" stroke-width="9"
        stroke-linecap="round"/>
  <path d="M370 292 q30 -22 58 0" fill="none" stroke="#ffffff"
        stroke-width="7" stroke-linecap="round"/>

  <!-- handlebar + headlight -->
  <path d="M392 200 L406 176 M382 172 h50" fill="none" stroke="#ffffff"
        stroke-width="9" stroke-linecap="round"/>
  <circle cx="418" cy="212" r="12" fill="{SIGNAL}"/>
  <circle cx="418" cy="212" r="20" fill="{SIGNAL}" opacity=".22"/>

  <!-- rear rack + top box -->
  <path d="M156 240 h44" stroke="#ffffff" stroke-width="7" stroke-linecap="round"/>
  <rect x="124" y="166" width="92" height="74" rx="12" fill="url(#topbox)"/>
  <rect x="124" y="166" width="92" height="74" rx="12" fill="none"
        stroke="#ffffff" stroke-opacity=".35" stroke-width="3"/>
  <path d="M170 186 l19 7v14c0 11-7.4 18.6-19 23-11.6-4.4-19-12-19-23v-14l19-7z"
        fill="#ffffff"/>
  <path d="M162 206 l6 6 12-13" fill="none" stroke="{ACCENT}" stroke-width="3.4"
        stroke-linecap="round" stroke-linejoin="round"/>

  <!-- ------------------------------------------------------------ rider -->
  <!-- rear leg -->
  <path d="M262 250 L286 282 L292 300" fill="none" stroke="#123A35"
        stroke-width="17" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- torso, leaning into the ride -->
  <path d="M252 246 q-14 -44 18 -66 l30 -18 q22 26 6 52 q-16 26 -54 32z"
        fill="#ffffff"/>
  <!-- front leg on the floorboard -->
  <path d="M276 244 L302 268 L292 284" fill="none" stroke="#0A211E"
        stroke-width="17" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- arm reaching the bar -->
  <path d="M296 178 L392 190" fill="none" stroke="#ffffff" stroke-width="16"
        stroke-linecap="round"/>
  <circle cx="392" cy="190" r="10" fill="#F3D6BE"/>
  <!-- neck + head -->
  <path d="M292 168 l10 14" stroke="#F3D6BE" stroke-width="13"
        stroke-linecap="round"/>
  <circle cx="290" cy="146" r="27" fill="#F3D6BE"/>
  <!-- helmet -->
  <path d="M263 146 a27 27 0 0 1 54 0 v3 h-54z" fill="{ACCENT}"/>
  <path d="M317 148 h9 a7 7 0 0 1 0 14 h-7" fill="{ACCENT}"/>
  <path d="M263 149 h54" stroke="#ffffff" stroke-opacity=".65" stroke-width="4"/>
  <path d="M317 132 q14 2 18 12" fill="none" stroke="{ACCENT}" stroke-width="6"
        stroke-linecap="round"/>

  <!-- ------------------------------------------------------------ labels -->
  <g>
    <rect x="386" y="60" width="164" height="46" rx="23" fill="#ffffff"/>
    <circle cx="411" cy="83" r="7" fill="#1F8A5B"/>
    <circle cx="411" cy="83" r="12" fill="#1F8A5B" opacity=".2"/>
    <text x="428" y="89" font-family="Helvetica Neue, Arial, sans-serif"
          font-size="16" font-weight="bold" fill="{DEEP}">Cover is live</text>
  </g>
  <g>
    <rect x="34" y="96" width="152" height="64" rx="16" fill="{DEEP}"
          stroke="#ffffff" stroke-opacity=".26" stroke-width="2"/>
    <text x="52" y="128" font-family="Helvetica Neue, Arial, sans-serif"
          font-size="26" font-weight="bold" fill="#ffffff">&#8377;2.50</text>
    <text x="122" y="128" font-family="Helvetica Neue, Arial, sans-serif"
          font-size="13" font-weight="bold" fill="{MINT}">/hour</text>
    <text x="52" y="147" font-family="Helvetica Neue, Arial, sans-serif"
          font-size="11.5" fill="#ffffff" opacity=".72">only while you ride</text>
  </g>
</svg>"""


def hero_visual() -> str:
    """The hero image — a photograph if one has been supplied, else the rider."""
    for name in ("hero.jpg", "hero.jpeg", "hero.png", "hero.webp"):
        p = ASSETS / name
        if p.exists():
            import base64
            b64 = base64.b64encode(p.read_bytes()).decode()
            mime = "jpeg" if name.endswith(("jpg", "jpeg")) else name.rsplit(".", 1)[1]
            return (f"<img src='data:image/{mime};base64,{b64}' alt='' "
                    f"style='width:100%;height:100%;object-fit:cover;"
                    f"border-radius:20px;display:block'/>")
    return _img(_rider_svg(), "width:100%;display:block",
                "A delivery rider on a two-wheeler, covered")


# -------------------------------------------------- one policy, every app
def platform_web() -> str:
    """
    The core proposition as a picture: one policy at the centre, every app a
    rider earns from wired into it, and the cover live in the gaps between.

    Chip positions are computed on an ellipse rather than hand-placed, so no
    label can drift outside the viewBox and get clipped at the edge.
    """
    import math

    apps = [
        ("Swiggy", "#FC8019"), ("Zomato", "#E23744"), ("Zepto", "#7B2FF7"),
        ("Blinkit", "#E0B321"), ("Rapido", "#C99A05"), ("Amazon", "#FF9900"),
        ("Flipkart", "#2874F0"),
    ]
    cx, cy, rx, ry = 300.0, 210.0, 205.0, 158.0
    cw, ch = 108.0, 38.0

    spokes, chips = "", ""
    for i, (name, colour) in enumerate(apps):
        ang = -math.pi / 2 + i * (2 * math.pi / len(apps))
        px, py = cx + rx * math.cos(ang), cy + ry * math.sin(ang)
        x, y = px - cw / 2, py - ch / 2
        spokes += (f"<line x1='{cx}' y1='{cy}' x2='{px:.1f}' y2='{py:.1f}' "
                   f"stroke='{colour}' stroke-opacity='.45' stroke-width='2.4' "
                   f"stroke-dasharray='5 5'/>")
        chips += (f"<g><rect x='{x:.1f}' y='{y:.1f}' width='{cw}' height='{ch}' "
                  f"rx='{ch / 2}' fill='#ffffff' stroke='{colour}' "
                  f"stroke-opacity='.4' stroke-width='2'/>"
                  f"<text x='{px:.1f}' y='{py + 5.5:.1f}' text-anchor='middle' "
                  f"font-family='Helvetica Neue, Arial, sans-serif' "
                  f"font-size='15' font-weight='bold' fill='{colour}'>"
                  f"{name}</text></g>")

    return _img(f"""
<svg viewBox="0 0 600 420" xmlns="http://www.w3.org/2000/svg" width="100%">
  <defs>
    <radialGradient id="glow" cx="50%" cy="50%">
      <stop offset="0%" stop-color="{MINT}" stop-opacity=".5"/>
      <stop offset="100%" stop-color="{MINT}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="core" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{T.BRAND_MID}"/>
      <stop offset="100%" stop-color="{DEEP}"/>
    </linearGradient>
  </defs>

  <ellipse cx="{cx}" cy="{cy}" rx="185" ry="150" fill="url(#glow)"/>
  <ellipse cx="{cx}" cy="{cy}" rx="150" ry="118" fill="none" stroke="{BRAND}"
           stroke-opacity=".18" stroke-width="1.5" stroke-dasharray="3 7"/>
  {spokes}
  {chips}

  <circle cx="{cx}" cy="{cy}" r="82" fill="url(#core)"/>
  <circle cx="{cx}" cy="{cy}" r="82" fill="none" stroke="{MINT}"
          stroke-opacity=".5" stroke-width="2"/>
  <path d="M{cx} {cy - 48} l32 12v26c0 19-13.2 33.4-32 40-18.8-6.6-32-21-32-40v-26l32-12z"
        fill="{MINT}"/>
  <path d="M{cx - 13} {cy - 2} l9 9 17-18" fill="none" stroke="{DEEP}"
        stroke-width="4.4" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="{cx}" y="{cy + 58}" text-anchor="middle"
        font-family="Helvetica Neue, Arial, sans-serif" font-size="14"
        font-weight="bold" fill="#ffffff" letter-spacing="1">YOUR POLICY</text>
</svg>""", "width:100%;display:block",
        "One policy, live across every app a rider works on")


# ------------------------------------------------- phone: the risk analytics
def phone_score(score: float = 78, rate: float = 2.50, hours: float = 6.5,
                spend: float = 18, m_time: float = 1.15, m_wx: float = 1.00,
                m_city: float = 1.20) -> str:
    """
    The app screen a rider actually sees: what they are paying this hour, and
    the three things making it that. This is the usage-based risk model with
    its jargon removed — the same numbers the insurer console shows as
    multipliers, shown here as reasons.
    """
    circ = 2 * 3.14159 * 46
    filled = circ * (score / 100.0)

    def bar(y, label, mult, colour):
        w = max(6, min(150, (mult - 0.6) / 1.6 * 150))
        return (f"<text x='30' y='{y}' font-family='Helvetica Neue, Arial, sans-serif' "
                f"font-size='11.5' font-weight='700' fill='#3B4B48'>{label}</text>"
                f"<rect x='30' y='{y + 6}' width='150' height='7' rx='3.5' fill='#EEF3F2'/>"
                f"<rect x='30' y='{y + 6}' width='{w:.0f}' height='7' rx='3.5' fill='{colour}'/>"
                f"<text x='196' y='{y + 13}' font-family='Helvetica Neue, Arial, sans-serif' "
                f"font-size='11.5' font-weight='800' fill='{colour}'>×{mult:.2f}</text>")

    return _img(f"""
<svg viewBox="0 0 300 600" xmlns="http://www.w3.org/2000/svg" width="100%"
     role="img" aria-label="The GigSure app showing this hour's price and why">
  <defs>
    <linearGradient id="scr" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#F3FAF8"/>
      <stop offset="100%" stop-color="#ffffff"/>
    </linearGradient>
    <linearGradient id="hdr" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{T.BRAND_MID}"/>
      <stop offset="100%" stop-color="{DEEP}"/>
    </linearGradient>
  </defs>

  <!-- handset -->
  <rect x="6" y="6" width="288" height="588" rx="42" fill="#0B1A18"/>
  <rect x="14" y="14" width="272" height="572" rx="36" fill="url(#scr)"/>
  <rect x="112" y="22" width="76" height="9" rx="4.5" fill="#0B1A18"/>

  <!-- status -->
  <text x="34" y="52" font-family="Helvetica Neue, Arial, sans-serif" font-size="11.5"
        font-weight="700" fill="#6E807D">21:40</text>
  <g fill="#6E807D">
    <rect x="232" y="44" width="3" height="8" rx="1.5"/>
    <rect x="238" y="41" width="3" height="11" rx="1.5"/>
    <rect x="244" y="38" width="3" height="14" rx="1.5"/>
    <rect x="254" y="41" width="14" height="8" rx="2.4"/>
  </g>

  <!-- live cover header -->
  <rect x="24" y="66" width="252" height="126" rx="22" fill="url(#hdr)"/>
  <circle cx="48" cy="96" r="6" fill="{MINT}"/>
  <circle cx="48" cy="96" r="11" fill="{MINT}" opacity=".25"/>
  <text x="64" y="101" font-family="Helvetica Neue, Arial, sans-serif" font-size="13"
        font-weight="800" fill="#ffffff">You are covered</text>
  <text x="46" y="146" font-family="Helvetica Neue, Arial, sans-serif" font-size="38"
        font-weight="800" fill="#ffffff">₹{rate:.2f}</text>
  <text x="150" y="146" font-family="Helvetica Neue, Arial, sans-serif" font-size="14"
        font-weight="700" fill="{MINT}">/hour</text>
  <text x="46" y="170" font-family="Helvetica Neue, Arial, sans-serif" font-size="11.5"
        font-weight="600" fill="#ffffff" opacity=".78">
    Today ₹{spend:.0f} · {hours:.1f} hrs · Zepto then Swiggy</text>

  <!-- score ring -->
  <text x="30" y="228" font-family="Helvetica Neue, Arial, sans-serif" font-size="12.5"
        font-weight="800" fill="{T.INK}">Your riding score</text>
  <g transform="translate(84,300)">
    <circle r="46" fill="none" stroke="#E7F1F0" stroke-width="13"/>
    <circle r="46" fill="none" stroke="{BRAND}" stroke-width="13"
            stroke-linecap="round" stroke-dasharray="{filled:.0f} {circ:.0f}"
            transform="rotate(-90)"/>
    <text y="6" text-anchor="middle" font-family="Helvetica Neue, Arial, sans-serif"
          font-size="30" font-weight="800" fill="{DEEP}">{score:.0f}</text>
    <text y="24" text-anchor="middle" font-family="Helvetica Neue, Arial, sans-serif"
          font-size="10.5" font-weight="700" fill="#6E807D">out of 100</text>
  </g>
  <rect x="150" y="258" width="120" height="84" rx="16" fill="#E7F1F0"/>
  <text x="164" y="284" font-family="Helvetica Neue, Arial, sans-serif" font-size="11.5"
        font-weight="800" fill="{BRAND}">−5% next week</text>
  <text x="164" y="304" font-family="Helvetica Neue, Arial, sans-serif" font-size="10.5"
        font-weight="600" fill="#3B4B48">2 fewer harsh</text>
  <text x="164" y="318" font-family="Helvetica Neue, Arial, sans-serif" font-size="10.5"
        font-weight="600" fill="#3B4B48">brakes than last</text>
  <text x="164" y="332" font-family="Helvetica Neue, Arial, sans-serif" font-size="10.5"
        font-weight="600" fill="#3B4B48">week</text>

  <!-- why this price -->
  <text x="30" y="386" font-family="Helvetica Neue, Arial, sans-serif" font-size="12.5"
        font-weight="800" fill="{T.INK}">Why this hour costs what it does</text>
  {bar(406, "Time — 19:00 to 23:00", m_time, ACCENT)}
  {bar(444, "Weather — clear", m_wx, BRAND)}
  {bar(482, "City — Bengaluru", m_city, ACCENT)}

  <!-- cap -->
  <rect x="24" y="516" width="252" height="52" rx="16" fill="{T.ACCENT_SOFT}"/>
  <text x="42" y="540" font-family="Helvetica Neue, Arial, sans-serif" font-size="11.5"
        font-weight="800" fill="#8A3A14">Capped at ₹5.51 an hour</text>
  <text x="42" y="556" font-family="Helvetica Neue, Arial, sans-serif" font-size="10.5"
        font-weight="600" fill="#8A3A14" opacity=".85">
    whatever the weather does tonight</text>
</svg>""", "width:100%;display:block", "The GigSure app showing this hour's price and why")


# ---------------------------------------------------- a day, charged by hour
def day_strip() -> str:
    """
    Twenty-four hours of a rider's day. Only the hours actually ridden are
    charged, and each is charged at the risk of that hour — which is the whole
    product in one picture.
    """
    hours = [
        (0, 6, None), (6, 11, 0.85), (11, 13, None), (13, 16, 1.00),
        (16, 19, 1.15), (19, 21, None), (21, 24, 1.35),
    ]
    seg = ""
    x = 30.0
    span = 900.0 / 24
    for a, b, m in hours:
        w = (b - a) * span
        if m is None:
            seg += (f"<rect x='{x:.1f}' y='58' width='{w - 3:.1f}' height='44' rx='9' "
                    f"fill='#EFF3F2'/>"
                    f"<text x='{x + w / 2:.1f}' y='86' text-anchor='middle' "
                    f"font-family='Helvetica Neue, Arial, sans-serif' font-size='13' "
                    f"font-weight='800' fill='#9BA9A7'>₹0</text>")
        else:
            # Cheap hours read light, expensive hours read hot. The previous
            # scale had the safest hour as the darkest block, which said the
            # opposite of what it meant.
            colour = ("#3FB49B" if m <= 0.9 else
                      "#14796F" if m <= 1.05 else
                      "#E8823C" if m <= 1.2 else ACCENT)
            rate = 2.50 * m
            seg += (f"<rect x='{x:.1f}' y='58' width='{w - 3:.1f}' height='44' rx='9' "
                    f"fill='{colour}'/>"
                    f"<text x='{x + w / 2:.1f}' y='86' text-anchor='middle' "
                    f"font-family='Helvetica Neue, Arial, sans-serif' font-size='13' "
                    f"font-weight='800' fill='#ffffff'>₹{rate:.2f}</text>")
        x += w

    ticks = ""
    for h in range(0, 25, 4):
        tx = 30 + h * span
        ticks += (f"<text x='{tx:.1f}' y='126' text-anchor='middle' "
                  f"font-family='Helvetica Neue, Arial, sans-serif' font-size='11.5' "
                  f"font-weight='700' fill='#6E807D'>{h:02d}:00</text>")

    return _img(f"""
<svg viewBox="0 0 960 150" xmlns="http://www.w3.org/2000/svg" width="100%"
     role="img" aria-label="A rider's day, charged only for the hours ridden">
  <text x="30" y="34" font-family="Helvetica Neue, Arial, sans-serif" font-size="14"
        font-weight="800" fill="{T.INK}">One day, hour by hour</text>
  <text x="196" y="34" font-family="Helvetica Neue, Arial, sans-serif" font-size="12.5"
        font-weight="600" fill="#6E807D">
    grey hours cost you nothing · orange hours are the risky ones</text>
  {seg}
  {ticks}
</svg>""", "width:100%;display:block", "A rider's day, charged only for the hours ridden")


# -------------------------------------------------------- product headliners
def product_banner(kind: str) -> str:
    """
    The wide illustration at the top of each product card.

    Rider Shield shows the thing that is actually being insured — a calendar of
    days off the road, every one of them paid. Ride Shield shows the scooter,
    the order and the phone. Both are drawn to the same 520x170 frame so the
    two cards line up exactly.
    """
    if kind == "rider":
        # 18 of 21 days shaded: the income benefit runs after a three-day wait.
        days = "".join(
            "<rect x='%d' y='%d' width='19' height='13' rx='3.5' fill='%s'/>"
            % (14 + (i % 7) * 25, 40 + (i // 7) * 19,
               MINT if i >= 3 else "#DCE6E4")
            for i in range(21))
        return _img(f"""
<svg viewBox="0 0 520 170" xmlns="http://www.w3.org/2000/svg" width="100%">
  <rect width="520" height="170" rx="16" fill="{T.BRAND_SOFT}"/>
  <circle cx="450" cy="26" r="72" fill="{MINT}" opacity=".3"/>

  <g transform="translate(288,26)">
    <rect width="196" height="120" rx="14" fill="#ffffff"/>
    <path d="M0 14a14 14 0 0 1 14-14h168a14 14 0 0 1 14 14v12H0z" fill="{BRAND}"/>
    <text x="14" y="18" font-family="Helvetica Neue, Arial, sans-serif"
          font-size="10.5" font-weight="bold" fill="#ffffff"
          letter-spacing=".5">DAYS YOU CANNOT RIDE</text>
    {days}
    <text x="14" y="112" font-family="Helvetica Neue, Arial, sans-serif"
          font-size="10.5" font-weight="bold" fill="{BRAND}">
      paid, every one of them</text>
  </g>

  <g transform="translate(58,30)">
    <circle cx="44" cy="26" r="23" fill="#F3D6BE"/>
    <path d="M21 25a23 23 0 0 1 46 0v3H21z" fill="{DEEP}"/>
    <path d="M44 51 q29 4 31 33 v22 H13 V84 q2-29 31-33z" fill="#ffffff"/>
    <path d="M27 72 l30 9" stroke="{ACCENT}" stroke-width="9"
          stroke-linecap="round"/>
    <path d="M25 63 q23 23 37 13" fill="none" stroke="{ACCENT}"
          stroke-width="5" stroke-linecap="round"/>
  </g>

  <g transform="translate(178,86)">
    <rect width="80" height="44" rx="11" fill="{ACCENT}"/>
    <text x="40" y="29" text-anchor="middle"
          font-family="Helvetica Neue, Arial, sans-serif" font-size="16"
          font-weight="bold" fill="#ffffff">&#8377; / day</text>
  </g>
</svg>""", "width:100%;display:block", "Cover on the rider")

    return _img(f"""
<svg viewBox="0 0 520 170" xmlns="http://www.w3.org/2000/svg" width="100%">
  <rect width="520" height="170" rx="16" fill="{T.ACCENT_SOFT}"/>
  <circle cx="90" cy="150" r="80" fill="{SIGNAL}" opacity=".3"/>

  <g transform="translate(28,34)">
    <circle cx="42" cy="86" r="24" fill="#12302C"/>
    <circle cx="42" cy="86" r="8" fill="#ffffff" opacity=".85"/>
    <circle cx="164" cy="86" r="24" fill="#12302C"/>
    <circle cx="164" cy="86" r="8" fill="#ffffff" opacity=".85"/>
    <path d="M24 68 q-4 -28 28 -30 h34 l4 30z" fill="{ACCENT}"/>
    <rect x="44" y="30" width="60" height="14" rx="7" fill="#12302C"/>
    <path d="M96 68 h42 v-9 h-42z" fill="#12302C"/>
    <path d="M138 70 q2 -42 24 -58 l16 -10 q6 28 2 48 q-2 13 -13 20z"
          fill="#12302C"/>
    <path d="M172 20 L180 82" stroke="#12302C" stroke-width="7"
          stroke-linecap="round"/>
    <path d="M172 20 L182 6 M166 4 h30" fill="none" stroke="#12302C"
          stroke-width="7" stroke-linecap="round"/>
    <circle cx="190" cy="30" r="8" fill="{SIGNAL}"/>
  </g>

  <g transform="translate(236,24)" stroke="{ACCENT}" stroke-width="5"
     stroke-linecap="round">
    <line x1="0" y1="20" x2="20" y2="0"/>
    <line x1="12" y1="34" x2="38" y2="27"/>
    <line x1="2" y1="2" x2="8" y2="-16"/>
  </g>

  <g transform="translate(288,40)">
    <rect width="100" height="92" rx="12" fill="#ffffff"/>
    <path d="M50 20 L74 30 L50 40 L26 30z" fill="{ACCENT}"/>
    <path d="M26 30 v22 l24 10 v-22z" fill="{ACCENT}" opacity=".82"/>
    <path d="M74 30 v22 l-24 10 v-22z" fill="{ACCENT}" opacity=".6"/>
    <text x="50" y="82" text-anchor="middle"
          font-family="Helvetica Neue, Arial, sans-serif" font-size="10"
          font-weight="bold" fill="{DEEP}">YOUR ORDER</text>
  </g>

  <g transform="translate(404,32)">
    <rect width="76" height="108" rx="12" fill="#ffffff"/>
    <rect x="12" y="12" width="52" height="72" rx="7" fill="{T.ACCENT_SOFT}"/>
    <rect x="30" y="18" width="16" height="3" rx="1.5" fill="{ACCENT}"
          opacity=".6"/>
    <path d="M24 50 l12 12 20-24" fill="none" stroke="{ACCENT}"
          stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
    <text x="38" y="100" text-anchor="middle"
          font-family="Helvetica Neue, Arial, sans-serif" font-size="10"
          font-weight="bold" fill="{DEEP}">PHONE</text>
  </g>
</svg>""", "width:100%;display:block", "Cover on your bike, order and phone")
