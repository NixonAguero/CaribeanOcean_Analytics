from datetime import date, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.get_occupancy_forecast import (
    OccupancyForecastRepositoryInterface,
)
from app.domain.entities.occupancy import DailyOccupancy


class SQLServerOccupancyRepository(OccupancyForecastRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_daily_occupancy(
        self,
        date_from: date,
        date_to: date,
    ) -> list[DailyOccupancy]:
        total_rooms = await self._get_total_active_rooms()
        occupied_by_date = await self._get_occupied_rooms_by_date(date_from, date_to)

        history: list[DailyOccupancy] = []
        current_date = date_from
        while current_date <= date_to:
            occupied_rooms = occupied_by_date.get(current_date, 0)
            occupancy_rate = (
                round((occupied_rooms / total_rooms) * 100, 2)
                if total_rooms > 0
                else 0
            )
            history.append(
                DailyOccupancy(
                    date=current_date,
                    occupied_rooms=occupied_rooms,
                    total_rooms=total_rooms,
                    occupancy_rate=occupancy_rate,
                )
            )
            current_date += timedelta(days=1)

        return history

    async def _get_total_active_rooms(self) -> int:
        result = await self.db.execute(
            text(
                """
                SELECT COUNT(*) AS total_rooms
                FROM [ROOM]
                WHERE ISNULL(active, 1) = 1
                """
            )
        )
        return int(result.scalar() or 0)

    async def _get_occupied_rooms_by_date(
        self,
        date_from: date,
        date_to: date,
    ) -> dict[date, int]:
        result = await self.db.execute(
            text(
                """
                SELECT
                    CAST(detail.stay_date AS date) AS occupancy_date,
                    COUNT(DISTINCT reservation.id) AS occupied_rooms
                FROM [RESERVATION_NIGHT_DETAIL] detail
                INNER JOIN [RESERVATION] reservation
                    ON reservation.id = detail.reservation_id
                INNER JOIN [ROOM] room
                    ON room.id = reservation.room_id
                WHERE CAST(detail.stay_date AS date) BETWEEN :date_from AND :date_to
                    AND ISNULL(detail.active, 1) = 1
                    AND ISNULL(reservation.active, 1) = 1
                    AND ISNULL(room.active, 1) = 1
                GROUP BY CAST(detail.stay_date AS date)
                ORDER BY occupancy_date
                """
            ),
            {"date_from": date_from, "date_to": date_to},
        )

        occupied_by_date: dict[date, int] = {}
        for row in result.fetchall():
            occupancy_date = row.occupancy_date
            if isinstance(occupancy_date, datetime):
                occupancy_date = occupancy_date.date()

            occupied_by_date[occupancy_date] = int(row.occupied_rooms or 0)

        return occupied_by_date
