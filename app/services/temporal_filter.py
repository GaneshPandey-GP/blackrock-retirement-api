from typing import List,Optional
from concurrent.futures import ThreadPoolExecutor
import os
import math
from app.models.schemas import (
    Transaction, InvalidTransaction, ValidTransactionWithKPeriod,
    QPeriod, PPeriod, KPeriod,
    TransactionFilterRequest, TransactionFilterResponse
)


def preprocess_q_periods(q_periods: List[QPeriod]) -> List[QPeriod]:
    return sorted(q_periods, key=lambda q: q.start, reverse=True)



def apply_q_rule(txn_date, q_sorted: List[QPeriod]) -> Optional[float]:
    for q in q_sorted:
        if q.start <= txn_date <= q.end:
            return q.fixed
    return None

def apply_p_rule(txn_date, p_periods: List[PPeriod]) -> float:
    return sum(p.extra for p in p_periods if p.start <= txn_date <= p.end)


def is_in_k_period(txn_date, k_periods: List[KPeriod]) -> bool:
    if not k_periods:
        return True
    return any(k.start <= txn_date <= k.end for k in k_periods)



def process_chunk(args):
    expenses_chunk, q_sorted, p_periods, k_periods, seen = args
    chunk_valid = []
    chunk_invalid = []

    for expense in expenses_chunk:
        key = (expense.date, expense.amount)

      
        if key in seen:
            chunk_invalid.append(InvalidTransaction(
                date=expense.date,
                amount=expense.amount,
                message="Duplicate transaction"
            ))
            continue
        seen.add(key)

    
        if expense.amount < 0:
            chunk_invalid.append(InvalidTransaction(
                date=expense.date,
                amount=expense.amount,
                message="Negative amounts are not allowed"
            ))
            continue

        ceiling = math.floor(expense.amount / 100) * 100 + 100
        remanent = ceiling - expense.amount

        txn = Transaction(
            date=expense.date,
            amount=expense.amount,
            ceiling=ceiling,
            remanent=remanent
        )


        q_result = apply_q_rule(expense.date, q_sorted)
        remanent = q_result if q_result is not None else remanent


        remanent += apply_p_rule(expense.date, p_periods)

   
        in_k = is_in_k_period(expense.date, k_periods)

        txn_data = txn.model_dump()
        txn_data["remanent"] = remanent
        txn_data["inKPeriod"] = in_k
        chunk_valid.append(ValidTransactionWithKPeriod(**txn_data))

    return chunk_valid, chunk_invalid



def filter_transactions(request: TransactionFilterRequest) -> TransactionFilterResponse:
    q_sorted = preprocess_q_periods(request.q)
    seen = set()

    CHUNK_SIZE = 10000
    chunks = [
        request.transactions[i:i + CHUNK_SIZE]
        for i in range(0, len(request.transactions), CHUNK_SIZE)
    ]
    
    args_list = [
        (chunk, q_sorted, request.p, request.k, seen)
        for chunk in chunks
    ]
    valid = []
    invalid = []

    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        results = list(executor.map(process_chunk, args_list))
        
    for chunk_valid, chunk_invalid in results:
        valid.extend(chunk_valid)
        invalid.extend(chunk_invalid)

    return TransactionFilterResponse(valid=valid, invalid=invalid)