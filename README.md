<<<<<<< HEAD
# Usage-Based Insurance for India's Gig Workers — Dashboard

Companion to the business plan. Implements the pricing engine, sum insured
formulas and portfolio model described in Appendix A.
=======
# Suraksha — Usage-Based Insurance for India's Gig Workers

Proof-of-concept product site and pricing engine, built as a companion to the
business plan. Every number it produces reconciles to a published figure in the
report.
>>>>>>> 03dbdc9 (Initial commit)

## Run it

```bash
cd gig-insurance-dashboard
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`. Stop it with Ctrl+C.

<<<<<<< HEAD
If `pip` isn't found, try `pip3`. If Streamlit says the port is busy, run
`streamlit run app.py --server.port 8502`.

**Python 3.9 or newer.** Check with `python3 --version`. The code uses
`from __future__ import annotations` in every module so it runs on 3.9 as well
as newer versions — if you edit a file and add a type hint, keep that import at
the top or 3.9 will raise `TypeError: unsupported operand type(s) for |`.

## The four pages

| Page | What it does | Plan reference |
|---|---|---|
| **Overview** | Headline figures and the calibration check | — |
| **1 · Rider Quote** | Price one rider; move exposure controls and watch the premium move. Full derivation shown as a waterfall | §5.1, §5.3 |
| **2 · Sum Insured** | Cover calculated from observed earnings; fixed-benefit vs indemnity schedule with the moral-hazard control on each | §5.4, §4.2, §4.3 |
| **3 · Portfolio Simulator** | Years 1–7: GWP, loss ratio, expense ratio, combined ratio, solvency. Includes the §6.7 stress cases | §6.2, §6.4, §6.6, §6.7 |
| **4 · Risk Explorer** | Synthetic book of 5,000 riders: exposure distribution, anti-selection under flat pricing, risk heatmap | §3.2, §5.5, §12.1 |

## Changing the numbers

**Everything lives in `config/rating_factors.yaml`.** No figure is hard-coded.
When the plan changes, edit that one file and the whole dashboard follows —
multipliers, caps, sum insured parameters, the benefit schedule, the year 1–7
trajectory, solvency assumptions and the funding rounds.
=======
If `pip` isn't found, try `pip3`. If the port is busy, add
`--server.port 8502`.

**Python 3.9 or newer.** Check with `python3 --version`. Every module starts
with `from __future__ import annotations` so the code runs on 3.9 as well as
newer versions — keep that import at the top if you add type hints, or 3.9 will
raise `TypeError: unsupported operand type(s) for |`.

## The pages

| Page | What it does | Plan reference |
|---|---|---|
| **Home** | Product framing, the four gaps, headline numbers, calibration check | §1.1 |
| **1 · Rider App** | The phone view a worker actually sees: cover live now, hours ridden, what it has cost, safety score and what would lower it | §1.2, §1.3, §3.2 |
| **2 · Pricing Engine** | Price any rider under any conditions. Governance band gauge, full waterfall derivation, and the comparison against a flat premium | §1.2, §3.3 |
| **3 · Cover & Benefits** | Sums insured derived from observed earnings, both covers, and the fixed-benefit vs indemnity schedule with the control on each | §1.2 |
| **4 · Claims Journey** | Run a claim end to end. Six incident types, live adjudication against the telematics trace, and the settlement mix | §1.1, §3.2 |
| **5 · Market & Strategy** | Segment sizing across the 1.2 crore workforce, the competitive quadrant, channel economics and the capital plan | §2.1, §2.2, §3.1, §3.3, §5 |
| **6 · Portfolio Simulator** | The book years 1–7: premium, loss ratio, expense ratio, solvency, with the stress cases | §4, §4.1, §2.1 |
| **7 · Risk Explorer** | Synthetic book of 5,000 riders: exposure distribution, anti-selection under flat pricing, risk heatmap | §3.3, §1.3 |

## Changing the numbers

**Everything lives in `config/rating_factors.yaml`.** No figure is hard-coded —
multipliers, the governance band, sum insured parameters, the benefit schedule
and its settlement basis, market segments, the year 1–7 trajectory, solvency
assumptions and the funding rounds.
>>>>>>> 03dbdc9 (Initial commit)

Refresh the browser after editing. If a change doesn't appear, clear the cache
from the ⋮ menu top-right → *Clear cache*.

## Calibration

<<<<<<< HEAD
The engine is calibrated to one reference rider (defined in the config) so its
output can be checked rather than taken on trust:

| Figure | Plan | Engine |
|---|---|---|
| Suraksha Plus, per active hour | ₹2.50 (§4.4) | ₹2.50 |
| Full-time rider, monthly premium | ₹520 (§4.4) | ₹520 |
| Book-average GWP per worker per year | ₹5,400 (§6.2) | ₹5,400 |
| Expected claim cost per rider-year | ₹3,148 (§6.1) | ₹3,148 |
| Year 7 combined ratio | 95% (§6.4) | 95% |
| Underwriting break-even | Year 7 (§6.4) | Year 7 |

**One reconciliation worth knowing.** §4.4 prices Suraksha Plus at ₹2.50 per
active hour with a full-time rider at ~208 hours a month — that is ₹6,240 a
year. §6.2 uses ₹5,400 per active worker. Both hold: ₹5,400 is the blended
average across a book including part-time and occasional riders, implying about
180 active hours a month. The Rider Quote page prices an individual at the tier
rate; the Portfolio page uses the book average. The Overview page states this.
=======
Checked against the report on every run, and shown on the Home page:

