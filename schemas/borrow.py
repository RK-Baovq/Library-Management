from pydantic import BaseModel
from datetime import date


class BorrowIn(BaseModel):
    borrow_date: date
    expected_payment_date: date
