from sqlalchemy import Column, Integer, Enum, ForeignKey, DateTime
from database.db import Base
from constants import target, enum


class Borrow(Base):
    __tablename__ = "borrow"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    book_id = Column(Integer, ForeignKey("book.id"))
    borrow_date = Column(DateTime)
    expected_payment_date = Column(DateTime)
    actual_payment_date = Column(DateTime, nullable=True)
    status = Column(Enum(*enum.Borrow_status), default=target.BORROW)
