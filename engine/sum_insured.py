"""
Sum insured determination.

Business plan reference: section 1.2.

Formula-driven rather than menu-driven, because gig workers do not have the
information to choose a sum insured well. Earnings are observed through the
Account Aggregator framework or platform APIs, not self-declared - which is
the control that stops the death benefit being gamed upward.
"""
from __future__ import annotations
from .config import CFG


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def accidental_death(annual_net_earnings: float, cfg: dict | None = None) -> dict:
    """Human life value approach: 8 x observed annual earnings, clamped."""
    cfg = (cfg or CFG)["sum_insured"]
    raw = cfg["ad_earnings_multiple"] * annual_net_earnings
    si = clamp(raw, cfg["ad_floor"], cfg["ad_ceiling"])
    return {
        "formula": "clamp( 8 x annualised observed net earnings, Rs 5,00,000, Rs 10,00,000 )",
        "uncapped": raw,
        "value": si,
        "binding": ("floor" if raw < cfg["ad_floor"]
                    else "ceiling" if raw > cfg["ad_ceiling"] else "none"),
    }


def daily_income_benefit(avg_daily_net_earnings: float,
                         platform_loss_of_pay_daily: float = 0.0,
                         cfg: dict | None = None) -> dict:
    """
    75% of observed daily earnings, capped, less any platform loss-of-pay
    benefit for the same period.

    The 0.75 factor and the platform offset both exist for the same reason:
    it must never be more profitable to stay off the road than to ride. The
    offset is a clause in our own contract, not a recovery right against the
    platform's insurer - fixed-benefit policies carry no contribution right.
    """
    cfg = (cfg or CFG)["sum_insured"]
    gross = cfg["dib_earnings_factor"] * avg_daily_net_earnings
    capped = min(gross, cfg["dib_daily_cap"])
    net = max(0.0, capped - platform_loss_of_pay_daily)
    return {
        "formula": "min( 0.75 x observed avg daily net earnings, Rs 1,200 ) less platform loss-of-pay",
        "gross": gross,
        "after_cap": capped,
        "platform_offset": platform_loss_of_pay_daily,
        "value": net,
        "waiting_days": cfg["dib_waiting_days"],
        "max_days": cfg["dib_max_days"],
        "max_annual_payout": net * cfg["dib_max_days"],
        "replacement_ratio": (net / avg_daily_net_earnings
                              if avg_daily_net_earnings else 0.0),
    }


def vehicle_benefit(idv: float, cfg: dict | None = None) -> dict:
    cfg = (cfg or CFG)["sum_insured"]
    si = min(idv, cfg["vehicle_idv_cap"])
    return {
        "formula": "min( IDV, Rs 80,000 ); per event capped at 40% of SI; annual aggregate 100%",
        "value": si,
        "per_event": si * cfg["vehicle_per_event_pct"],
        "annual_aggregate": si * cfg["vehicle_annual_aggregate_pct"],
    }


def consignment_benefit(p95_order_value: float, cfg: dict | None = None) -> dict:
    cfg = (cfg or CFG)["sum_insured"]
    per_event = min(p95_order_value, cfg["consignment_per_event_cap"])
    return {
        "formula": "min( P95(order value, trailing 30 days), Rs 25,000 ) per event; 10x annual aggregate",
        "per_event": per_event,
        "annual_aggregate": per_event * cfg["consignment_aggregate_multiple"],
    }


def fixed_benefits(cfg: dict | None = None) -> dict:
    c = (cfg or CFG)["sum_insured"]
    return {
        "hospital_daily_cash": c["hospital_daily_cash"],
        "hospital_cash_max_days": c["hospital_cash_max_days"],
        "hospital_cash_max_payout": c["hospital_daily_cash"] * c["hospital_cash_max_days"],
        "fracture_range": (c["fracture_min"], c["fracture_max"]),
        "ambulance_network_cap": c["ambulance_network_cap"],
        "ambulance_out_of_network_fixed": c["ambulance_out_of_network_fixed"],
    }


def full_schedule(monthly_net_earnings: float,
                  idv: float = 65000,
                  p95_order_value: float = 1800,
                  platform_loss_of_pay_daily: float = 0.0,
                  cfg: dict | None = None) -> dict:
    """Everything at once, for the Sum Insured page."""
    annual = monthly_net_earnings * 12
    daily = monthly_net_earnings / 26.0
    return {
        "inputs": {
            "monthly_net_earnings": monthly_net_earnings,
            "annual_net_earnings": annual,
            "avg_daily_net_earnings": daily,
            "idv": idv,
            "p95_order_value": p95_order_value,
        },
        "accidental_death": accidental_death(annual, cfg),
        "daily_income_benefit": daily_income_benefit(
            daily, platform_loss_of_pay_daily, cfg),
        "vehicle": vehicle_benefit(idv, cfg),
        "consignment": consignment_benefit(p95_order_value, cfg),
        "fixed": fixed_benefits(cfg),
    }
