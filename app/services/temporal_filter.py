from typing import List
from app.models.schemas import (
    Transaction, InvalidTransaction, ValidTransactionWithKPeriod,
    QPeriod, PPeriod, KPeriod,
    TransactionFilterRequest, TransactionFilterResponse
)
from app.services.transaction_builder import build_transactions

def apply_q_rule(txn: Transaction, q_periods: List[QPeriod]) -> float:
    """
    If transaction date falls in a q period, replace remanent with fixed amount.
    If multiple q periods match, use the one with latest start date.
    If same start date, use first in list.
    """
    matching = [
        q for q in q_periods
        if q.start <= txn.date <= q.end
    ]

    if not matching:
        return txn.remanent

    # latest start wins, ties broken by first in list
    best = max(matching, key=lambda q: q.start)
    return best.fixed


def apply_p_rule(remanent: float, txn: Transaction, p_periods: List[PPeriod]) -> float:
    """
    If transaction date falls in any p period, add ALL their extras to remanent.
    """
    matching = [
        p for p in p_periods
        if p.start <= txn.date <= p.end
    ]

    for p in matching:
        remanent += p.extra

    return remanent


def is_in_k_period(txn: Transaction, k_periods: List[KPeriod]) -> bool:
    """
    Check if transaction falls in ANY k period.
    """
    return any(k.start <= txn.date <= k.end for k in k_periods)


# def filter_transactions(request: TransactionFilterRequest) -> TransactionFilterResponse:
#     valid = []
#     invalid = []
#     seen = set()

#     for txn in request.transactions:
#         key = (txn.date, txn.amount)

#         # --- Duplicate check ---
#         if key in seen:
#             invalid.append(InvalidTransaction(
#                 **txn.dict(),
#                 message="Duplicate transaction"
#             ))
#             continue
#         seen.add(key)

#         # --- Negative amount check ---
#         if txn.amount < 0:
#             invalid.append(InvalidTransaction(
#                 **txn.dict(),
#                 message="Negative amounts are not allowed"
#             ))
#             continue

#         # --- Step 1: Apply q rule (replace remanent) ---
#         remanent = apply_q_rule(txn, request.q)

#         # --- Step 2: Apply p rule (add to remanent) ---
#         remanent = apply_p_rule(remanent, txn, request.p)

#         # --- Step 3: Check k period ---
#         in_k = is_in_k_period(txn, request.k)
#         txn_data = txn.dict()
#         txn_data["remanent"] = remanent  # override with updated remanent
#         txn_data["inKPeriod"] = in_k
        
#         valid.append(ValidTransactionWithKPeriod(
#             **txn_data
#         ))

#     return TransactionFilterResponse(
#         valid=valid,
#         invalid=invalid
#     )


def filter_transactions(request: TransactionFilterRequest) -> TransactionFilterResponse:
    valid = []
    invalid = []
    seen = set()
    txns = build_transactions(request.transactions)["transactions"]
    for txn in txns:
        key = (txn.date, txn.amount)
        if key in seen:
            invalid.append(InvalidTransaction(
                **txn.dict(),
                message="Duplicate transaction"
            ))
            continue
        seen.add(key)

        # --- Negative check ---
        if txn.amount < 0:
            invalid.append(InvalidTransaction(
                **txn.dict(),
                message="Negative amounts are not allowed"
            ))
            continue

        # --- Apply q rule ---
        remanent = apply_q_rule(txn, request.q)

        # --- Apply p rule ---
        remanent = apply_p_rule(remanent, txn, request.p)

        # --- Check k period ---
        in_k = is_in_k_period(txn, request.k)

        txn_data = txn.dict()
        txn_data["remanent"] = remanent
        txn_data["inKPeriod"] = in_k

        valid.append(ValidTransactionWithKPeriod(**txn_data))

    return TransactionFilterResponse(valid=valid, invalid=invalid)