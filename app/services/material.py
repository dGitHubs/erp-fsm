from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.material import Material
from app.schemas.material import MaterialCreate


class MaterialSkuAlreadyExistsError(Exception):
    pass


def create_material(db: Session, data: MaterialCreate) -> Material:
    material = Material(
        sku=data.sku,
        name=data.name,
        description=data.description,
        unit=data.unit.value,
        unit_cost=data.unit_cost,
    )
    db.add(material)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise MaterialSkuAlreadyExistsError from exc

    db.refresh(material)
    return material


def list_materials(db: Session) -> list[Material]:
    statement = select(Material).order_by(Material.id.asc())
    return list(db.execute(statement).scalars().all())


def get_material_by_id(db: Session, material_id: int) -> Material | None:
    statement = select(Material).where(Material.id == material_id)
    return db.execute(statement).scalars().first()