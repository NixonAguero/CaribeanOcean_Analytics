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
            text("""
                SELECT ISNULL(SUM(total_amount), 0)
                FROM RESERVATION
                WHERE active = 1
                  AND check_in >= :date_from
                  AND check_in <= :date_to
            """),
            {"date_from": date_from, "date_to": date_to},
        )
        return float(result.scalar() or 0)

    async def get_avg_night_price(self, date_from: date, date_to: date) -> float:
        result = await self.db.execute(
            text("""
                SELECT ISNULL(AVG(rnd.final_night_price), 0)
                FROM RESERVATION_NIGHT_DETAIL rnd
                INNER JOIN RESERVATION r ON rnd.reservation_id = r.id
                WHERE rnd.active = 1
                  AND r.check_in >= :date_from
                  AND r.check_in <= :date_to
            """),
            {"date_from": date_from, "date_to": date_to},
        )
        return float(result.scalar() or 0)

    async def get_total_reservations(self, date_from: date, date_to: date) -> int:
        result = await self.db.execute(
            text("""
                SELECT COUNT(*)
                FROM RESERVATION
                WHERE active = 1
                  AND check_in >= :date_from
                  AND check_in <= :date_to
            """),
            {"date_from": date_from, "date_to": date_to},
        )
        return int(result.scalar() or 0)

    async def get_revenue_by_month(self, date_from: date, date_to: date) -> list[MonthlyRevenue]:
        result = await self.db.execute(
            text("""
                SELECT
                    YEAR(check_in)    AS year,
                    MONTH(check_in)   AS month,
                    SUM(total_amount) AS total
                FROM RESERVATION
                WHERE active = 1
                  AND check_in >= :date_from
                  AND check_in <= :date_to
                GROUP BY YEAR(check_in), MONTH(check_in)
                ORDER BY year, month
            """),
            {"date_from": date_from, "date_to": date_to},
        )
        rows = result.fetchall()
        return [MonthlyRevenue(year=r.year, month=r.month, total=float(r.total)) for r in rows]

    async def get_revenue_by_room_type(
        self, date_from: date, date_to: date
    ) -> list[RoomTypeRevenue]:
        result = await self.db.execute(
            text("""
                SELECT
                    rt.name             AS room_type,
                    SUM(r.total_amount) AS total
                FROM RESERVATION r
                INNER JOIN ROOM      ro ON r.room_id        = ro.id
                INNER JOIN ROOM_TYPE rt ON ro.room_type_id  = rt.id
                WHERE r.active = 1
                  AND r.check_in >= :date_from
                  AND r.check_in <= :date_to
                GROUP BY rt.name
                ORDER BY total DESC
            """),
            {"date_from": date_from, "date_to": date_to},
        )
        rows = result.fetchall()
        return [RoomTypeRevenue(room_type=r.room_type, total=float(r.total)) for r in rows]

    async def get_revenue_by_offer(self, date_from: date, date_to: date) -> list[OfferRevenue]:
        result = await self.db.execute(
            text("""
                SELECT
                    ISNULL(o.name, 'Sin oferta') AS offer_name,
                    SUM(r.total_amount)           AS total,
                    COUNT(r.id)                   AS reservations_count
                FROM RESERVATION r
                LEFT JOIN OFFER o ON r.selected_offer_id = o.id
                WHERE r.active = 1
                  AND r.check_in >= :date_from
                  AND r.check_in <= :date_to
                GROUP BY o.name
                ORDER BY total DESC
            """),
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
