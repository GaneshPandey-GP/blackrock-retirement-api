import math
from typing import List
from app.models.schemas import Expense, Transaction


def build_transactions(expenses: List[Expense]):
    transactions = []

    for exp in expenses:
        ceiling = math.floor(exp.amount / 100) * 100 + 100
        remanent = ceiling - exp.amount

        txn = Transaction(
            date=exp.date,
            amount=exp.amount,
            ceiling=ceiling,
            remanent=remanent
        )

        transactions.append(txn)



    return {"transactions": transactions}