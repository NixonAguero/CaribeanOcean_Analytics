from abc import ABC, abstractmethod
from datetime import date

from app.domain.entities.revenue import OfferRevenue
from app.domain.exceptions import InvalidDateRangeError


class RevenueByOfferRepositoryInterface(ABC):
    @abstractmethod
    async def get_revenue_by_offer(self, date_from: date, date_to: date) -> list[OfferRevenue]: ...


class GetRevenueByOfferUseCase:
    def __init__(self, repo: RevenueByOfferRepositoryInterface):
        self.repo = repo

    async def execute(self, date_from: date, date_to: date) -> list[OfferRevenue]:
        if date_from > date_to:
            raise InvalidDateRangeError()

        return await self.repo.get_revenue_by_offer(date_from, date_to)
