/** Product API shapes aligned with FastAPI. */

export type ProductStatus = "draft" | "published";

export type ProductCategory =
  | "electronics"
  | "textile"
  | "furniture"
  | "food"
  | "automotive"
  | "other";

export const PRODUCT_CATEGORIES = [
  "electronics",
  "textile",
  "furniture",
  "food",
  "automotive",
  "other",
] as const satisfies readonly ProductCategory[];

export interface ProductCoverImage {
  id: string;
  url: string;
}

export interface Product {
  id: string;
  created_by_id: string;
  name: string;
  sku: string;
  serial_number: string;
  category: ProductCategory;
  description: string;
  production_date: string;
  country_of_origin: string;
  status: ProductStatus;
  created_at: string;
  updated_at: string;
  cover_image: ProductCoverImage | null;
}

export interface ProductWrite {
  name: string;
  sku: string;
  serial_number: string;
  category: ProductCategory;
  description: string;
  production_date: string;
  country_of_origin: string;
}

export interface Material {
  id: string;
  product_id: string;
  name: string;
  percentage: string;
  country_of_origin: string;
  recyclable: boolean;
}

export interface MaterialWrite {
  name: string;
  percentage: string;
  country_of_origin: string;
  recyclable: boolean;
}

export interface Sustainability {
  id: string;
  product_id: string;
  carbon_footprint: string;
  water_consumption: string;
  recycled_material_percent: string;
  repairability_score: string;
  recyclable: boolean;
}

export interface SustainabilityWrite {
  carbon_footprint: string;
  water_consumption: string;
  recycled_material_percent: string;
  repairability_score: string;
  recyclable: boolean;
}

export interface LookupItem {
  id: string;
  code: string;
  name: string;
}

export interface Certification {
  id: string;
  product_id: string;
  certification_type_id: string;
  issuing_authority_id: string;
  issue_date: string;
  expiration_date: string | null;
  pdf_path: string;
  certification_type: LookupItem;
  issuing_authority: LookupItem;
}

export type DocumentType =
  | "user_manual"
  | "warranty"
  | "technical_datasheet";

export const DOCUMENT_TYPES = [
  "user_manual",
  "warranty",
  "technical_datasheet",
] as const satisfies readonly DocumentType[];

export interface ProductDocument {
  id: string;
  product_id: string;
  doc_type: DocumentType;
  file_path: string;
  original_filename: string;
}

export type ImageType = "cover" | "gallery";

export const IMAGE_TYPES = ["cover", "gallery"] as const satisfies readonly ImageType[];

export interface ProductImage {
  id: string;
  product_id: string;
  image_type: ImageType;
  file_path: string;
  sort_order: number;
}
