from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.material import MaterialCreate, MaterialResponse
from app.services.material import (
    MaterialSkuAlreadyExistsError,
    create_material,
    get_material_by_id,
    list_materials,
)

router = APIRouter(prefix="/materials", tags=["Materials"])


@router.post("/", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
def create_material_endpoint(
    data: MaterialCreate,
    db: Session = Depends(get_db),
) -> MaterialResponse:
    try:
        return create_material(db, data)
    except MaterialSkuAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail="Material SKU already exists") from exc


@router.get("/", response_model=list[MaterialResponse])
def list_materials_endpoint(
    db: Session = Depends(get_db),
) -> list[MaterialResponse]:
    return list_materials(db)


@router.get("/{material_id}", response_model=MaterialResponse)
def get_material_endpoint(
    material_id: int,
    db: Session = Depends(get_db),
) -> MaterialResponse:
    material = get_material_by_id(db, material_id)
    if material is None:
        raise HTTPException(status_code=404, detail="Material not found")
    return material