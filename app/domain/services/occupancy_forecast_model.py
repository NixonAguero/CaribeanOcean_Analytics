from datetime import timedelta
from math import sqrt

from app.domain.entities.occupancy import DailyOccupancy, OccupancyForecastPoint


class SeasonalTrendOccupancyForecastModel:
    name = "seasonal_trend_v1"

    def forecast(
        self,
        history: list[DailyOccupancy],
        forecast_days: int,
    ) -> list[OccupancyForecastPoint]:
        if not history:
            return []

        total_rooms = history[-1].total_rooms
        if total_rooms <= 0:
            return self._empty_room_forecast(history, forecast_days)

        rates = [point.occupancy_rate for point in history]
        global_avg = self._average(rates)
        recent_avg = self._average(rates[-28:])
        weekday_averages = self._weekday_averages(history, global_avg)
        intercept, slope = self._linear_trend(rates)
        variability = self._standard_deviation(rates)

        forecast: list[OccupancyForecastPoint] = []
        for step in range(1, forecast_days + 1):
            forecast_date = history[-1].date + timedelta(days=step)
            trend_value = intercept + slope * (len(history) - 1 + step)
            weekday_value = weekday_averages[forecast_date.weekday()]
            predicted_rate = self._clamp(
                (weekday_value * 0.50) + (trend_value * 0.30) + (recent_avg * 0.20),
                0,
                100,
            )
            predicted_rooms = round((predicted_rate / 100) * total_rooms)

            forecast.append(
                OccupancyForecastPoint(
                    date=forecast_date,
                    predicted_occupied_rooms=predicted_rooms,
                    total_rooms=total_rooms,
                    predicted_occupancy_rate=round(predicted_rate, 2),
                    confidence=self._confidence(len(history), variability, step),
                )
            )

        return forecast

    def _empty_room_forecast(
        self,
        history: list[DailyOccupancy],
        forecast_days: int,
    ) -> list[OccupancyForecastPoint]:
        return [
            OccupancyForecastPoint(
                date=history[-1].date + timedelta(days=step),
                predicted_occupied_rooms=0,
                total_rooms=0,
                predicted_occupancy_rate=0,
                confidence=0,
            )
            for step in range(1, forecast_days + 1)
        ]

    def _weekday_averages(
        self,
        history: list[DailyOccupancy],
        fallback: float,
    ) -> dict[int, float]:
        weekday_rates: dict[int, list[float]] = {weekday: [] for weekday in range(7)}
        for point in history:
            weekday_rates[point.date.weekday()].append(point.occupancy_rate)

        return {
            weekday: self._average(rates) if rates else fallback
            for weekday, rates in weekday_rates.items()
        }

    def _linear_trend(self, values: list[float]) -> tuple[float, float]:
        if len(values) == 1:
            return values[0], 0

        mean_x = (len(values) - 1) / 2
        mean_y = self._average(values)
        denominator = sum((index - mean_x) ** 2 for index in range(len(values)))
        if denominator == 0:
            return mean_y, 0

        slope = sum(
            (index - mean_x) * (value - mean_y)
            for index, value in enumerate(values)
        ) / denominator
        intercept = mean_y - slope * mean_x
        return intercept, slope

    def _confidence(self, sample_size: int, variability: float, step: int) -> float:
        sample_score = min(0.90, 0.45 + (sample_size / 180) * 0.35)
        variability_penalty = min(0.25, variability / 250)
        horizon_penalty = min(0.35, step * 0.01)
        return round(max(0.10, sample_score - variability_penalty - horizon_penalty), 2)

    def _standard_deviation(self, values: list[float]) -> float:
        if not values:
            return 0

        average = self._average(values)
        variance = self._average([(value - average) ** 2 for value in values])
        return sqrt(variance)

    def _average(self, values: list[float]) -> float:
        if not values:
            return 0
        return sum(values) / len(values)

    def _clamp(self, value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(maximum, value))
