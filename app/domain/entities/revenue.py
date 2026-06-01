# app/domain/entities/revenue.py
from dataclasses import dataclass
from datetime import date


@dataclass
class MonthlyRevenue:
    year: int
    month: int
    total: float

    @property
    def month_label(self) -> str:
        months = [
            "",
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre",
        ]
        return f"{months[self.month]} {self.year}"


@dataclass
class RoomTypeRevenue:
    room_type: str
    total: float


@dataclass
class OfferRevenue:
    offer_name: str
    total: float
    reservations_count: int


@dataclass
class RevenueKPIs:
    total_revenue: float
    avg_night_price: float
    total_reservations: int
    date_from: date
    date_to: date

    @property
    def avg_revenue_per_reservation(self) -> float:
        if self.total_reservations == 0:
            return 0.0
        return round(self.total_revenue / self.total_reservations, 2)
