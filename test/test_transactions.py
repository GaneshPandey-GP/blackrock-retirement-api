# Test type: Unit Tests
# Validation: Transaction parsing, validation, and duplicate detection
# Command: pytest test/test_transactions.py -v

import pytest
from app.services.transaction_builder import build_transactions
from app.services.transaction_validator import validate_transactions
from app.models.schemas import Expense, Transaction

# ─── Parse Tests ───────────────────────────────

def test_parse_basic():
    expenses = [Expense(date="2023-10-12 20:15:30", amount=250)]
    result = build_transactions(expenses)
    assert result.transactions[0].ceiling == 300
    assert result.transactions[0].remanent == 50

def test_parse_already_multiple_of_100():
    expenses = [Expense(date="2023-10-12 20:15:30", amount=500)]
    result = build_transactions(expenses)
    assert result.transactions[0].ceiling == 600
    assert result.transactions[0].remanent == 100

def test_parse_total_amounts():
    expenses = [
        Expense(date="2023-10-12 20:15:30", amount=250),
        Expense(date="2023-02-28 15:49:20", amount=375),
        Expense(date="2023-07-01 21:59:00", amount=620),
        Expense(date="2023-12-17 08:09:45", amount=480),
    ]
    result = build_transactions(expenses)
    assert result.totalAmount == 1725.0
    assert result.totalCeiling == 1900.0
    assert result.totalRemanent == 175.0

def test_parse_empty():
    result = build_transactions([])
    assert result.transactions == []
    assert result.totalAmount == 0
    assert result.totalRemanent == 0

# ─── Validator Tests ───────────────────────────

def test_validator_negative_amount():
    transactions = [
        Transaction(date="2023-07-10 09:15:00", amount=-250, ceiling=200, remanent=30)
    ]
    result = validate_transactions(wage=50000, transactions=transactions)
    assert len(result["invalid"]) == 1
    assert result["invalid"][0].message == "Negative amounts are not allowed"

def test_validator_duplicate():
    transactions = [
        Transaction(date="2023-10-12 20:15:30", amount=250, ceiling=300, remanent=50),
        Transaction(date="2023-10-12 20:15:30", amount=250, ceiling=300, remanent=50),
    ]
    result = validate_transactions(wage=50000, transactions=transactions)
    assert len(result["valid"]) == 1
    assert len(result["duplicates"]) == 1

def test_validator_valid_transactions():
    transactions = [
        Transaction(date="2023-01-15 10:30:00", amount=2000, ceiling=2100, remanent=100),
        Transaction(date="2023-03-20 14:45:00", amount=3500, ceiling=3600, remanent=100),
    ]
    result = validate_transactions(wage=50000, transactions=transactions)
    assert len(result["valid"]) == 2
    assert len(result["invalid"]) == 0