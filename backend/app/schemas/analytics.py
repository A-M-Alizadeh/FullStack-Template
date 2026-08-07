"""Analytics shapes."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProductScanStat(BaseModel):
    product_id: UUID
    name: str
    sku: str
    scan_count: int


class LatestScan(BaseModel):
    scanned_at: datetime
    product_id: UUID
    product_name: str
    sku: str
    country: str
    browser: str
    operating_system: str


class AnalyticsResponse(BaseModel):
    scans_today: int
    scans_this_week: int
    most_viewed_products: list[ProductScanStat]
    latest_scans: list[LatestScan]
