from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.product_material import (
    ProductMaterialCreate,
    ProductMaterialResponse,
)
from app.services.product_material import (
    MaterialNotFoundError,
    ProductMaterialAlreadyExistsError,
    ProductNotFoundError,
    create_product_material,
    get_product_material_by_id,
    list_product_materials,
)

router = APIRouter(prefix="/product-materials", tags=["Product Materials"])


@router.post(
    "/",
    response_model=ProductMaterialResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product_material_endpoint(
    data: ProductMaterialCreate,
    db: Session = Depends(get_db),
) -> ProductMaterialResponse:
    try:
        return create_product_material(db, data)
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Product not found") from exc
    except MaterialNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Material not found") from exc
    except ProductMaterialAlreadyExistsError as exc:
        raise HTTPException(
            status_code=409,
            detail="Product material already exists",
        ) from exc


@router.get("/", response_model=list[ProductMaterialResponse])
def list_product_materials_endpoint(
    db: Session = Depends(get_db),
) -> list[ProductMaterialResponse]:
    return list_product_materials(db)


@router.get("/{product_material_id}", response_model=ProductMaterialResponse)
def get_product_material_endpoint(
    product_material_id: int,
    db: Session = Depends(get_db),
) -> ProductMaterialResponse:
    product_material = get_product_material_by_id(db, product_material_id)
    if product_material is None:
        raise HTTPException(status_code=404, detail="Product material not found")
    return product_material