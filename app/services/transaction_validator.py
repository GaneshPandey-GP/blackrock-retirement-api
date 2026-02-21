from typing import List
from app.models.schemas import Transaction, InvalidTransaction

MAX_AMOUNT = 5 * 10**5

def validate_transactions(wage: float, transactions: List[Transaction]):
    valid = []
    invalid = []
    duplicates = []

    seen = set()  # for duplicate detection

    for txn in transactions:
        key = (txn.date, txn.amount)

        # Duplicate check
        if key in seen:
            duplicates.append(txn)
            continue
        seen.add(key)

        # Constraint checks
        if txn.amount < 0:
            invalid.append(InvalidTransaction(**txn.dict(), message="Negative amount"))
            continue

        if txn.amount >= MAX_AMOUNT:
            invalid.append(InvalidTransaction(**txn.dict(), message="Amount exceeds limit"))
            continue

        if txn.ceiling < txn.amount:
            invalid.append(InvalidTransaction(**txn.dict(), message="Ceiling less than amount"))
            continue

        if txn.remanent != (txn.ceiling - txn.amount):
            invalid.append(InvalidTransaction(**txn.dict(), message="Invalid remanent calculation"))
            continue

        if txn.remanent < 0:
            invalid.append(InvalidTransaction(**txn.dict(), message="Negative remanent"))
            continue

        valid.append(txn)

    return {
        "valid": valid,
        "invalid": invalid,
        "duplicates": duplicates
    }