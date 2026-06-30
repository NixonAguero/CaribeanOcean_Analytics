from abc import ABC, abstractmethod
from datetime import date

from app.domain.entities.occupancy import (
    DailyOccupancy,
    OccupancyForecast,
    OccupancyForecastPoint,
)
from app.domain.exceptions import InvalidDateRangeError, InvalidForecastHorizonError
from app.domain.services.occupancy_forecast_model import SeasonalTrendOccupancyForecastModel


class OccupancyForecastRepositoryInterface(ABC):
    @abstractmethod
    async def get_daily_occupancy(
        self,
        date_from: date,
        date_to: date,
    ) -> list[DailyOccupancy]: ...


class GetOccupancyForecastUseCase:
    def __init__(self, repo: OccupancyForecastRepositoryInterface):
        self.repo = repo
        self.model = SeasonalTrendOccupancyForecastModel()

    async def execute(
        self,
        date_from: date,
        date_to: date,
        forecast_days: int,
    ) -> OccupancyForecast:
        if date_from > date_to:
            raise InvalidDateRangeError()
        if forecast_days < 1 or forecast_days > 365:
            raise InvalidForecastHorizonError()

        history = await self.repo.get_daily_occupancy(date_from, date_to)
        forecast = self.model.forecast(history, forecast_days)
        peak_forecast = max(forecast, key=lambda point: point.predicted_occupancy_rate, default=None)

        return OccupancyForecast(
            model_name=self.model.name,
            history_date_from=date_from,
            history_date_to=date_to,
            forecast_days=forecast_days,
            avg_historical_occupancy_rate=self._avg_historical_occupancy(history),
            avg_predicted_occupancy_rate=self._avg_predicted_occupancy(forecast),
            peak_predicted_date=peak_forecast.date if peak_forecast else None,
            peak_predicted_occupancy_rate=(
                peak_forecast.predicted_occupancy_rate if peak_forecast else 0
            ),
            historical=history,
            forecast=forecast,
        )

    def _avg_historical_occupancy(self, history: list[DailyOccupancy]) -> float:
        if not history:
            return 0
        return round(sum(point.occupancy_rate for point in history) / len(history), 2)

    def _avg_predicted_occupancy(self, forecast: list[OccupancyForecastPoint]) -> float:
        if not forecast:
            return 0
        return round(
            sum(point.predicted_occupancy_rate for point in forecast) / len(forecast),
            2,
        )
