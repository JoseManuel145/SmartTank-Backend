from typing import Any, Dict
from pydantic import BaseModel
from datetime import datetime

class ReadingBase(BaseModel):
    sensor: str
    data: Dict[str, Any]
    date: datetime

class ReadingCreate(ReadingBase):
    pass

class ReadingResponse(ReadingBase):
    id_reading: int

    model_config = {
    "from_attributes": True
    }