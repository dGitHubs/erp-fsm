from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.product import ProductCreate, ProductResponse
from app.services.product import (
    ProductSkuAlreadyExistsError,
    create_product,
    get_product_by_id,
    list_products,
)

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product_endpoint(
    data: ProductCreate,
    db: Session = Depends(get_db),
) -> ProductResponse:
    try:
        return create_product(db, data)
    except ProductSkuAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail="Product SKU already exists") from exc


@router.get("/", response_model=list[ProductResponse])
def list_products_endpoint(
    db: Session = Depends(get_db),
) -> list[ProductResponse]:
    return list_products(db)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product_endpoint(
    product_id: int,
    db: Session = Depends(get_db),
) -> ProductResponse:
    product = get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product