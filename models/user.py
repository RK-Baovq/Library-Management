from sqlalchemy import Column, Integer, String, Enum
from database.db import Base
from constants import target, enum


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True)
    password = Column(String(255))
    email = Column(String(255), unique=True)
    role = Column(Enum(*enum.User_Role), default=target.USER)
