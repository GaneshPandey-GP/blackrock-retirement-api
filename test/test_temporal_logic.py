# Test type: Unit Tests
# Validation: q period, p period, k period rules
# Command: pytest test/test_temporal_logic.py -v

import pytest
from app.services.temporal_filter import filter_transactions
from app.models.schemas import (
    TransactionFilterRequest, Expense,
    QPeriod, PPeriod, KPeriod
)

def make_request(transactions, q=[], p=[], k=[], wage=50000):
    return TransactionFilterRequest(
        q=q, p=p, k=k,
        wage=wage,
        transactions=transactions
    )

# ─── Q Period Tests ────────────────────────────

def test_q_period_replaces_remanent():
    """Transaction in July should have remanent replaced with 0"""
    request = make_request(
        transactions=[Expense(date="2023-07-15 10:30:00", amount=620)],
        q=[QPeriod(fixed=0, start="2023-07-01 00:00:00", end="2023-07-31 23:59:59")]
    )
    result = filter_transactions(request)
    assert result.valid[0].remanent == 0

def test_q_period_multiple_match_latest_start_wins():
    """If multiple q periods match, latest start date wins"""
    request = make_request(
        transactions=[Expense(date="2023-07-15 10:30:00", amount=620)],
        q=[
            QPeriod(fixed=50, start="2023-07-01 00:00:00", end="2023-07-31 23:59:59"),
            QPeriod(fixed=99, start="2023-07-10 00:00:00", end="2023-07-31 23:59:59"),
        ]
    )
    result = filter_transactions(request)
    assert result.valid[0].remanent == 99  # latest start wins

def test_q_period_no_match():
    """Transaction outside q period should keep original remanent"""
    request = make_request(
        transactions=[Expense(date="2023-02-28 15:49:20", amount=375)],
        q=[QPeriod(fixed=0, start="2023-07-01 00:00:00", end="2023-07-31 23:59:59")]
    )
    result = filter_transactions(request)
    assert result.valid[0].remanent == 25  # original remanent (400-375)

# ─── P Period Tests ────────────────────────────

def test_p_period_adds_extra():
    """Transaction in Oct-Dec should have extra added to remanent"""
    request = make_request(
        transactions=[Expense(date="2023-10-12 20:15:30", amount=250)],
        p=[PPeriod(extra=25, start="2023-10-01 08:00:00", end="2023-12-31 19:59:59")]
    )
    result = filter_transactions(request)
    assert result.valid[0].remanent == 75  # 50 + 25

def test_p_period_multiple_all_add():
    """Multiple p periods should ALL add to remanent"""
    request = make_request(
        transactions=[Expense(date="2023-10-12 20:15:30", amount=250)],
        p=[
            PPeriod(extra=25, start="2023-10-01 00:00:00", end="2023-12-31 23:59:59"),
            PPeriod(extra=10, start="2023-10-01 00:00:00", end="2023-12-31 23:59:59"),
        ]
    )
    result = filter_transactions(request)
    assert result.valid[0].remanent == 85  # 50 + 25 + 10

def test_q_and_p_both_apply():
    """q replaces first, then p adds on top"""
    request = make_request(
        transactions=[Expense(date="2023-10-12 20:15:30", amount=250)],
        q=[QPeriod(fixed=30, start="2023-10-01 00:00:00", end="2023-12-31 23:59:59")],
        p=[PPeriod(extra=25, start="2023-10-01 00:00:00", end="2023-12-31 23:59:59")]
    )
    result = filter_transactions(request)
    assert result.valid[0].remanent == 55  # q replaces to 30, p adds 25

# ─── K Period Tests ────────────────────────────

def test_k_period_in_range():
    request = make_request(
        transactions=[Expense(date="2023-06-15 10:00:00", amount=300)],
        k=[KPeriod(start="2023-01-01 00:00:00", end="2023-12-31 23:59:59")]
    )
    result = filter_transactions(request)
    assert result.valid[0].inKPeriod == True

def test_k_period_out_of_range():
    request = make_request(
        transactions=[Expense(date="2023-12-25 10:00:00", amount=300)],
        k=[KPeriod(start="2023-01-01 00:00:00", end="2023-11-30 23:59:59")]
    )
    result = filter_transactions(request)
    assert result.valid[0].inKPeriod == False

# ─── Invalid Transaction Tests ─────────────────

def test_negative_amount_invalid():
    request = make_request(
        transactions=[Expense(date="2023-12-17 08:09:45", amount=-480)]
    )
    result = filter_transactions(request)
    assert len(result.invalid) == 1
    assert result.invalid[0].message == "Negative amounts are not allowed"

def test_duplicate_invalid():
    request = make_request(
        transactions=[
            Expense(date="2023-10-12 20:15:30", amount=250),
            Expense(date="2023-10-12 20:15:30", amount=250),
        ]
    )
    result = filter_transactions(request)
    assert len(result.valid) == 1
    assert len(result.invalid) == 1
    assert result.invalid[0].message == "Duplicate transaction"