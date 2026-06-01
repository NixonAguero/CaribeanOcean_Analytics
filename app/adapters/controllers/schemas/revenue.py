from datetime import date

from pydantic import BaseModel


class RevenueKPIsResponse(BaseModel):
    total_revenue: float
    avg_night_price: float
    total_reservations: int
    avg_revenue_per_reservation: float
    date_from: date
    date_to: date


class MonthlyRevenueSchema(BaseModel):
    year: int
    month: int
    month_label: str
    total: float


class RoomTypeRevenueSchema(BaseModel):
    room_type: str
    total: float


class OfferRevenueSchema(BaseModel):
    offer_name: str
    total: float
    reservations_count: int
