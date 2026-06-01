from abc import ABC, abstractmethod
from datetime import date

from app.domain.entities.revenue import MonthlyRevenue
from app.domain.exceptions import InvalidDateRangeError


class RevenueByMonthRepositoryInterface(ABC):
    @abstractmethod
    async def get_revenue_by_month(
        self, date_from: date, date_to: date
    ) -> list[MonthlyRevenue]: ...


class GetRevenueByMonthUseCase:
    def __init__(self, repo: RevenueByMonthRepositoryInterface):
        self.repo = repo

    async def execute(self, date_from: date, date_to: date) -> list[MonthlyRevenue]:
        if date_from > date_to:
            raise InvalidDateRangeError()

        return await self.repo.get_revenue_by_month(date_from, date_to)
