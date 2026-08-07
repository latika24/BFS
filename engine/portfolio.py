"""
Book-level economics: the year 1-7 trajectory, solvency, and capital.

Business plan references: sections 6.1, 6.2, 6.4, 6.6, 6.7.

Year 1 is the first full year of writing business (project month 21 onward).
The important point this model is built to show: what moves the combined ratio
from 190% to 95% is the EXPENSE ratio collapsing as premium grows against a
largely fixed regulatory cost base - not the loss ratio, which is respectable
by year four. That is the lesson from the international benchmark in section 3.5.
"""
from __future__ import annotations
import pandas as pd

from .config import CFG

CR = 1e7  # one crore


def burning_cost(cfg: dict | None = None) -> dict:
    """Expected claim cost per rider-year, built up head by head (section 6.1)."""
    cfg = cfg or CFG
    rows, total = [], 0.0
    for head in cfg["burning_cost"]:
        annual = head["frequency_per_1000"] * head["average_claim"]
        total += annual
        rows.append({
            "Benefit head": head["head"],
            "Frequency per 1,000": head["frequency_per_1000"],
            "Average claim": head["average_claim"],
            "Annual cost per 1,000": annual,
        })
    return {"rows": rows, "total_per_1000": total, "per_rider": total / 1000.0}


def trajectory(cfg: dict | None = None,
               loss_ratio_override: list[float] | None = None,
               growth_factor: float = 1.0,
               gwp_per_worker: float | None = None) -> pd.DataFrame:
    """
    Build the year 1-7 P&L.

    growth_factor scales the worker count in every year - use it to model the
    section 6.7 stress case where growth stalls.
    loss_ratio_override replaces the planned loss ratio path.
    """
    cfg = cfg or CFG
    p = cfg["portfolio"]
    gwp_pw = gwp_per_worker if gwp_per_worker is not None else p["gwp_per_worker"]

    ri = p["reinsurance_pct_gwp"]
    wallet = p["no_claim_wallet_pct_gwp"]
    inv = p["investment_income_pct_gwp"]
    cession = p["quota_share_cession"]

    sol = p["solvency"]
    rows = []
    cumulative_uw = 0.0
    cumulative_pbt = 0.0

    fixed_share = p.get("fixed_expense_share", 0.65)

    for i, yr in enumerate(p["trajectory"]):
        workers = yr["workers"] * growth_factor
        lr = (loss_ratio_override[i]
              if loss_ratio_override and i < len(loss_ratio_override)
              else yr["loss_ratio"])

        gwp = workers * gwp_pw

        # The expense ratio is DERIVED, not assumed.
        #
        # The planned ratio in the config holds at the planned scale. Split the
        # implied expense rupees into a fixed part (the regulatory cost base -
        # statutory key management, actuarial, audit, compliance, tech) and a
        # variable part (acquisition, claims handling) that scales with premium.
        # Then, if growth differs from plan, only the variable part moves.
        #
        # This is the whole point of section 6.7's second failure mode: if the
        # book never reaches scale, the expense ratio never falls, because the
        # cost base of a licensed insurer does not shrink to match. Holding the
        # expense ratio fixed while shrinking premium would hide exactly the
        # risk the scenario exists to show.
        plan_gwp = yr["workers"] * gwp_pw
        plan_expenses = plan_gwp * yr["expense_ratio"]
        fixed_expenses = plan_expenses * fixed_share
        variable_rate = (plan_expenses * (1 - fixed_share) / plan_gwp
                         if plan_gwp else 0.0)
        expenses = fixed_expenses + variable_rate * gwp
        er = expenses / gwp if gwp else 0.0
        combined = lr + er + ri + wallet
        uw_result = gwp * (1 - combined)
        inv_income = gwp * inv
        pbt = uw_result + inv_income

        cumulative_uw += uw_result
        cumulative_pbt += pbt

        nwp = gwp * (1 - cession)
        rsm = max(sol["rsm_floor_cr"] * CR, nwp * sol["rsm_pct_nwp"])
        asm_statutory = rsm * sol["statutory_ratio"]
        asm_target = rsm * sol["target_ratio"]

        rows.append({
            "Year": yr["year"],
            "Active workers": workers,
            "GWP": gwp,
            "Loss ratio": lr,
            "Expense ratio": er,
            "Reinsurance": ri,
            "No-Claim Wallet": wallet,
            "Combined ratio": combined,
            "Underwriting result": uw_result,
            "Investment income": inv_income,
            "Profit before tax": pbt,
            "Cumulative UW result": cumulative_uw,
            "Cumulative PBT": cumulative_pbt,
            "Net written premium": nwp,
            "RSM": rsm,
            "ASM @150%": asm_statutory,
            "ASM @200%": asm_target,
        })

    return pd.DataFrame(rows)


