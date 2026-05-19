from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.product_material import ProductMaterial
from app.schemas.product import ProductCreate
from app.schemas.product_cost import (
    ProductMaterialCostLineResponse,
    ProductMaterialCostResponse,
)


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


def get_product_material_cost(
    db: Session,
    product_id: int,
) -> ProductMaterialCostResponse | None:
    product = db.get(Product, product_id)
    if product is None:
        return None

    statement = (
        select(ProductMaterial)
        .where(ProductMaterial.product_id == product_id)
        .order_by(ProductMaterial.id.asc())
    )
    product_materials = list(db.execute(statement).scalars().all())

    lines: list[ProductMaterialCostLineResponse] = []
    total_cost = 0.0

    for product_material in product_materials:
        unit_cost = product_material.material.unit_cost
        line_cost = product_material.quantity * unit_cost
        total_cost += line_cost

        lines.append(
            ProductMaterialCostLineResponse(
                material_id=product_material.material_id,
                quantity=product_material.quantity,
                unit_cost=unit_cost,
                line_cost=line_cost,
            )
        )

    return ProductMaterialCostResponse(
        product_id=product_id,
        material_cost=total_cost,
        lines=lines,
    )