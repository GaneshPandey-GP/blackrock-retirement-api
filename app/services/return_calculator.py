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
    remanent = apply_q_rule(txn, q_periods)
    remanent = apply_p_rule(remanent, txn, p_periods)
    return remanent


def calculate_returns(request: ReturnsRequest, rate: float, is_nps: bool) -> ReturnsResponse:
    annual_wage = request.wage * 12
    years = get_investment_years(request.age)

    valid_transactions = []
    seen = set()

    txns = build_transactions(request.transactions)["transactions"]
    # --- Filter valid transactions ---
    for txn in txns:
        # skip negatives
        if txn.amount < 0:
            continue

        key = (txn.date, txn.amount)

        # skip duplicates
        if key in seen:
            continue
        seen.add(key)

        # ceiling = get_ceiling(expense.amount)
        # remanent = ceiling - expense.amount

        # txn = Transaction(
        #     date=expense.date,
        #     amount=expense.amount,
        #     ceiling=ceiling,
        #     remanent=remanent
        # )

        # apply q and p rules
        txn_data = txn.dict()
        txn_data["remanent"] = calculate_remanent_for_transaction(txn, request.q, request.p)
        valid_transactions.append(Transaction(**txn_data))

    # --- Totals ---
    total_amount = sum(t.amount for t in valid_transactions)
    total_ceiling = sum(t.ceiling for t in valid_transactions)

    # --- Savings by k periods ---
    savings_by_dates = []

    for k in request.k:
        # sum remanents within this k period
        amount = sum(
            t.remanent for t in valid_transactions
            if k.start <= t.date <= k.end
        )

        # compound interest
        A = compound_interest(amount, rate, years)
        profit = round(A - amount, 2)

        # inflation adjust the profit
        profit_real = round(inflation_adjust(A, request.inflation, years) - 
                           inflation_adjust(amount, request.inflation, years), 2)

        # tax benefit (NPS only)
        tax_benefit = calculate_tax_benefit(amount, annual_wage) if is_nps else 0.0

        savings_by_dates.append(SavingByDate(
            start=k.start,
            end=k.end,
            amount=round(amount, 2),
            profit=profit_real,
            taxBenefit=tax_benefit
        ))

    return ReturnsResponse(
        totalTransactionAmount=round(total_amount, 2),
        totalCeiling=round(total_ceiling, 2),
        savingsByDates=savings_by_dates
    )