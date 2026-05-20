from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.manufacturing_order import ManufacturingOrder
from app.models.product import Product
from app.models.product_material import ProductMaterial
from app.models.stock_movement import MovementType, StockMovement
from app.schemas.manufacturing_order import ManufacturingOrderCreate, ManufacturingOrderStatus
from app.schemas.material_availability import (
    ManufacturingOrderMaterialAvailabilityLineResponse,
    ManufacturingOrderMaterialAvailabilityResponse,
)
from app.schemas.material_consumption import (
    ManufacturingOrderConsumptionResponse,
    MaterialConsumptionLineResponse,
)
from app.schemas.material_requirements import (
    ManufacturingOrderMaterialRequirementLineResponse,
    ManufacturingOrderMaterialRequirementsResponse,
)


class CustomerNotFoundError(Exception):
    pass


class ProductNotFoundError(Exception):
    pass


class ManufacturingOrderNotFoundError(Exception):
    pass


class ManufacturingOrderReferenceAlreadyExistsError(Exception):
    pass


class InsufficientStockError(Exception):
    pass


class OrderNotConsumableError(Exception):
    pass


class InvalidStatusTransitionError(Exception):
    pass


_TERMINAL_STATUSES = {ManufacturingOrderStatus.DONE, ManufacturingOrderStatus.CANCELLED}

_ALLOWED_TRANSITIONS: dict[ManufacturingOrderStatus, set[ManufacturingOrderStatus]] = {
    ManufacturingOrderStatus.DRAFT: {
        ManufacturingOrderStatus.CONFIRMED,
        ManufacturingOrderStatus.CANCELLED,
    },
    ManufacturingOrderStatus.CONFIRMED: {
        ManufacturingOrderStatus.IN_PROGRESS,
        ManufacturingOrderStatus.CANCELLED,
    },
    ManufacturingOrderStatus.IN_PROGRESS: {
        ManufacturingOrderStatus.DONE,
        ManufacturingOrderStatus.CANCELLED,
    },
    ManufacturingOrderStatus.DONE: set(),
    ManufacturingOrderStatus.CANCELLED: set(),
}


def create_manufacturing_order(
    db: Session,
    data: ManufacturingOrderCreate,
) -> ManufacturingOrder:
    customer = db.get(Customer, data.customer_id)
    if customer is None:
        raise CustomerNotFoundError

    product = db.get(Product, data.product_id)
    if product is None:
        raise ProductNotFoundError

    order = ManufacturingOrder(
        reference=data.reference,
        customer_id=data.customer_id,
        product_id=data.product_id,
        quantity=data.quantity,
        description=data.description,
        status=data.status.value,
    )
    db.add(order)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ManufacturingOrderReferenceAlreadyExistsError from exc

    db.refresh(order)
    return order


def list_manufacturing_orders(db: Session) -> list[ManufacturingOrder]:
    statement = select(ManufacturingOrder).order_by(ManufacturingOrder.id.asc())
    return list(db.execute(statement).scalars().all())


def get_manufacturing_order_by_id(
    db: Session,
    order_id: int,
) -> ManufacturingOrder | None:
    statement = select(ManufacturingOrder).where(ManufacturingOrder.id == order_id)
    return db.execute(statement).scalars().first()


def get_manufacturing_order_material_requirements(
    db: Session,
    order_id: int,
) -> ManufacturingOrderMaterialRequirementsResponse | None:
    order = db.get(ManufacturingOrder, order_id)
    if order is None:
        return None

    statement = (
        select(ProductMaterial)
        .where(ProductMaterial.product_id == order.product_id)
        .order_by(ProductMaterial.id.asc())
    )
    product_materials = list(db.execute(statement).scalars().all())

    lines: list[ManufacturingOrderMaterialRequirementLineResponse] = []

    for product_material in product_materials:
        required_quantity = product_material.quantity * order.quantity
        lines.append(
            ManufacturingOrderMaterialRequirementLineResponse(
                material_id=product_material.material_id,
                quantity_per_product=product_material.quantity,
                required_quantity=required_quantity,
            )
        )

    return ManufacturingOrderMaterialRequirementsResponse(
        manufacturing_order_id=order.id,
        product_id=order.product_id,
        order_quantity=order.quantity,
        lines=lines,
    )


