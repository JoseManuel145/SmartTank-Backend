from .repository import SensorRepository
from .schemas import ReadingCreate, ReadingResponse, WaterQualityResponse, WaterQualityObservation
from typing import List
from collections import defaultdict

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

    def get_readings_water_bomb(self) -> ReadingResponse:
        reading = self.repo.get_readings_bombs()
        if not reading:
            raise ValueError("No readings found for bomba_agua")
        return ReadingResponse.model_validate(reading)

    def get_readings_float(self) -> ReadingResponse:
        reading = self.repo.get_readings_float()
        if not reading:
            raise ValueError("No readings found for flotador")
        return ReadingResponse.model_validate(reading)

    def get_last_ph_reading(self) -> ReadingResponse:
        reading = self.repo.get_last_ph()
        if not reading:
            raise ValueError("No readings found for pH sensor")
        return ReadingResponse.model_validate(reading)
    
    def get_last_turbidity_reading(self) -> ReadingResponse:
        reading = self.repo.get_last_turbidity()
        if not reading:
            raise ValueError("No readings found for turbidity sensor")
        return ReadingResponse.model_validate(reading)
    
    def get_last_conductivity_reading(self) -> ReadingResponse:
        reading = self.repo.get_last_conductivity()
        if not reading:
            raise ValueError("No readings found for conductivity sensor")
        return ReadingResponse.model_validate(reading)
    
    def evaluate_water_quality(self, n: int = 100) -> WaterQualityResponse:
        # Obtener las últimas n lecturas
        readings = self.repo.get_last_n(n)

        # Agrupar datos por sensor
        sensor_values = defaultdict(list)
        for r in readings:
            sensor_values[r.sensor].append(r.data.get('value', 0))

        observations = []
        points = 0
        total_sensors = 3  # ph, turbidez, conductividad
        max_points = 2 * total_sensors  # 2 puntos por cada sensor

        # Evaluar pH
        ph_values = sensor_values.get('ph', [])
        if ph_values:
            ph_avg = sum(ph_values) / len(ph_values)
            if 6.5 <= ph_avg <= 8.5:
                observations.append(WaterQualityObservation(sensor='ph', status='Normal'))
                points += 2
            elif ph_avg < 6.5 or ph_avg > 8.5:
                observations.append(WaterQualityObservation(sensor='ph', status='Aceptable'))
                points += 1
            else:
                observations.append(WaterQualityObservation(sensor='ph', status='Alto/Bajo'))
        else:
            observations.append(WaterQualityObservation(sensor='ph', status='No data'))

        # Evaluar turbidez
        turbidez_values = sensor_values.get('turbidez', [])
        if turbidez_values:
            turbidez_avg = sum(turbidez_values) / len(turbidez_values)
            if turbidez_avg <= 1:
                observations.append(WaterQualityObservation(sensor='turbidez', status='Perfecta'))
                points += 2
            elif 0 < turbidez_avg <= 5:
                observations.append(WaterQualityObservation(sensor='turbidez', status='Aceptable'))
                points += 1
            else:
                observations.append(WaterQualityObservation(sensor='turbidez', status='Alta'))
        else:
            observations.append(WaterQualityObservation(sensor='turbidez', status='No data'))

        # Evaluar conductividad
        conductividad_values = sensor_values.get('conductividad electrica', [])
        if conductividad_values:
            conductividad_avg = sum(conductividad_values) / len(conductividad_values)
            if 50 <= conductividad_avg <= 1500:
                observations.append(WaterQualityObservation(sensor='conductividad electrica', status='Normal'))
                points += 2
            elif conductividad_avg < 50 or conductividad_avg > 1500:
                observations.append(WaterQualityObservation(sensor='conductividad electrica', status='Aceptable'))
                points += 1
            else:
                observations.append(WaterQualityObservation(sensor='conductividad electrica', status='Alta/Muy baja'))
        else:
            observations.append(WaterQualityObservation(sensor='conductividad electrica', status='No data'))

        # Determinar calidad general
        if points == max_points:
            quality = 'Buena'
        elif points >= max_points * 0.5:
            quality = 'Regular'
        else:
            quality = 'Mala'

        # Calcular valor numérico para frontend (porcentaje más granular)
        quality_value = int((points / max_points) * 100)

        return WaterQualityResponse(
            quality=quality,
            quality_value=quality_value,
            observations=observations
        )
