from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.controllers.schemas.occupancy import (
    DailyOccupancySchema,
    OccupancyForecastPointSchema,
    OccupancyForecastResponse,
)
from app.adapters.db.repositories.occupancy_repository import SQLServerOccupancyRepository
from app.application.use_cases.get_occupancy_forecast import GetOccupancyForecastUseCase
from app.domain.entities.occupancy import OccupancyForecast
from app.domain.exceptions import InvalidDateRangeError, InvalidForecastHorizonError
from app.infrastructure.database import get_db

router = APIRouter(prefix="/occupancy", tags=["occupancy"])


def build_occupancy_forecast_use_case(db: AsyncSession = Depends(get_db)):
    return GetOccupancyForecastUseCase(SQLServerOccupancyRepository(db))


@router.get("/forecast", response_model=OccupancyForecastResponse)
async def get_occupancy_forecast(
    date_from: date = Query(..., description="Fecha inicio historica YYYY-MM-DD"),
    date_to: date = Query(..., description="Fecha fin historica YYYY-MM-DD"),
    forecast_days: int = Query(30, ge=1, le=365),
    use_case: GetOccupancyForecastUseCase = Depends(build_occupancy_forecast_use_case),
):
    return await _execute_forecast(date_from, date_to, forecast_days, use_case)


@router.get("/dashboard", response_model=OccupancyForecastResponse)
async def get_occupancy_dashboard(
    date_from: date = Query(..., description="Fecha inicio historica YYYY-MM-DD"),
    date_to: date = Query(..., description="Fecha fin historica YYYY-MM-DD"),
    forecast_days: int = Query(30, ge=1, le=365),
    use_case: GetOccupancyForecastUseCase = Depends(build_occupancy_forecast_use_case),
):
    return await _execute_forecast(date_from, date_to, forecast_days, use_case)


async def _execute_forecast(
    date_from: date,
    date_to: date,
    forecast_days: int,
    use_case: GetOccupancyForecastUseCase,
) -> OccupancyForecastResponse:
    try:
        result = await use_case.execute(date_from, date_to, forecast_days)
        return _to_response(result)
    except (InvalidDateRangeError, InvalidForecastHorizonError) as error:
        raise HTTPException(status_code=400, detail=str(error))


def _to_response(result: OccupancyForecast) -> OccupancyForecastResponse:
    return OccupancyForecastResponse(
        model_name=result.model_name,
        history_date_from=result.history_date_from,
        history_date_to=result.history_date_to,
        forecast_days=result.forecast_days,
        avg_historical_occupancy_rate=result.avg_historical_occupancy_rate,
        avg_predicted_occupancy_rate=result.avg_predicted_occupancy_rate,
        peak_predicted_date=result.peak_predicted_date,
        peak_predicted_occupancy_rate=result.peak_predicted_occupancy_rate,
        historical=[
            DailyOccupancySchema(
                date=point.date,
                occupied_rooms=point.occupied_rooms,
                total_rooms=point.total_rooms,
                occupancy_rate=point.occupancy_rate,
            )
            for point in result.historical
        ],
        forecast=[
            OccupancyForecastPointSchema(
                date=point.date,
                predicted_occupied_rooms=point.predicted_occupied_rooms,
                total_rooms=point.total_rooms,
                predicted_occupancy_rate=point.predicted_occupancy_rate,
                confidence=point.confidence,
            )
            for point in result.forecast
        ],
    )
