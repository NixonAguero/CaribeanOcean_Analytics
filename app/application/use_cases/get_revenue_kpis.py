from abc import ABC, abstractmethod
from datetime import date

from app.domain.entities.revenue import RevenueKPIs
from app.domain.exceptions import InvalidDateRangeError


class RevenueKPIsRepositoryInterface(ABC):
    @abstractmethod
    async def get_total_revenue(self, date_from: date, date_to: date) -> float: ...

    @abstractmethod
    async def get_avg_night_price(self, date_from: date, date_to: date) -> float: ...

    @abstractmethod
    async def get_total_reservations(self, date_from: date, date_to: date) -> int: ...


class GetRevenueKPIsUseCase:
    def __init__(self, repo: RevenueKPIsRepositoryInterface):
        self.repo = repo

    async def execute(self, date_from: date, date_to: date) -> RevenueKPIs:
        if date_from > date_to:
            raise InvalidDateRangeError()

        total_revenue = await self.repo.get_total_revenue(date_from, date_to)
        avg_night_price = await self.repo.get_avg_night_price(date_from, date_to)
        total_reservations = await self.repo.get_total_reservations(date_from, date_to)

        return RevenueKPIs(
            total_revenue=total_revenue,
            avg_night_price=avg_night_price,
            total_reservations=total_reservations,
            date_from=date_from,
            date_to=date_to,
        )
