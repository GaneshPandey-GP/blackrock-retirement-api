from typing import List
from app.models.schemas import (
    Transaction, QPeriod, PPeriod, KPeriod,
    ReturnsRequest, ReturnsResponse, SavingByDate
)
from app.services.temporal_filter import apply_q_rule, apply_p_rule
from app.services.transaction_builder import build_transactions
from app.services.tax_calculator import calculate_tax_benefit

NPS_RATE = 0.0711
INDEX_RATE = 0.1449


def get_investment_years(age: int) -> int:
    return max(60 - age, 5)


def compound_interest(principal: float, rate: float, years: int) -> float:
    return principal * (1 + rate) ** years


def inflation_adjust(amount: float, inflation: float, years: int) -> float:
    return amount / (1 + inflation / 100) ** years


def calculate_remanent_for_transaction(
    txn: Transaction,
    q_periods: List[QPeriod],
    p_periods: List[PPeriod]
) -> float:
    
    q_result = apply_q_rule(txn.date, q_periods)
    remanent = q_result if q_result is not None else txn.remanent

    remanent += apply_p_rule(txn.date, p_periods)
    return remanent



def calculate_returns(request: ReturnsRequest, rate: float, is_nps: bool) -> ReturnsResponse:
    annual_wage = request.wage * 12
    years = get_investment_years(request.age)

    valid_transactions = []
    seen = set()

    txns = build_transactions(request.transactions)["transactions"]

    for txn in txns:
        if txn.amount < 0:
            continue

        key = (txn.date, txn.amount)
        if key in seen:
            continue
        seen.add(key)

        txn_data = txn.dict()
        txn_data["remanent"] = calculate_remanent_for_transaction(
            txn, request.q, request.p
        )
        valid_transactions.append(Transaction(**txn_data))

    total_amount = sum(t.amount for t in valid_transactions)
    total_ceiling = sum(t.ceiling for t in valid_transactions)

    savings_by_dates = []

    for k in request.k:
        amount = sum(
            t.remanent for t in valid_transactions
            if k.start <= t.date <= k.end
        )

        A = compound_interest(amount, rate, years)

        real_value = inflation_adjust(A, request.inflation, years)

        profit = round(real_value - amount, 2)

        tax_benefit = calculate_tax_benefit(amount, annual_wage) if is_nps else 0.0

        savings_by_dates.append(SavingByDate(
            start=k.start,
            end=k.end,
            amount=round(amount, 2),
            profit=profit,
            taxBenefit=tax_benefit
        ))

    return ReturnsResponse(
        totalTransactionAmount=round(total_amount, 2),
        totalCeiling=round(total_ceiling, 2),
        savingsByDates=savings_by_dates
    )
