# Test type: Unit Tests
# Validation: NPS and Index Fund return calculations, tax benefit, inflation adjustment
# Command: pytest test/test_returns.py -v

import pytest
from app.services.return_calculator import calculate_returns
from app.services.tax_calculator import calculate_tax_benefit
from app.models.schemas import ReturnsRequest, Expense, QPeriod, PPeriod, KPeriod

def make_returns_request():
    return ReturnsRequest(
        age=29,
        wage=50000,
        inflation=5.5,
        q=[QPeriod(fixed=0, start="2023-07-01 00:00:00", end="2023-07-31 23:59:59")],
        p=[PPeriod(extra=25, start="2023-10-01 08:00:00", end="2023-12-31 19:59:59")],
        k=[
            KPeriod(start="2023-01-01 00:00:00", end="2023-12-31 23:59:59"),
            KPeriod(start="2023-03-01 00:00:00", end="2023-11-30 23:59:59"),
        ],
        transactions=[
            Expense(date="2023-02-28 15:49:20", amount=375),
            Expense(date="2023-07-01 21:59:00", amount=620),
            Expense(date="2023-10-12 20:15:30", amount=250),
            Expense(date="2023-12-17 08:09:45", amount=480),
        ]
    )

# ─── NPS Tests ─────────────────────────────────

def test_nps_amount_k1():
    result = calculate_returns(make_returns_request(), rate=0.0711)
    k1 = result.savingsByDates[0]
    assert k1.amount == 145.0

def test_nps_profit_k1():
    result = calculate_returns(make_returns_request(), rate=0.0711)
    k1 = result.savingsByDates[0]
    assert round(k1.profit, 2) == 86.88

def test_nps_amount_k2():
    result = calculate_returns(make_returns_request(), rate=0.0711)
    k2 = result.savingsByDates[1]
    assert k2.amount == 75.0

def test_nps_profit_k2():
    result = calculate_returns(make_returns_request(), rate=0.0711)
    k2 = result.savingsByDates[1]
    assert round(k2.profit, 2) == 44.94

# ─── Index Fund Tests ──────────────────────────

def test_index_amount_k1():
    result = calculate_returns(make_returns_request(), rate=0.1449)
    k1 = result.savingsByDates[0]
    assert k1.amount == 145.0

def test_index_profit_k1():
    result = calculate_returns(make_returns_request(), rate=0.1449)
    k1 = result.savingsByDates[0]
    assert round(k1.profit, 2) == 1684.5  # 1829.5 - 145

def test_index_tax_benefit_always_zero():
    result = calculate_returns(make_returns_request(), rate=0.1449)
    for k in result.savingsByDates:
        assert k.taxBenefit == 0.0

# ─── Tax Benefit Tests ─────────────────────────

def test_tax_benefit_zero_slab():
    """Income below 7L → tax = 0, benefit = 0"""
    benefit = calculate_tax_benefit(income=600000, invested=145)
    assert benefit == 0.0

def test_tax_benefit_10_percent_slab():
    """Income in 7L-10L slab"""
    benefit = calculate_tax_benefit(income=800000, invested=10000)
    assert benefit > 0

def test_tax_benefit_cap_at_2L():
    """NPS deduction capped at 2L"""
    benefit = calculate_tax_benefit(income=2000000, invested=500000)
    # deduction should be capped at 200000
    assert benefit == calculate_tax_benefit(income=2000000, invested=200000)

# ─── Total Amount Tests ────────────────────────

def test_total_transaction_amount():
    result = calculate_returns(make_returns_request(), rate=0.0711)
    assert result.totalTransactionAmount == 1725.0

def test_total_ceiling():
    result = calculate_returns(make_returns_request(), rate=0.0711)
    assert result.totalCeiling == 1900.0