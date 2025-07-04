from sqlalchemy.orm import Session
from typing import List, Optional
from .model import Reading
from .schemas import ReadingCreate

class SensorRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_last_n(self, n: int = 30) -> List[Reading]:
        # Devuelve los últimos n registros ordenados por fecha descendente
        return (
            self.db.query(Reading)
            .order_by(Reading.date.desc())
            .limit(n)
            .all()
        )

    def create(self, reading_data: ReadingCreate) -> Reading:
        # Crea y guarda un nuevo registro de lectura
        reading = Reading(
            sensor=reading_data.sensor,
            data=reading_data.data,
            date=reading_data.date
        )
        self.db.add(reading)
        self.db.commit()
        self.db.refresh(reading)
        return reading

    def get_by_id(self, id_reading: int) -> Optional[Reading]:
        # Busca un registro por su id
        return self.db.query(Reading).filter(Reading.id_reading == id_reading).first()