"""Product HTTP routes."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import FileResponse

from app.auth.deps import AppSettings, DbSession, FileStorage, RequireEditorOrAdmin
from app.core.enums import ProductStatus
from app.passport import service as passport_service
from app.products import service as products_service
from app.products.nested_router import router as nested_router
from app.schemas.passport import PublishResponse
from app.schemas.products import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)

# No default tags on the parent — nested routes keep their own Swagger groups.
router = APIRouter(prefix="/products")
router.include_router(nested_router)


@router.get("", response_model=ProductListResponse, tags=["products"])
def list_products(
    db: DbSession,
    _: RequireEditorOrAdmin,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    q: str | None = Query(None, max_length=100, description="Search name/SKU/serial"),
    status: ProductStatus | None = Query(
        None, description="Filter by draft or published"
    ),
) -> ProductListResponse:
    return products_service.list_products(
        db, skip=skip, limit=limit, q=q, status_filter=status
    )


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["products"],
)
def create_product(
    body: ProductCreate,
    db: DbSession,
    user: RequireEditorOrAdmin,
) -> ProductResponse:
    return products_service.create_product(db, data=body, user=user)


@router.get("/{product_id}", response_model=ProductResponse, tags=["products"])
def get_product(
    product_id: UUID,
    db: DbSession,
    _: RequireEditorOrAdmin,
) -> ProductResponse:
    return products_service.get_product_response(db, product_id)


@router.patch("/{product_id}", response_model=ProductResponse, tags=["products"])
def update_product(
    product_id: UUID,
    body: ProductUpdate,
    db: DbSession,
    _: RequireEditorOrAdmin,
) -> ProductResponse:
    return products_service.update_product(db, product_id, data=body)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["products"],
)
def delete_product(
    product_id: UUID,
    db: DbSession,
    _: RequireEditorOrAdmin,
) -> None:
    products_service.delete_product(db, product_id)


@router.post(
    "/{product_id}/restore",
    response_model=ProductResponse,
    tags=["products"],
)
def restore_product(
    product_id: UUID,
    db: DbSession,
    _: RequireEditorOrAdmin,
) -> ProductResponse:
    return products_service.restore_product(db, product_id)


@router.post(
    "/{product_id}/publish",
    response_model=PublishResponse,
    tags=["publish"],
)
def publish_product(
    product_id: UUID,
    db: DbSession,
    settings: AppSettings,
    storage: FileStorage,
    _: RequireEditorOrAdmin,
) -> PublishResponse:
    return passport_service.publish_product(
        db, product_id, settings=settings, storage=storage
    )


@router.get("/{product_id}/passport/qr", tags=["publish"])
def download_product_qr(
    product_id: UUID,
    db: DbSession,
    storage: FileStorage,
    _: RequireEditorOrAdmin,
) -> FileResponse:
    passport = passport_service.get_passport_for_product(db, product_id)
    if passport is None:
        raise HTTPException(status_code=404, detail="Passport not found")
    path = storage.path(passport.qr_code_path)
    return FileResponse(
        path,
        filename=f"{passport.public_uuid}.png",
        media_type="image/png",
    )