def get_manufacturing_order_material_availability(
    db: Session,
    order_id: int,
) -> ManufacturingOrderMaterialAvailabilityResponse | None:
    order = db.get(ManufacturingOrder, order_id)
    if order is None:
        return None

    statement = (
        select(ProductMaterial)
        .where(ProductMaterial.product_id == order.product_id)
        .order_by(ProductMaterial.id.asc())
    )
    product_materials = list(db.execute(statement).scalars().all())

    lines: list[ManufacturingOrderMaterialAvailabilityLineResponse] = []
    can_produce = True

    for product_material in product_materials:
        required_quantity = product_material.quantity * order.quantity
        available_quantity = product_material.material.quantity_on_hand
        missing_quantity = max(required_quantity - available_quantity, 0.0)

        if missing_quantity > 0:
            can_produce = False

        lines.append(
            ManufacturingOrderMaterialAvailabilityLineResponse(
                material_id=product_material.material_id,
                required_quantity=required_quantity,
                available_quantity=available_quantity,
                missing_quantity=missing_quantity,
            )
        )

    return ManufacturingOrderMaterialAvailabilityResponse(
        manufacturing_order_id=order.id,
        product_id=order.product_id,
        order_quantity=order.quantity,
        can_produce=can_produce,
        lines=lines,
    )


def consume_manufacturing_order_materials(
    db: Session,
    order_id: int,
) -> ManufacturingOrderConsumptionResponse:
    order = db.get(ManufacturingOrder, order_id)
    if order is None:
        raise ManufacturingOrderNotFoundError

    if ManufacturingOrderStatus(order.status) in _TERMINAL_STATUSES:
        raise OrderNotConsumableError

    statement = (
        select(ProductMaterial)
        .where(ProductMaterial.product_id == order.product_id)
        .order_by(ProductMaterial.id.asc())
    )
    product_materials = list(db.execute(statement).scalars().all())

    # Verify all materials have sufficient stock before touching anything
    for pm in product_materials:
        required = pm.quantity * order.quantity
        if pm.material.quantity_on_hand < required:
            raise InsufficientStockError

    lines: list[MaterialConsumptionLineResponse] = []

    for pm in product_materials:
        required = pm.quantity * order.quantity
        before = pm.material.quantity_on_hand
        pm.material.quantity_on_hand -= required
        db.add(
            StockMovement(
                material_id=pm.material_id,
                quantity=-required,
                movement_type=MovementType.CONSUMPTION,
                reference=order.reference,
            )
        )
        lines.append(
            MaterialConsumptionLineResponse(
                material_id=pm.material_id,
                quantity_consumed=required,
                quantity_on_hand_before=before,
                quantity_on_hand_after=pm.material.quantity_on_hand,
            )
        )

    order.status = ManufacturingOrderStatus.DONE.value
    db.commit()

    return ManufacturingOrderConsumptionResponse(
        manufacturing_order_id=order.id,
        product_id=order.product_id,
        order_quantity=order.quantity,
        lines=lines,
    )


def update_manufacturing_order_status(
    db: Session,
    order_id: int,
    new_status: ManufacturingOrderStatus,
) -> ManufacturingOrder:
    order = db.get(ManufacturingOrder, order_id)
    if order is None:
        raise ManufacturingOrderNotFoundError

    current = ManufacturingOrderStatus(order.status)
    if new_status not in _ALLOWED_TRANSITIONS[current]:
        raise InvalidStatusTransitionError

    order.status = new_status.value
    db.commit()
    db.refresh(order)
    return order