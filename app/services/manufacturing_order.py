from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.manufacturing_order import ManufacturingOrder
from app.models.product import Product
from app.models.product_material import ProductMaterial
from app.schemas.manufacturing_order import ManufacturingOrderCreate
from app.schemas.material_requirements import (
    ManufacturingOrderMaterialRequirementLineResponse,
    ManufacturingOrderMaterialRequirementsResponse,
)


class CustomerNotFoundError(Exception):
    pass


class ProductNotFoundError(Exception):
    pass


class ManufacturingOrderReferenceAlreadyExistsError(Exception):
    pass


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