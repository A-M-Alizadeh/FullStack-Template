"""Public passport routes (no auth)."""

from uuid import UUID

from fastapi import APIRouter, Query, Request
from fastapi.responses import FileResponse

from app.auth.deps import AppSettings, DbSession, FileStorage
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
) -> PublicPassportResponse:
    """Public product passport. Writes a qr_scans row only when src=qr."""
    return passport_service.get_public_passport_and_track(
        db,
        public_uuid,
        settings=settings,
        request=request,
        src=src,
    )


@router.get("/{public_uuid}/certifications/{certification_id}/file")
def public_cert_file(
    public_uuid: UUID,
    certification_id: UUID,
    db: DbSession,
    storage: FileStorage,
) -> FileResponse:
    row = passport_service.resolve_public_cert_file(db, public_uuid, certification_id)
    path = storage.path(row.pdf_path)
    return FileResponse(path, filename=path.name, media_type="application/pdf")


@router.get("/{public_uuid}/documents/{document_id}/file")
def public_document_file(
    public_uuid: UUID,
    document_id: UUID,
    db: DbSession,
    storage: FileStorage,
) -> FileResponse:
    row = passport_service.resolve_public_document(db, public_uuid, document_id)
    path = storage.path(row.file_path)
    return FileResponse(
        path, filename=row.original_filename, media_type="application/pdf"
    )


@router.get("/{public_uuid}/images/{image_id}/file")
def public_image_file(
    public_uuid: UUID,
    image_id: UUID,
    db: DbSession,
    storage: FileStorage,
) -> FileResponse:
    row = passport_service.resolve_public_image(db, public_uuid, image_id)
    path = storage.path(row.file_path)
    return FileResponse(path, filename=path.name)