| Figure | Plan | Engine |
|---|---|---|
| Suraksha Plus, base rate per active hour | ₹2.50 (§3.3) | ₹2.50 |
| Price band under the governance cap | ₹1.50–₹5.50 (§3.3) | ₹1.50–₹5.51 |
| Full-time rider, monthly premium | ₹520 (§3.3) | ₹520 |
| Book-average premium per worker per year | ₹5,400 (§4) | ₹5,400 |
| Expected claim cost per rider-year | ₹3,148 | ₹3,148 |
| Year 1 / 3 / 5 / 7 combined ratio | 190 / 118 / 104 / 95% (§4.1) | 190 / 118 / 104 / 95% |
| Year 7 gross written premium | ₹648 cr (§4.1) | ₹648 cr |
| Underwriting break-even | Year 7 (§4.1) | Year 7 |
| Total equity raised | ₹500 cr (§5 table) | ₹500 cr |

### Two things the model surfaces rather than hides

**The governance band applies to the total multiplier.** §3.3 says the band
covers "time of day, weather, traffic, city and behaviour score" and produces a
Plus price of ₹1.50–₹5.50 an hour. So the 0.6–2.2× cap is applied to the
exposure and rating factors *combined*, not to the rating factors alone. Without
that, a rider at 11pm in heavy metro rain would price above ₹12 an hour, far
outside the band the plan commits to.

**A discrepancy in the report worth fixing.** The narrative in §2.1 and §5 says
₹300 crore is raised pre-launch; the investor table in §5 says ₹250 crore. The
model uses the table figure — the tighter of the two — and flags the difference
on the Home page and the Market & Strategy page.

Separately, §3.3 prices Plus at ₹2.50 an hour with a full-time rider at ~208
hours a month, which is ₹6,240 a year, while §4 uses ₹5,400 per active worker.
Both hold: ₹5,400 is the blended average across a book including part-time and
Shift Pass riders, implying about 180 active hours a month.
>>>>>>> 03dbdc9 (Initial commit)

## Data

Synthetic, generated by `engine/data_gen.py` with a fixed seed. There is no
public gig-worker telematics dataset, and for a demonstration synthetic is the
<<<<<<< HEAD
honest choice. Distributions match the plan: ~25% of workers ride more than
eight hours a day, ~33% work purely in free time, claim frequencies come from
the §6.1 burning cost table. Download the generated CSVs from the bottom of the
Risk Explorer page.

Nothing here is fitted to real loss experience. These are prior estimates for a
pilot, to be replaced by a fitted GLM once roughly 12 months and 2,000 claims of
real data exist (§5.6).
=======
honest choice. Distributions match the plan — about a quarter of workers ride
more than eight hours a day, about a third work purely in free time — and claim
frequencies come from the burning cost table. Download the generated CSVs from
the bottom of the Risk Explorer page.

Nothing here is fitted to real loss experience. These are prior estimates for a
pilot, to be replaced by a fitted GLM once roughly 12 months and 2,000 claims of
real data exist.
>>>>>>> 03dbdc9 (Initial commit)

## Structure

```
<<<<<<< HEAD
app.py                      Overview page and entry point
shared.py                   Formatting, cached data loading, page furniture
config/rating_factors.yaml  Every number the model uses
engine/
  config.py                 Config loader and band lookups
  exposure.py               Effective Exposure Unit (§5.1)
  pricing.py                The premium function (§5.3)
  safety_score.py           Rider Safety Score (§5.2 Layer B)
  sum_insured.py            Sum insured formulas (§5.4)
  portfolio.py              Book P&L, solvency, capital (§6)
  data_gen.py               Synthetic riders, trips, claims
pages/                      The four Streamlit pages
=======
app.py                      Home page and entry point
shared.py                   Design system, formatting, cached data loading
config/rating_factors.yaml  Every number the model uses
engine/
  config.py                 Config loader and band lookups
  exposure.py               Effective Exposure Unit (§1.2)
  pricing.py                Premium function and governance band (§3.3)
  safety_score.py           Rider Safety Score (§1.2)
  sum_insured.py            Sum insured formulas (§1.2)
  portfolio.py              Book P&L, solvency, capital (§4, §4.1)
  data_gen.py               Synthetic riders, trips, claims
pages/                      The seven pages
>>>>>>> 03dbdc9 (Initial commit)
```

## Deploying a shareable link (optional)

<<<<<<< HEAD
1. Create a free account at github.com and a new **public** repository
2. Upload this whole folder to it
3. Go to share.streamlit.io, sign in with GitHub, click *New app*
4. Select the repo, set the main file to `app.py`, click *Deploy*

Takes about ten minutes and gives you a public URL. Free tier is sufficient.
=======
1. Create a free github.com account and a new **public** repository
2. Upload this whole folder to it (delete any `__pycache__` folders first)
3. Go to share.streamlit.io, sign in with GitHub, click *New app*
4. Select the repo, set the main file to `app.py`, click *Deploy*

About ten minutes, and it gives you a public URL. The free tier is sufficient.
>>>>>>> 03dbdc9 (Initial commit)
