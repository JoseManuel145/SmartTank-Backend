from App.core.mysql import Base
from sqlalchemy import Column, Integer, String


class User(Base):
    __tablename__ = "Users"
    
    id_user = Column(Integer, primary_key=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)