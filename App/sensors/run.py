import json
import asyncio
import threading
from .repository import SensorRepository
from .service import SensorService
from .schemas import ReadingCreate
from App.core.rabbit import RabbitConsumer
from App.core.mysql import SessionLocal
from App.core.websocket import manager

def serialize_reading(reading_dict):
    # Suponiendo que el campo 'date' es datetime
    if 'date' in reading_dict and hasattr(reading_dict['date'], 'isoformat'):
        reading_dict['date'] = reading_dict['date'].isoformat()
    return reading_dict

def process_message(ch, method, properties, body):
    print(f"[RabbitMQ] Mensaje recibido: {body}")
    try:
        data = json.loads(body)
        db = SessionLocal()
        try:
            repo = SensorRepository(db)
            service = SensorService(repo)
            reading_create = ReadingCreate(**data)
            reading = service.create_reading(reading_create)

            # Serializar la lectura para convertir datetime a string
            reading_dict = reading.model_dump()
            reading_dict = serialize_reading(reading_dict)

            # Envía la lectura por websocket
            asyncio.run(manager.broadcast(reading_dict))
        finally:
            db.close()
    except Exception as e:
        print(f"Error procesando mensaje: {e}")


def start_rabbit_consumer():
    consumer = RabbitConsumer()
    consumer.start_consuming(process_message)

def run():
    thread = threading.Thread(target=start_rabbit_consumer, daemon=True)
    thread.start()
    print("RabbitMQ consumer started in a separate thread.")