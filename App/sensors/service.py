from .repository import SensorRepository
from .schemas import ReadingCreate, ReadingResponse
from typing import List

class SensorService:
    def __init__(self, repository: SensorRepository):
        self.repo = repository

    def get_last_n_readings(self, n: int = 30) -> List[ReadingResponse]:
        readings = self.repo.get_last_n(n)
        return [ReadingResponse.model_validate(r) for r in readings]

    def create_reading(self, data: ReadingCreate) -> ReadingResponse:
        reading = self.repo.create(data)
        return ReadingResponse.model_validate(reading)

    def get_reading_by_id(self, id_reading: int) -> ReadingResponse:
        reading = self.repo.get_by_id(id_reading)
        if not reading:
            raise ValueError("Reading not found")
        return ReadingResponse.model_validate(reading)