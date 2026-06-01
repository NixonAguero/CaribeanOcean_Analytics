from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.controllers.schemas.revenue import (
    MonthlyRevenueSchema,
    OfferRevenueSchema,
    RevenueKPIsResponse,
    RoomTypeRevenueSchema,
)
from app.adapters.db.repositories.revenue_repository import SQLServerRevenueRepository
from app.application.use_cases.get_revenue_by_month import GetRevenueByMonthUseCase
from app.application.use_cases.get_revenue_by_offer import GetRevenueByOfferUseCase
from app.application.use_cases.get_revenue_by_room_type import GetRevenueByRoomTypeUseCase
from app.application.use_cases.get_revenue_kpis import GetRevenueKPIsUseCase
from app.domain.exceptions import InvalidDateRangeError
from app.infrastructure.database import get_db

router = APIRouter(prefix="/revenue", tags=["revenue"])


def build_kpis_use_case(db: AsyncSession = Depends(get_db)):
    return GetRevenueKPIsUseCase(SQLServerRevenueRepository(db))


def build_by_month_use_case(db: AsyncSession = Depends(get_db)):
    return GetRevenueByMonthUseCase(SQLServerRevenueRepository(db))


def build_by_room_type_use_case(db: AsyncSession = Depends(get_db)):
    return GetRevenueByRoomTypeUseCase(SQLServerRevenueRepository(db))


def build_by_offer_use_case(db: AsyncSession = Depends(get_db)):
    return GetRevenueByOfferUseCase(SQLServerRevenueRepository(db))


@router.get("/kpis", response_model=RevenueKPIsResponse)
async def get_revenue_kpis(
    date_from: date = Query(..., description="Fecha inicio YYYY-MM-DD"),
    date_to: date = Query(..., description="Fecha fin YYYY-MM-DD"),
    use_case: GetRevenueKPIsUseCase = Depends(build_kpis_use_case),
):
    try:
        result = await use_case.execute(date_from, date_to)
        return RevenueKPIsResponse(
            total_revenue=result.total_revenue,
            avg_night_price=result.avg_night_price,
            total_reservations=result.total_reservations,
            avg_revenue_per_reservation=result.avg_revenue_per_reservation,
            date_from=result.date_from,
            date_to=result.date_to,
        )
    except InvalidDateRangeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/by-month", response_model=list[MonthlyRevenueSchema])
async def get_revenue_by_month(
    date_from: date = Query(...),
    date_to: date = Query(...),
    use_case: GetRevenueByMonthUseCase = Depends(build_by_month_use_case),
):
    try:
        results = await use_case.execute(date_from, date_to)
        return [
            MonthlyRevenueSchema(
                year=r.year,
                month=r.month,
                month_label=r.month_label,
                total=r.total,
            )
            for r in results
        ]
    except InvalidDateRangeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/by-room-type", response_model=list[RoomTypeRevenueSchema])
async def get_revenue_by_room_type(
    date_from: date = Query(...),
    date_to: date = Query(...),
    use_case: GetRevenueByRoomTypeUseCase = Depends(build_by_room_type_use_case),
):
    try:
        results = await use_case.execute(date_from, date_to)
        return [RoomTypeRevenueSchema(room_type=r.room_type, total=r.total) for r in results]
    except InvalidDateRangeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/by-offer", response_model=list[OfferRevenueSchema])
async def get_revenue_by_offer(
    date_from: date = Query(...),
    date_to: date = Query(...),
    use_case: GetRevenueByOfferUseCase = Depends(build_by_offer_use_case),
):
    try:
        results = await use_case.execute(date_from, date_to)
        return [
            OfferRevenueSchema(
                offer_name=r.offer_name,
                total=r.total,
                reservations_count=r.reservations_count,
            )
            for r in results
        ]
    except InvalidDateRangeError as e:
        raise HTTPException(status_code=400, detail=str(e))
