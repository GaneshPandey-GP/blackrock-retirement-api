from pydantic import BaseModel,field_validator
from datetime import datetime
from typing import List

class Expense(BaseModel):
    date: datetime
    amount: float
    
    # @field_validator('amount')
    # @classmethod
    # def amount_must_be_non_negative(cls, v):
    #     if v < 0:
    #         raise ValueError('Amount must be non-negative')
    #     return v
    

class Transaction(BaseModel):
    date: datetime
    amount: float
    ceiling: float
    remanent: float

class TransactionParseRequest(BaseModel):
    expenses: List[Expense]

class TransactionParseResponse(BaseModel):
    transactions: List[Transaction]
    totalAmount: float
    totalCeiling: float
    totalRemanent: float

class InvalidTransaction(Transaction):
    message: str

class TransactionValidatorRequest(BaseModel):
    wage: float
    transactions: List[Transaction]

class TransactionValidatorResponse(BaseModel):
    valid: List[Transaction]
    invalid: List[InvalidTransaction]
    duplicates: List[Transaction]    
    
class QPeriod(BaseModel):
    fixed: float
    start: datetime
    end: datetime

class PPeriod(BaseModel):
    extra: float
    start: datetime
    end: datetime

class KPeriod(BaseModel):
    start: datetime
    end: datetime



class ValidTransactionWithKPeriod(Transaction):
    inKPeriod: bool

class TransactionFilterRequest(BaseModel):
    q: List[QPeriod]
    p: List[PPeriod]
    k: List[KPeriod]
    wage: float
    # transactions: List[Transaction]
    transactions: List[Expense]

class TransactionFilterResponse(BaseModel):
    valid: List[ValidTransactionWithKPeriod]
    invalid: List[InvalidTransaction]

class SavingByDate(BaseModel):
    start: datetime
    end: datetime
    amount: float
    profit: float
    taxBenefit: float

class ReturnsRequest(BaseModel):
    age: int
    wage: float
    inflation: float
    q: List[QPeriod]
    p: List[PPeriod]
    k: List[KPeriod]
    transactions: List[Expense]

class ReturnsResponse(BaseModel):
    totalTransactionAmount: float
    totalCeiling: float
    savingsByDates: List[SavingByDate]    