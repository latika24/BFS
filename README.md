# GigSure — usage-based insurance for India's gig workers

A working prototype, not a slide deck. Three products share one live state and
one rating engine, in the order a real business meets its customer:

* **GigSure.com** — the commercial site. What we sell, why it is different from
  the cover a platform gives a rider, what it costs by the hour, what happens
  when you claim, and a sign-up that issues a real policy.
* **Rider app** — what a gig worker sees once they are covered: cover live right
  now, their policy, their riding score, and raising a claim.
* **Insurer console** — what the company sees: the in-force book, the rating
  engine, the claims queue, accumulation risk, solvency and capital.

They are wired to the same store, so **registering on the website or raising a
claim in the rider app appears immediately in the insurer console.** That is the
point of the demo.

Navigation lives in the header, not a sidebar, because the first screen a
visitor sees has to read as a website rather than a dashboard.

## Run it

```bash
cd gig-insurance-dashboard/Code
pip install -r requirements.txt
streamlit run app.py
```

Python 3.9 or newer, Streamlit 1.50 or newer — 1.50 is the last release that
supports Python 3.9, and it is the version this is tested against. The header
navigation uses `st.navigation(position="top")`, which 1.50 has. Opens at
http://localhost:8501.

If you are on Python 3.9 and `pip` refuses `streamlit`, that is the cause: every
release from 1.51 onward requires Python 3.10.

## The demo worth showing

1. **GigSure.com → Home.** Move "hours you ride a month" to 60. All three plans
   reprice live, and the comparison against a flat annual policy flips from
   "you save" to "you pay more" as you drag past ~150 hours. That crossover is
   the whole argument for usage pricing, and it is drawn by the rating engine,
   not asserted.
2. **Switch the language to हिन्दी** in the top right. The whole commercial
   layer is bilingual — the plan commits to vernacular distribution, so the site
   has to be able to do it.
3. **GigSure.com → Get covered.** Complete the three steps. A real policy is
   issued into the store.
4. **Rider app → My cover.** The policy you just bought from the website is
   there, with benefit amounts sized to the earnings you entered.
5. **Rider app → Claims.** Raise "Hospital admission" and watch it settle in
   under a minute. Then raise one with *cover was live* switched off, and watch
   the anti-selection control decline it with a reason.
6. **Insurer console → Portfolio / Claims desk.** The policy and the claim are
   both in the book. Settle or decline it and the rider's view updates.

## Screens

**GigSure.com**

| Page | What it does |
|---|---|
| Home | The proposition in four seconds, live price calculator, the four failures, both products, claims promise, testimonials |
| Rider Shield | Cover on the worker — benefit amounts recalculated live from earnings, and the fine print stated up front |
| Ride Shield | Cover on the bike, the order and the phone; leads with the commercial-use exclusion in private motor policies |
| Pricing | Full calculator with conditions, the crossover against flat pricing, the governance band, and every rating factor published |
| Claims | The settlement promise, the published monthly claims record, and every reason we declined a claim |
| Why GigSure | The four structural failures, the owner-versus-protects map, and a side-by-side against platform cover and PMSBY |
| Trust | Compliance register, data rights under the DPDP Act, solvency, and who built this |
| Refer a rider | ₹100 each side, a referral calculator, and the channel economics behind it |
| Get covered | Three questions, three consents — issues a live policy into the store |

**Rider app**

| Screen | What it does |
|---|---|
| Home | Live cover status, hourly rate and why it is what it is, today's spend, benefits at a glance |
| My cover | Policy card, certificate, full benefit schedule sized to observed earnings, premium ledger |
| Buy cover | Plan catalogue, premium calculator on your own hours, add-ons, KYC and UPI mandate checkout |
| Claims | Raise a claim in one tap, live status tracker, full history |
| My riding | Safety score, what is costing points, a what-if that reprices you live, exposure by hour, consent control |

**Insurer console**

| Screen | What it does |
|---|---|
| Portfolio | In-force book, GWP run-rate, mix by segment/city/platform, exposure distribution, recently issued |
| Underwriting | Quote-and-bind tool, the full filed rating basis, portfolio pricing monitor against the governance band |
| Claims desk | Live queue with telematics evidence, settle/decline, SLA and fraud controls |
| Risk & exposure | Concurrent riders by hour, accumulation, loss experience by cohort, flat-premium stress test |
| Finance & solvency | Years 1–7 P&L, solvency against the throttle, unit economics, capital plan, scenarios |

## Changing the numbers

Two configuration files, and nothing is hard-coded in a page.

* `config/rating_factors.yaml` — everything the **risk model** uses: multipliers,
  the governance band, sum insured formulas, the benefit schedule, market
  segments, the year 1–7 trajectory, solvency and funding rounds.
* `config/site_content.yaml` — everything the **website claims**: the published
  claims report and its rejection reasons, the settlement promise, rider
  testimonials, referral terms, channel economics, the compliance register, the
  four failures and the FAQs. Every text field has an optional `_hi` twin.

