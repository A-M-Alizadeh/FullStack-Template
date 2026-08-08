export interface ProductScanStat {
  product_id: string;
  name: string;
  sku: string;
  scan_count: number;
}

export interface LatestScan {
  scanned_at: string;
  product_id: string;
  product_name: string;
  sku: string;
  country: string;
  browser: string;
  operating_system: string;
}

export interface AnalyticsSummary {
  scans_today: number;
  scans_this_week: number;
  most_viewed_products: ProductScanStat[];
  latest_scans: LatestScan[];
}
