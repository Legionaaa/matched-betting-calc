from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

QUALIFIER = "qualifier"
FREE_BET_SNR = "free_bet_snr"
MONEY_BACK_IF_STAKE_LOSES = "money_back_if_stake_loses"

VALID_BET_TYPES = {QUALIFIER, FREE_BET_SNR, MONEY_BACK_IF_STAKE_LOSES}


@dataclass
class CalculationResult:
    base_lay_stake: float
    adjusted_lay_stake: float
    placed_lay_stake: float
    lay_liability: float
    bookmaker_if_back_wins: float
    cashback_if_back_wins: float
    exchange_if_back_wins: float
    total_if_back_wins: float
    bookmaker_if_lay_wins: float
    cashback_if_lay_wins: float
    exchange_if_lay_wins: float
    total_if_lay_wins: float
    profit_floor: float
    profit_skew: float


def format_currency(value: float) -> str:
    sign = "-" if value < 0 else ""
    return f"{sign}£{abs(value):,.2f}"


def round_currency(value: float) -> float:
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def calculate_matched_bet(
    back_stake: float,
    back_odds: float,
    lay_odds: float,
    back_commission_percentage: float,
    lay_commission_percentage: float,
    bet_type: str = QUALIFIER,
    adjustment_percentage: float = 0.0,
    cashback_amount: float = 0.0,
) -> CalculationResult:
    validate_positive(back_stake, "Back stake")
    validate_minimum(back_odds, "Back odds", minimum=1.01)
    validate_minimum(lay_odds, "Lay odds", minimum=1.01)
    validate_bet_type(bet_type)
    validate_non_negative(cashback_amount, "Cashback")

    back_commission = percentage_to_fraction(back_commission_percentage, "Back commission")
    lay_commission = percentage_to_fraction(lay_commission_percentage, "Lay commission")

    denominator = lay_odds - lay_commission
    if denominator <= 0:
        raise ValueError("Lay odds must be greater than the lay commission amount.")

    (
        bookmaker_if_back_wins,
        bookmaker_if_lay_wins,
        cashback_if_back_wins,
        cashback_if_lay_wins,
    ) = calculate_bookmaker_outcomes(
        back_stake=back_stake,
        back_odds=back_odds,
        back_commission=back_commission,
        bet_type=bet_type,
        cashback_amount=cashback_amount,
    )

    base_lay_stake = (
        (bookmaker_if_back_wins + cashback_if_back_wins)
        - (bookmaker_if_lay_wins + cashback_if_lay_wins)
    ) / denominator

    adjustment_multiplier = 1.0 + (adjustment_percentage / 100.0)
    if adjustment_multiplier <= 0:
        raise ValueError("The slider adjustment makes the lay stake zero or negative.")

    adjusted_lay_stake = base_lay_stake * adjustment_multiplier
    placed_lay_stake = round_currency(adjusted_lay_stake)
    lay_liability = placed_lay_stake * (lay_odds - 1.0)

    exchange_if_back_wins = -lay_liability
    total_if_back_wins = bookmaker_if_back_wins + cashback_if_back_wins + exchange_if_back_wins

    exchange_if_lay_wins = placed_lay_stake * (1.0 - lay_commission)
    total_if_lay_wins = bookmaker_if_lay_wins + cashback_if_lay_wins + exchange_if_lay_wins
    profit_floor = min(total_if_back_wins, total_if_lay_wins)
    profit_skew = abs(total_if_back_wins - total_if_lay_wins)

    return CalculationResult(
        base_lay_stake=base_lay_stake,
        adjusted_lay_stake=adjusted_lay_stake,
        placed_lay_stake=placed_lay_stake,
        lay_liability=lay_liability,
        bookmaker_if_back_wins=bookmaker_if_back_wins,
        cashback_if_back_wins=cashback_if_back_wins,
        exchange_if_back_wins=exchange_if_back_wins,
        total_if_back_wins=total_if_back_wins,
        bookmaker_if_lay_wins=bookmaker_if_lay_wins,
        cashback_if_lay_wins=cashback_if_lay_wins,
        exchange_if_lay_wins=exchange_if_lay_wins,
        total_if_lay_wins=total_if_lay_wins,
        profit_floor=profit_floor,
        profit_skew=profit_skew,
    )


def calculate_bookmaker_outcomes(
    back_stake: float,
    back_odds: float,
    back_commission: float,
    bet_type: str,
    cashback_amount: float,
) -> tuple[float, float, float, float]:
    winnings = back_stake * (back_odds - 1.0) * (1.0 - back_commission)

    if bet_type == QUALIFIER:
        return winnings, -back_stake, 0.0, 0.0

    if bet_type == FREE_BET_SNR:
        return winnings, 0.0, 0.0, 0.0

    if bet_type == MONEY_BACK_IF_STAKE_LOSES:
        return winnings, -back_stake, 0.0, cashback_amount

    raise ValueError(f"Unsupported bet type: {bet_type}")


def validate_positive(value: float, label: str) -> None:
    if value <= 0:
        raise ValueError(f"{label} must be greater than zero.")


def validate_minimum(value: float, label: str, minimum: float) -> None:
    if value < minimum:
        raise ValueError(f"{label} must be at least {minimum:.2f}.")


def validate_non_negative(value: float, label: str) -> None:
    if value < 0:
        raise ValueError(f"{label} cannot be negative.")


def validate_percentage_range(value: float, label: str) -> None:
    if not 0 <= value < 100:
        raise ValueError(f"{label} must be between 0 and 100.")


def validate_bet_type(value: str) -> None:
    if value not in VALID_BET_TYPES:
        raise ValueError("Bet type must be qualifier, free_bet_snr, or money_back_if_stake_loses.")


def percentage_to_fraction(percentage: float, label: str) -> float:
    validate_percentage_range(percentage, label)
    return percentage / 100.0
