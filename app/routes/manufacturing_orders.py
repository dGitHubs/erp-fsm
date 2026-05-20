from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.manufacturing_order import (
    ManufacturingOrderCreate,
    ManufacturingOrderResponse,
    ManufacturingOrderStatus,
    ManufacturingOrderStatusUpdate,
)
from app.schemas.material_availability import (
    ManufacturingOrderMaterialAvailabilityResponse,
)
from app.schemas.material_consumption import ManufacturingOrderConsumptionResponse
from app.schemas.material_requirements import (
    ManufacturingOrderMaterialRequirementsResponse,
)
from app.services.manufacturing_order import (
    CustomerNotFoundError,
    InsufficientStockError,
    InvalidStatusTransitionError,
    ManufacturingOrderNotFoundError,
    ManufacturingOrderReferenceAlreadyExistsError,
    OrderNotConsumableError,
    ProductNotFoundError,
    consume_manufacturing_order_materials,
    create_manufacturing_order,
    get_manufacturing_order_by_id,
    get_manufacturing_order_material_availability,
    get_manufacturing_order_material_requirements,
    list_manufacturing_orders,
    update_manufacturing_order_status,
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


@router.get(
    "/{order_id}/material-availability",
    response_model=ManufacturingOrderMaterialAvailabilityResponse,
)
def get_manufacturing_order_material_availability_endpoint(
    order_id: int,
    db: Session = Depends(get_db),
) -> ManufacturingOrderMaterialAvailabilityResponse:
    availability = get_manufacturing_order_material_availability(db, order_id)
    if availability is None:
        raise HTTPException(status_code=404, detail="Manufacturing order not found")
    return availability


@router.post(
    "/{order_id}/consume",
    response_model=ManufacturingOrderConsumptionResponse,
)
def consume_manufacturing_order_materials_endpoint(
    order_id: int,
    db: Session = Depends(get_db),
) -> ManufacturingOrderConsumptionResponse:
    try:
        return consume_manufacturing_order_materials(db, order_id)
    except ManufacturingOrderNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Manufacturing order not found") from exc
    except OrderNotConsumableError as exc:
        raise HTTPException(status_code=409, detail="Order has already been consumed or cancelled") from exc
    except InsufficientStockError as exc:
        raise HTTPException(status_code=409, detail="Insufficient stock to consume materials") from exc


@router.patch("/{order_id}/status", response_model=ManufacturingOrderResponse)
def update_manufacturing_order_status_endpoint(
    order_id: int,
    data: ManufacturingOrderStatusUpdate,
    db: Session = Depends(get_db),
) -> ManufacturingOrderResponse:
    try:
        return update_manufacturing_order_status(db, order_id, data.status)
    except ManufacturingOrderNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Manufacturing order not found") from exc
    except InvalidStatusTransitionError as exc:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot transition order to status '{data.status}'",
        ) from exc