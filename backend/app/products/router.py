"""Product HTTP routes."""

from uuid import UUID

from fastapi import APIRouter, Query, status

from app.auth.deps import DbSession, RequireEditorOrAdmin
from app.products import service as products_service
from app.products.nested_router import router as nested_router
from app.schemas.products import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])
router.include_router(nested_router)


@router.get("", response_model=list[ProductResponse])
def list_products(
    db: DbSession,
    _: RequireEditorOrAdmin,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> list[ProductResponse]:
    return products_service.list_products(db, skip=skip, limit=limit)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    body: ProductCreate,
    db: DbSession,
    user: RequireEditorOrAdmin,
) -> ProductResponse:
    return products_service.create_product(db, data=body, user=user)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: UUID,
    db: DbSession,
    _: RequireEditorOrAdmin,
) -> ProductResponse:
    return products_service.get_product_response(db, product_id)


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: UUID,
    body: ProductUpdate,
    db: DbSession,
    _: RequireEditorOrAdmin,
) -> ProductResponse:
    return products_service.update_product(db, product_id, data=body)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: UUID,
    db: DbSession,
    _: RequireEditorOrAdmin,
) -> None:
    products_service.delete_product(db, product_id)
