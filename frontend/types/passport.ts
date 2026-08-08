import type { ProductStatus } from "./products";

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

/** Auth-gated QR PNG plus uuid parsed from Content-Disposition. */
export interface ProductQrPayload {
  blob: Blob;
  publicUuid: string;
  filename: string;
}
