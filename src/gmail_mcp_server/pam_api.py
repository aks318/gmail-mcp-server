from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date


app = FastAPI(title="Mock PAM API")

# In-memory storage for this exercise
POSTED_TRANSACTIONS = {}


class LoanTransaction(BaseModel):
    loan_id: str
    borrower: str
    principal_amount: float
    interest_rate: float
    payment_amount: float
    payment_due_date: date
    currency: str

    approval_decision: Literal["approve"]


@app.post("/transactions", status_code=201)
def create_transaction(transaction: LoanTransaction):

    # Prevent duplicate posting for the same loan and due date
    transaction_key = (
        f"{transaction.loan_id}:{transaction.payment_due_date}"
    )

    if transaction_key in POSTED_TRANSACTIONS:
        raise HTTPException(
            status_code=409,
            detail="Transaction already posted",
        )

    posting_id = str(uuid4())

    result = {
        "posting_id": posting_id,
        "status": "posted",
        "transaction": transaction.model_dump(mode="json"),
    }

    POSTED_TRANSACTIONS[transaction_key] = result

    return result


@app.get("/transactions")
def list_transactions():
    return list(POSTED_TRANSACTIONS.values())