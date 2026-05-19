from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.material import Material
from app.models.product import Product
from app.models.product_material import ProductMaterial
from app.schemas.product_material import ProductMaterialCreate


class ProductNotFoundError(Exception):
    pass


class MaterialNotFoundError(Exception):
    pass


class ProductMaterialAlreadyExistsError(Exception):
    pass


def create_product_material(
    db: Session,
    data: ProductMaterialCreate,
) -> ProductMaterial:
    product = db.get(Product, data.product_id)
    if product is None:
        raise ProductNotFoundError

    material = db.get(Material, data.material_id)
    if material is None:
        raise MaterialNotFoundError

    product_material = ProductMaterial(
        product_id=data.product_id,
        material_id=data.material_id,
        quantity=data.quantity,
    )
    db.add(product_material)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ProductMaterialAlreadyExistsError from exc

    db.refresh(product_material)
    return product_material


def list_product_materials(db: Session) -> list[ProductMaterial]:
    statement = select(ProductMaterial).order_by(ProductMaterial.id.asc())
    return list(db.execute(statement).scalars().all())


def get_product_material_by_id(
    db: Session,
    product_material_id: int,
) -> ProductMaterial | None:
    statement = select(ProductMaterial).where(ProductMaterial.id == product_material_id)
    return db.execute(statement).scalars().first()