from dataclasses import dataclass
from datetime import date


@dataclass
class DailyOccupancy:
    date: date
    occupied_rooms: int
    total_rooms: int
    occupancy_rate: float


@dataclass
class OccupancyForecastPoint:
    date: date
    predicted_occupied_rooms: int
    total_rooms: int
    predicted_occupancy_rate: float
    confidence: float


@dataclass
class OccupancyForecast:
    model_name: str
    history_date_from: date
    history_date_to: date
    forecast_days: int
    avg_historical_occupancy_rate: float
    avg_predicted_occupancy_rate: float
    peak_predicted_date: date | None
    peak_predicted_occupancy_rate: float
    historical: list[DailyOccupancy]
    forecast: list[OccupancyForecastPoint]
