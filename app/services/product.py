from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate


class ProductSkuAlreadyExistsError(Exception):
    pass


def create_product(db: Session, data: ProductCreate) -> Product:
    product = Product(
        sku=data.sku,
        name=data.name,
        description=data.description,
        unit=data.unit.value,
        width=data.width,
        height=data.height,
        depth=data.depth,
    )
    db.add(product)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ProductSkuAlreadyExistsError from exc

    db.refresh(product)
    return product


def list_products(db: Session) -> list[Product]:
    statement = select(Product).order_by(Product.id.asc())
    return list(db.execute(statement).scalars().all())


def get_product_by_id(db: Session, product_id: int) -> Product | None:
    statement = select(Product).where(Product.id == product_id)
    return db.execute(statement).scalars().first()