def capital_plan(cfg: dict | None = None) -> pd.DataFrame:
    cfg = cfg or CFG
    return pd.DataFrame(cfg["portfolio"]["funding_rounds"])


def solvency_position(df: pd.DataFrame, cfg: dict | None = None) -> pd.DataFrame:
    """
    Track available solvency margin against requirement, given the funding
    rounds and accumulated losses. Flags the year the internal throttle
    (section 12.6) would fire.
    """
    cfg = cfg or CFG
    p = cfg["portfolio"]
    sol = p["solvency"]

    raised_by_year = {}
    for r in p["funding_rounds"]:
        raised_by_year.setdefault(r["year"], 0.0)
        raised_by_year[r["year"]] += r["amount_cr"] * CR

    build_cost = p["pre_launch_build_cost_cr"] * CR

    out = []
    cumulative_raised = raised_by_year.get(0, 0.0)
    for _, row in df.iterrows():
        yr = int(row["Year"])
        cumulative_raised += raised_by_year.get(yr, 0.0)
        net_worth = cumulative_raised - build_cost + row["Cumulative PBT"]
        ratio = net_worth / row["RSM"] if row["RSM"] else 0.0
        out.append({
            "Year": yr,
            "Capital raised (cumulative)": cumulative_raised,
            "Net worth (ASM proxy)": net_worth,
            "RSM": row["RSM"],
            "Solvency ratio": ratio,
            "Above statutory 150%": ratio >= sol["statutory_ratio"],
            "Above throttle 180%": ratio >= sol["internal_throttle_ratio"],
            "Above target 200%": ratio >= sol["target_ratio"],
        })
    return pd.DataFrame(out)


def breakeven_year(df: pd.DataFrame) -> int | None:
    """First year with a positive underwriting result."""
    hits = df[df["Underwriting result"] > 0]
    return int(hits.iloc[0]["Year"]) if len(hits) else None


def per_rider_pnl(cfg: dict | None = None) -> pd.DataFrame:
    """The steady-state per-rider P&L (section 6.2)."""
    cfg = cfg or CFG
    p = cfg["portfolio"]
    gwp = p["gwp_per_worker"]
    final = p["trajectory"][-1]
    lr, er = final["loss_ratio"], final["expense_ratio"]
    ri, wallet, inv = (p["reinsurance_pct_gwp"], p["no_claim_wallet_pct_gwp"],
                       p["investment_income_pct_gwp"])

    lines = [
        ("Gross written premium", gwp, 1.0),
        ("Claims incurred", -gwp * lr, lr),
        ("Reinsurance cost, net of commission", -gwp * ri, ri),
        ("Operating expenses", -gwp * er, er),
        ("No-Claim Wallet credited to workers", -gwp * wallet, wallet),
    ]
    combined = lr + er + ri + wallet
    uw = gwp * (1 - combined)
    lines.append(("Underwriting result", uw, 1 - combined))
    lines.append(("Investment income", gwp * inv, inv))
    lines.append(("Profit before tax", uw + gwp * inv, (uw + gwp * inv) / gwp))

    return pd.DataFrame(
        [{"Line": n, "Rs per rider-year": round(v), "% of GWP": pct}
         for n, v, pct in lines]
    )
