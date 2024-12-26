from sqlalchemy import Column, Integer, String, JSON
from ..models.db import Base, db

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=False, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    project = Column(JSON, nullable=True)