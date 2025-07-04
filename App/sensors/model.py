from App.core.mysql import Base
from sqlalchemy import JSON, Column, Integer, String, DateTime


class Reading(Base):
    __tablename__ = "Readings"
    
    id_reading = Column(Integer, primary_key=True, autoincrement=True)
    sensor = Column(String(100), nullable=False)
    data = Column(JSON, nullable=False) #guardamos el JSON 
    date = Column(DateTime, nullable=False) #fecha de la lectura