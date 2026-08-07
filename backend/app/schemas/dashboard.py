"""Dashboard summary shapes."""

from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_products: int
    published_passports: int
    generated_qr_codes: int
    total_passport_views: int
