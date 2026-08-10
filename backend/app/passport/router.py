"""Public passport routes (no auth)."""

from uuid import UUID

from fastapi import APIRouter, Query, Request
from fastapi.responses import Response

from app.auth.deps import AppSettings, DbSession, FileStorage
from app.core.storage import storage_response
from app.passport import service as passport_service
from app.schemas.passport import PublicPassportResponse

router = APIRouter(prefix="/passport", tags=["passport"])


@router.get("/{public_uuid}", response_model=PublicPassportResponse)
def get_passport(
    public_uuid: UUID,
    request: Request,
    db: DbSession,
    settings: AppSettings,
    src: str | None = Query(
        default=None,
        description="Pass src=qr when the visitor came from a QR code.",
    ),
    version: int | None = Query(
        default=None,
        ge=1,
        description="Optional historical version; default is the active passport.",
    ),
) -> PublicPassportResponse:
    """Public product passport. Writes a qr_scans row only when src=qr."""
    return passport_service.get_public_passport_and_track(
        db,
        public_uuid,
        settings=settings,
        request=request,
        src=src,
        version=version,
    )


@router.get("/{public_uuid}/pdf")
def download_passport_pdf(
    public_uuid: UUID,
    db: DbSession,
    settings: AppSettings,
    storage: FileStorage,
    version: int | None = Query(default=None, ge=1),
) -> Response:
    """Download a passport PDF (cached after publish via BackgroundTasks)."""
    pdf_bytes, filename = passport_service.get_or_build_passport_pdf(
        db,
        public_uuid,
        settings=settings,
        storage=storage,
        version=version,
    )
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)


@router.get("/{public_uuid}/certifications/{certification_id}/file")
def public_cert_file(
    public_uuid: UUID,
    certification_id: UUID,
    db: DbSession,
    storage: FileStorage,
) -> Response:
    row = passport_service.resolve_public_cert_file(db, public_uuid, certification_id)
    return storage_response(
        storage,
        row.pdf_path,
        filename=f"{certification_id}.pdf",
        media_type="application/pdf",
        product_id=row.product_id,
    )


@router.get("/{public_uuid}/documents/{document_id}/file")
def public_document_file(
    public_uuid: UUID,
    document_id: UUID,
    db: DbSession,
    storage: FileStorage,
) -> Response:
    row = passport_service.resolve_public_document(db, public_uuid, document_id)
    return storage_response(
        storage,
        row.file_path,
        filename=row.original_filename,
        media_type="application/pdf",
        product_id=row.product_id,
    )


@router.get("/{public_uuid}/images/{image_id}/file")
def public_image_file(
    public_uuid: UUID,
    image_id: UUID,
    db: DbSession,
    storage: FileStorage,
) -> Response:
    row = passport_service.resolve_public_image(db, public_uuid, image_id)
    return storage_response(
        storage,
        row.file_path,
        filename=f"{image_id}",
        product_id=row.product_id,
    )
