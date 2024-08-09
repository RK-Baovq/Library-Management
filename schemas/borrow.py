from pydantic import BaseModel
from datetime import date
from constants import target


class BorrowIn(BaseModel):
    borrow_date: date
    expected_payment_date: date


class UserUpdate(BaseModel):
    book_id: int
    borrow_date: date
    expected_payment_date: date
    status: str = target.WAITING
