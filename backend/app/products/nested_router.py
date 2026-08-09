"""Nested product routes: materials, sustainability, certs, docs, images."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, File, Form, Response, UploadFile, status

from app.auth.deps import DbSession, FileStorage, RequireEditorOrAdmin
from app.core.enums import DocumentType, ImageType
from app.core.storage import storage_response
from app.products import certifications as certs_service
from app.products import materials as materials_service
from app.products import media as media_service
from app.products import sustainability as sustainability_service
from app.schemas.certifications import (
    CertificationCreate,
    CertificationResponse,
    CertificationUpdate,
    LookupResponse,
)
from app.schemas.materials import MaterialCreate, MaterialResponse, MaterialUpdate
from app.schemas.media import DocumentResponse, ImageResponse
from app.schemas.sustainability import SustainabilityResponse, SustainabilityUpsert

router = APIRouter()


# --- lookups (used by cert forms) ---


@router.get(
    "/certification-types",
    response_model=list[LookupResponse],
    tags=["lookups"],
)
def list_certification_types(
    db: DbSession,
    _: RequireEditorOrAdmin,
) -> list[LookupResponse]:
    rows = certs_service.list_certification_types(db)
    return [LookupResponse.model_validate(r) for r in rows]


@router.get(
    "/issuing-authorities",
    response_model=list[LookupResponse],
    tags=["lookups"],
)
def list_issuing_authorities(
    db: DbSession,
    _: RequireEditorOrAdmin,
) -> list[LookupResponse]:
    rows = certs_service.list_issuing_authorities(db)
    return [LookupResponse.model_validate(r) for r in rows]


# --- materials ---


@router.get(
    "/{product_id}/materials",
    response_model=list[MaterialResponse],
    tags=["materials"],
)
def list_materials(
    product_id: UUID,
    db: DbSession,
    _: RequireEditorOrAdmin,
) -> list[MaterialResponse]:
    rows = materials_service.list_materials(db, product_id)
    return [MaterialResponse.model_validate(r) for r in rows]


@router.post(
    "/{product_id}/materials",
    response_model=MaterialResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["materials"],
)
def create_material(
    product_id: UUID,
    body: MaterialCreate,
    db: DbSession,
    _: RequireEditorOrAdmin,
) -> MaterialResponse:
    row = materials_service.create_material(db, product_id, data=body)
    return MaterialResponse.model_validate(row)


@router.patch(
    "/{product_id}/materials/{material_id}",
    response_model=MaterialResponse,
    tags=["materials"],
)
def update_material(
    product_id: UUID,
    material_id: UUID,
    body: MaterialUpdate,
    db: DbSession,
    _: RequireEditorOrAdmin,
) -> MaterialResponse:
    row = materials_service.update_material(
        db, product_id, material_id, data=body
    )
    return MaterialResponse.model_validate(row)


@router.delete(
    "/{product_id}/materials/{material_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["materials"],
)
def delete_material(
    product_id: UUID,
    material_id: UUID,
    db: DbSession,
    _: RequireEditorOrAdmin,
) -> None:
    materials_service.delete_material(db, product_id, material_id)


# --- sustainability ---


@router.get(
    "/{product_id}/sustainability",
    response_model=SustainabilityResponse,
    tags=["sustainability"],
)
def get_sustainability(
    product_id: UUID,
    db: DbSession,
    _: RequireEditorOrAdmin,
) -> SustainabilityResponse:
    row = sustainability_service.get_sustainability(db, product_id)
    return SustainabilityResponse.model_validate(row)


@router.put(
    "/{product_id}/sustainability",
    response_model=SustainabilityResponse,
    tags=["sustainability"],
)
def upsert_sustainability(
    product_id: UUID,
    body: SustainabilityUpsert,
    db: DbSession,
    _: RequireEditorOrAdmin,
) -> SustainabilityResponse:
    row = sustainability_service.upsert_sustainability(db, product_id, data=body)
    return SustainabilityResponse.model_validate(row)


@router.delete(
    "/{product_id}/sustainability",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["sustainability"],
)
def delete_sustainability(
    product_id: UUID,
    db: DbSession,
    _: RequireEditorOrAdmin,
) -> None:
    sustainability_service.delete_sustainability(db, product_id)


# --- certifications ---


@router.get(
    "/{product_id}/certifications",
    response_model=list[CertificationResponse],
    tags=["certifications"],
)
def list_certifications(
    product_id: UUID,
    db: DbSession,
    _: RequireEditorOrAdmin,
) -> list[CertificationResponse]:
    rows = certs_service.list_certifications(db, product_id)
    return [CertificationResponse.model_validate(r) for r in rows]


@router.post(
    "/{product_id}/certifications",
    response_model=CertificationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["certifications"],
)
def create_certification(
    product_id: UUID,
    db: DbSession,
    storage: FileStorage,
    _: RequireEditorOrAdmin,
    certification_type_id: UUID = Form(...),
    issuing_authority_id: UUID = Form(...),
    issue_date: date = Form(...),
    expiration_date: date | None = Form(None),
    pdf: UploadFile = File(...),
) -> CertificationResponse:
    data = CertificationCreate(
        certification_type_id=certification_type_id,
        issuing_authority_id=issuing_authority_id,
        issue_date=issue_date,
        expiration_date=expiration_date,
    )
    row = certs_service.create_certification(
        db, product_id, data=data, pdf=pdf, storage=storage
    )
    return CertificationResponse.model_validate(row)


@router.patch(
    "/{product_id}/certifications/{certification_id}",
    response_model=CertificationResponse,
    tags=["certifications"],
)
def update_certification(
    product_id: UUID,
    certification_id: UUID,
    db: DbSession,
    storage: FileStorage,
    _: RequireEditorOrAdmin,
    certification_type_id: UUID | None = Form(None),
    issuing_authority_id: UUID | None = Form(None),
    issue_date: date | None = Form(None),
    expiration_date: date | None = Form(None),
    pdf: UploadFile | None = File(None),
) -> CertificationResponse:
    data = CertificationUpdate(
        certification_type_id=certification_type_id,
        issuing_authority_id=issuing_authority_id,
        issue_date=issue_date,
        expiration_date=expiration_date,
    )
    # Drop unset form fields so we don't overwrite with None accidentally
    payload = CertificationUpdate.model_validate(
        {k: v for k, v in data.model_dump().items() if v is not None}
    )
    row = certs_service.update_certification(
        db,
        product_id,
        certification_id,
        data=payload,
        pdf=pdf,
        storage=storage,
    )
    return CertificationResponse.model_validate(row)


@router.delete(
    "/{product_id}/certifications/{certification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["certifications"],
)
def delete_certification(
    product_id: UUID,
    certification_id: UUID,
    db: DbSession,
    storage: FileStorage,
    _: RequireEditorOrAdmin,
) -> None:
    certs_service.delete_certification(
        db, product_id, certification_id, storage=storage
    )


@router.get(
    "/{product_id}/certifications/{certification_id}/file",
    tags=["certifications"],
)
def download_certification_pdf(
    product_id: UUID,
    certification_id: UUID,
    db: DbSession,
    storage: FileStorage,
    _: RequireEditorOrAdmin,
) -> Response:
    row = certs_service.get_certification(db, product_id, certification_id)
    return storage_response(
        storage,
        row.pdf_path,
        filename=f"{certification_id}.pdf",
        media_type="application/pdf",
    )


# --- documents ---


@router.get(
    "/{product_id}/documents",
    response_model=list[DocumentResponse],
    tags=["documents"],
)
def list_documents(
    product_id: UUID,
    db: DbSession,
    _: RequireEditorOrAdmin,
) -> list[DocumentResponse]:
    rows = media_service.list_documents(db, product_id)
    return [DocumentResponse.model_validate(r) for r in rows]


@router.post(
    "/{product_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["documents"],
)
def create_document(
    product_id: UUID,
    db: DbSession,
    storage: FileStorage,
    _: RequireEditorOrAdmin,
    doc_type: DocumentType = Form(...),
    file: UploadFile = File(...),
) -> DocumentResponse:
    row = media_service.create_document(
        db, product_id, doc_type=doc_type, file=file, storage=storage
    )
    return DocumentResponse.model_validate(row)


@router.delete(
    "/{product_id}/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["documents"],
)
def delete_document(
    product_id: UUID,
    document_id: UUID,
    db: DbSession,
    storage: FileStorage,
    _: RequireEditorOrAdmin,
) -> None:
    media_service.delete_document(db, product_id, document_id, storage=storage)


@router.get(
    "/{product_id}/documents/{document_id}/file",
    tags=["documents"],
)
def download_document(
    product_id: UUID,
    document_id: UUID,
    db: DbSession,
    storage: FileStorage,
    _: RequireEditorOrAdmin,
) -> Response:
    row = media_service.get_document(db, product_id, document_id)
    return storage_response(
        storage,
        row.file_path,
        filename=row.original_filename,
        media_type="application/pdf",
    )


# --- images ---


@router.get(
    "/{product_id}/images",
    response_model=list[ImageResponse],
    tags=["images"],
)
def list_images(
    product_id: UUID,
    db: DbSession,
    _: RequireEditorOrAdmin,
) -> list[ImageResponse]:
    rows = media_service.list_images(db, product_id)
    return [ImageResponse.model_validate(r) for r in rows]


@router.post(
    "/{product_id}/images",
    response_model=ImageResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["images"],
)
def create_image(
    product_id: UUID,
    db: DbSession,
    storage: FileStorage,
    _: RequireEditorOrAdmin,
    image_type: ImageType = Form(...),
    file: UploadFile = File(...),
    sort_order: int = Form(0),
) -> ImageResponse:
    row = media_service.create_image(
        db,
        product_id,
        image_type=image_type,
        file=file,
        sort_order=sort_order,
        storage=storage,
    )
    return ImageResponse.model_validate(row)


@router.delete(
    "/{product_id}/images/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["images"],
)
def delete_image(
    product_id: UUID,
    image_id: UUID,
    db: DbSession,
    storage: FileStorage,
    _: RequireEditorOrAdmin,
) -> None:
    media_service.delete_image(db, product_id, image_id, storage=storage)


@router.get(
    "/{product_id}/images/{image_id}/file",
    tags=["images"],
)
def download_image(
    product_id: UUID,
    image_id: UUID,
    db: DbSession,
    storage: FileStorage,
    _: RequireEditorOrAdmin,
) -> Response:
    row = media_service.get_image(db, product_id, image_id)
    return storage_response(storage, row.file_path, filename=f"{image_id}")
