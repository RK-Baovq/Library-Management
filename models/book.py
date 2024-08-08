from sqlalchemy import Column, Integer, String, ForeignKey, Date
from database.db import Base


class Book(Base):
    __tablename__ = "book"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    author = Column(String(255))
    category = Column(Integer, ForeignKey("category.id"))
    publishing_company = Column(String(255))
    publication_date = Column(Date)
    available_quantity = Column(Integer)
    describe = Column(String(255), nullable=True)
