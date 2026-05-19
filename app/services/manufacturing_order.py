from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.manufacturing_order import ManufacturingOrder
from app.models.product import Product
from app.schemas.manufacturing_order import ManufacturingOrderCreate


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