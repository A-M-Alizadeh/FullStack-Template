import type {
  DocumentType,
  ImageType,
  ProductCategory,
  ProductStatus,
} from "./products";

export type PassportStatus = "active" | "revoked";
export type VerificationStatus = "verified" | "unverified";

export interface PassportSummary {
  id: string;
  public_uuid: string;
  version: number;
  status: PassportStatus;
  verification_status: VerificationStatus;
  public_url: string;
  qr_code_url: string;
  created_at: string;
}

export interface PublishResponse {
  product_id: string;
  status: ProductStatus;
  passport: PassportSummary;
}

export interface PassportVersionItem {
  id: string;
  public_uuid: string;
  version: number;
  status: PassportStatus;
  verification_status: VerificationStatus;
  created_at: string;
}

/** Auth-gated QR PNG plus uuid parsed from Content-Disposition. */
export interface ProductQrPayload {
  blob: Blob;
  publicUuid: string;
  filename: string;
}

export interface PublicMaterial {
  name: string;
  percentage: string | number;
  country_of_origin: string;
  recyclable: boolean;
}

export interface PublicSustainability {
  carbon_footprint: string;
  water_consumption: string;
  recycled_material_percent: string | number;
  repairability_score: string | number;
  recyclable: boolean;
}

export interface PublicCertification {
  name: string;
  issuing_authority: string;
  issue_date: string;
  expiration_date: string | null;
  pdf_url: string;
}

export interface PublicDocument {
  doc_type: DocumentType;
  original_filename: string;
  file_url: string;
}

export interface PublicImage {
  id: string;
  image_type: ImageType;
  sort_order: number;
  file_url: string;
}

export interface PublicProduct {
  name: string;
  sku: string;
  serial_number: string;
  category: ProductCategory;
  description: string;
  production_date: string;
  country_of_origin: string;
}

export interface PublicPassport {
  public_uuid: string;
  version: number;
  status: PassportStatus;
  verification_status: VerificationStatus;
  created_at: string;
  product: PublicProduct;
  materials: PublicMaterial[];
  sustainability: PublicSustainability | null;
  certifications: PublicCertification[];
  documents: PublicDocument[];
  images: PublicImage[];
}
