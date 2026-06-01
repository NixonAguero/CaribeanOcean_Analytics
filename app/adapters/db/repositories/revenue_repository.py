from datetime import date

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.get_revenue_by_month import RevenueByMonthRepositoryInterface
from app.application.use_cases.get_revenue_by_offer import RevenueByOfferRepositoryInterface
from app.application.use_cases.get_revenue_by_room_type import RevenueByRoomTypeRepositoryInterface
from app.application.use_cases.get_revenue_kpis import RevenueKPIsRepositoryInterface
from app.domain.entities.revenue import MonthlyRevenue, OfferRevenue, RoomTypeRevenue


class SQLServerRevenueRepository(
    RevenueKPIsRepositoryInterface,
    RevenueByMonthRepositoryInterface,
    RevenueByRoomTypeRepositoryInterface,
    RevenueByOfferRepositoryInterface,
):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_total_revenue(self, date_from: date, date_to: date) -> float:
        result = await self.db.execute(
            text("EXEC sp_GetTotalRevenue @date_from = :date_from, @date_to = :date_to"),
            {"date_from": date_from, "date_to": date_to},
        )
        return float(result.scalar() or 0)

    async def get_avg_night_price(self, date_from: date, date_to: date) -> float:
        result = await self.db.execute(
            text("EXEC sp_GetAvgNightPrice @date_from = :date_from, @date_to = :date_to"),
            {"date_from": date_from, "date_to": date_to},
        )
        return float(result.scalar() or 0)

    async def get_total_reservations(self, date_from: date, date_to: date) -> int:
        result = await self.db.execute(
            text("EXEC sp_GetTotalReservations @date_from = :date_from, @date_to = :date_to"),
            {"date_from": date_from, "date_to": date_to},
        )
        return int(result.scalar() or 0)

    async def get_revenue_by_month(self, date_from: date, date_to: date) -> list[MonthlyRevenue]:
        result = await self.db.execute(
            text("EXEC sp_GetRevenueByMonth @date_from = :date_from, @date_to = :date_to"),
            {"date_from": date_from, "date_to": date_to},
        )
        rows = result.fetchall()
        return [MonthlyRevenue(year=r.year, month=r.month, total=float(r.total)) for r in rows]

    async def get_revenue_by_room_type(
        self, date_from: date, date_to: date
    ) -> list[RoomTypeRevenue]:
        result = await self.db.execute(
            text("EXEC sp_GetRevenueByRoomType @date_from = :date_from, @date_to = :date_to"),
            {"date_from": date_from, "date_to": date_to},
        )
        rows = result.fetchall()
        return [RoomTypeRevenue(room_type=r.room_type, total=float(r.total)) for r in rows]

    async def get_revenue_by_offer(self, date_from: date, date_to: date) -> list[OfferRevenue]:
        result = await self.db.execute(
            text("EXEC sp_GetRevenueByOffer @date_from = :date_from, @date_to = :date_to"),
            {"date_from": date_from, "date_to": date_to},
        )
        rows = result.fetchall()
        return [
            OfferRevenue(
                offer_name=r.offer_name,
                total=float(r.total),
                reservations_count=int(r.reservations_count),
            )
            for r in rows
        ]
