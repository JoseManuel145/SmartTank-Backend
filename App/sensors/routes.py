from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List
import asyncio

from .schemas import ReadingCreate, ReadingResponse, WaterQualityResponse
from .repository import SensorRepository
from .service import SensorService
from App.core.mysql import get_db
from App.core.websocket import manager

router = APIRouter()

def get_sensor_service(db: Session = Depends(get_db)) -> SensorService:
    repo = SensorRepository(db)
    return SensorService(repo)

@router.get("/", response_model=List[ReadingResponse])
def get_last_readings(
    n: int = 30,
    service: SensorService = Depends(get_sensor_service)
):
    return service.get_last_n_readings(n)

@router.get("/{id_reading}", response_model=ReadingResponse)
def get_reading_by_id(
    id_reading: int,
    service: SensorService = Depends(get_sensor_service)
):
    try:
        return service.get_reading_by_id(id_reading)
    except ValueError:
        raise HTTPException(status_code=404, detail="Reading not found")

@router.post("/", response_model=ReadingResponse, status_code=status.HTTP_201_CREATED)
def create_reading(
    data: ReadingCreate,
    service: SensorService = Depends(get_sensor_service)
):
    reading = service.create_reading(data)
    # Notifica a todos los clientes websocket con la nueva lectura
    asyncio.create_task(manager.broadcast(reading.model_dump()))
    return reading

@router.get("/water-quality", response_model=WaterQualityResponse)
def get_water_quality(
    service: SensorService = Depends(get_sensor_service)
):
    result = service.evaluate_water_quality()
    # Notifica a todos los clientes websocket con la evaluación de calidad del agua
    asyncio.create_task(manager.broadcast(result.model_dump()))
    return result

# Ruta de WebSocket para enviar datos en tiempo real a los clientes
@router.websocket("/values")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Mantiene la conexión abierta
    except WebSocketDisconnect:
            manager.disconnect(websocket)
