from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.manufacturing_order import (
    ManufacturingOrderCreate,
    ManufacturingOrderResponse,
)
from app.schemas.material_requirements import (
    ManufacturingOrderMaterialRequirementsResponse,
)
from app.services.manufacturing_order import (
    CustomerNotFoundError,
    ManufacturingOrderReferenceAlreadyExistsError,
    ProductNotFoundError,
    create_manufacturing_order,
    get_manufacturing_order_by_id,
    get_manufacturing_order_material_requirements,
    list_manufacturing_orders,
)

router = APIRouter(prefix="/manufacturing-orders", tags=["Manufacturing Orders"])


@router.post(
    "/",
    response_model=ManufacturingOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_manufacturing_order_endpoint(
    data: ManufacturingOrderCreate,
    db: Session = Depends(get_db),
) -> ManufacturingOrderResponse:
    try:
        return create_manufacturing_order(db, data)
    except CustomerNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Customer not found") from exc
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Product not found") from exc
    except ManufacturingOrderReferenceAlreadyExistsError as exc:
        raise HTTPException(
            status_code=409,
            detail="Manufacturing order reference already exists",
        ) from exc


@router.get("/", response_model=list[ManufacturingOrderResponse])
def list_manufacturing_orders_endpoint(
    db: Session = Depends(get_db),
) -> list[ManufacturingOrderResponse]:
    return list_manufacturing_orders(db)


@router.get("/{order_id}", response_model=ManufacturingOrderResponse)
def get_manufacturing_order_endpoint(
    order_id: int,
    db: Session = Depends(get_db),
) -> ManufacturingOrderResponse:
    order = get_manufacturing_order_by_id(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Manufacturing order not found")
    return order


@router.get(
    "/{order_id}/material-requirements",
    response_model=ManufacturingOrderMaterialRequirementsResponse,
)
def get_manufacturing_order_material_requirements_endpoint(
    order_id: int,
    db: Session = Depends(get_db),
) -> ManufacturingOrderMaterialRequirementsResponse:
    requirements = get_manufacturing_order_material_requirements(db, order_id)
    if requirements is None:
        raise HTTPException(status_code=404, detail="Manufacturing order not found")
    return requirements