Demo state (the rider, their policies, claims and ledger) is seeded in
`engine/store.py`. "Reset demo" sits in the top bar of every app and console
screen.

## A note on light and dark

The whole platform is pinned to a light ground by `FORCE_LIGHT` in `shared.py`,
injected from `app.py` on every rerun, and every Plotly figure goes through
`shared.light()`.

This is deliberate rather than lazy. Streamlit renders light by default, but a
viewer can switch the app to dark from its own **Settings → Appearance** menu,
and that choice is invisible from Python: `st.context.theme` reports what the
*browser* asked for, and a `prefers-color-scheme` query reports what the
*operating system* asked for. Either can disagree with what Streamlit actually
painted — which is how the headings ended up dark-on-dark and invisible. Since
the design is a light one, and every consumer insurance site is, pinning the
surface is the only answer that cannot be wrong.

`st.plotly_chart(theme=None)` is documented as handing styling back to Plotly,
but Streamlit still writes its own `paper_bgcolor` into the figure layout, so
`shared.light()` sets the background and font colour explicitly. Values already
set are not overwritten, which is what makes it stick.

## Artwork

Every illustration is hand-built SVG in `web/art.py` — the rider on a scooter,
the platform web, the phone mockup showing the live risk score, the hour-by-hour
day strip, and the two product banners. Nothing is a bitmap, so it stays sharp
and recolours from the palette.

Two implementation notes, both learned the hard way:

* Streamlit's HTML sanitiser strips `<svg>` elements, so every drawing is
  encoded as a base64 data-URI `<img>`. That survives sanitisation, but it also
  means an illustration cannot load a webfont — hence the system font stack
  inside the SVGs.
* XML forbids `--` inside a comment, and an SVG in an `<img>` is parsed as
  strict XML. `_img()` therefore strips comments before encoding, so the
  `<!-- ---- section ---- -->` rules in the source cannot silently break a
  drawing.

**To use a photograph in the hero instead of the illustration,** drop a file at
`assets/hero.jpg` (or `.png`/`.webp`). `art.hero_visual()` picks it up
automatically and falls back to the drawing when it is not there.

Platform names on the site are set as type in each brand's colour rather than
copied logo files — recognisable, and it keeps someone else's trademarked
artwork out of an academic prototype.

## Calibration

| Figure | Plan | Engine |
|---|---|---|
| GigSure Plus base rate | ₹2.50/hr (§3.3) | ₹2.50 |
| Price band under the governance cap | ₹1.50–₹5.50 (§3.3) | ₹1.50–₹5.51 |
| Full-time rider, monthly premium | ₹520 | ₹520 |
| Book-average premium per worker | ₹5,400/yr (§4) | ₹5,400 |
| Expected claim cost per rider-year | ₹3,148 | ₹3,148 |
| Year 1/3/5/7 combined ratio | 190/118/104/95% (§4.1) | 190/118/104/95% |
| Underwriting break-even | Year 7 (§4.1) | Year 7 |

The flat-premium benchmark used on the website and in the rider app is the tier
price times the reference rider's hours (8 × 26 × 12), not the ₹5,400 book
average — a flat annual policy has to be priced for a full-time rider, and
comparing against our own blended average would flatter us.

## Data

The 5,000-rider book is synthetic, generated by `engine/data_gen.py` with a
fixed seed — there is no public gig-worker telematics dataset. Distributions
match the plan. Nothing is fitted to real loss experience, and the published
claims report is a modelled steady state rather than live experience. Both
statements are made on the Trust page rather than buried here.

## Structure

```
app.py                      Router — st.navigation(position="top"), three sections
shared.py                   App/console design system, formatting, cached data
.streamlit/config.toml      Streamlit theme, so its chrome matches the site
assets/                     Logo and icon
config/
  rating_factors.yaml       Every number the risk model uses
  site_content.yaml         Every number and claim the website makes
engine/
  store.py                  Live state: riders, policies, claims, ledger
  pricing.py                Premium function and governance band
  exposure.py               Effective Exposure Unit
  safety_score.py           Rider Safety Score
  sum_insured.py            Benefit formulas
  portfolio.py              Book P&L, solvency, capital
  data_gen.py               Synthetic book
web/                        The commercial site
  theme.py                  Site design system — components render via st.html
  art.py                    Illustrations, line icons, phone mockup, platform web
  chrome.py                 Utility bar, CTA row, footer, route constants
  i18n.py                   Language switch; copy sits next to its layout
  content.py                Loads site_content.yaml, resolves _hi fields
  quote.py                  Public quoting helper — same engine as the console
  home.py … register.py     Nine pages
views/                      Five rider screens, five insurer screens
```

`pages/` is a leftover from an earlier version. Streamlit ignores it entirely
once `st.navigation` has been called, so it is inert — but it can be deleted.
