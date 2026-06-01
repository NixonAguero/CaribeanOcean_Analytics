from abc import ABC, abstractmethod
from datetime import date

from app.domain.entities.revenue import RoomTypeRevenue
from app.domain.exceptions import InvalidDateRangeError


class RevenueByRoomTypeRepositoryInterface(ABC):
    @abstractmethod
    async def get_revenue_by_room_type(
        self, date_from: date, date_to: date
    ) -> list[RoomTypeRevenue]: ...


class GetRevenueByRoomTypeUseCase:
    def __init__(self, repo: RevenueByRoomTypeRepositoryInterface):
        self.repo = repo

    async def execute(self, date_from: date, date_to: date) -> list[RoomTypeRevenue]:
        if date_from > date_to:
            raise InvalidDateRangeError()

        return await self.repo.get_revenue_by_room_type(date_from, date_to)
