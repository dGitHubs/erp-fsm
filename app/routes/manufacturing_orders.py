from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.manufacturing_order import (
    ManufacturingOrderCreate,
    ManufacturingOrderResponse,
)
from app.services.manufacturing_order import (
    CustomerNotFoundError,
    ManufacturingOrderReferenceAlreadyExistsError,
    ProductNotFoundError,
    create_manufacturing_order,
    get_manufacturing_order_by_id,
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


@router.get("/{manufacturing_order_id}", response_model=ManufacturingOrderResponse)
def get_manufacturing_order_endpoint(
    manufacturing_order_id: int,
    db: Session = Depends(get_db),
) -> ManufacturingOrderResponse:
    manufacturing_order = get_manufacturing_order_by_id(db, manufacturing_order_id)
    if manufacturing_order is None:
        raise HTTPException(status_code=404, detail="Manufacturing order not found")
    return manufacturing_order