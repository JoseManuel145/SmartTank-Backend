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
@router.get("/ph", response_model=ReadingResponse, status_code=status.HTTP_200_OK)
def get_last_ph_reading(
    service: SensorService = Depends(get_sensor_service)
):
    try:
        return service.get_last_ph_reading()
    except ValueError:
        raise HTTPException(status_code=404, detail="No readings found for pH sensor")
    
@router.get("/turbidity", response_model=ReadingResponse, status_code=status.HTTP_200_OK)
def get_last_turbidity_reading(
    service: SensorService = Depends(get_sensor_service)
):
    try:
        return service.get_last_turbidity_reading()
    except ValueError:
        raise HTTPException(status_code=404, detail="No readings found for turbidity sensor")

@router.get("/conductivity", response_model=ReadingResponse, status_code=status.HTTP_200_OK)
def get_last_conductivity_reading(
    service: SensorService = Depends(get_sensor_service)
):
    try:
        return service.get_last_conductivity_reading()
    except ValueError:
        raise HTTPException(status_code=404, detail="No readings found for conductivity sensor")

# Ruta para evaluar la calidad del agua
@router.websocket("/water-quality")
async def websocket_water_quality(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Espera a que el cliente envíe un mensaje (puede ser cualquier texto)
            await websocket.receive_text()
            # Calcula la calidad del agua y la envía al cliente
            result = get_sensor_service().evaluate_water_quality()
            await websocket.send_json(result.model_dump())
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.websocket("/water-bomb")
async def websocket_water_bomb(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
            bomb = get_sensor_service().get_readings_water_bomb()
            await websocket.send_json(bomb.model_dump())
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.websocket("/water-float")
async def websocket_float(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
            flotador = get_sensor_service().get_readings_float()
            await websocket.send_json(flotador.model_dump())
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        
@router.websocket("/ws")
async def websocket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)