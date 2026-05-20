from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.material import Material
from app.models.stock_movement import MovementType, StockMovement
from app.schemas.material import MaterialCreate
from app.schemas.material_receipt import MaterialReceiveRequest


class MaterialSkuAlreadyExistsError(Exception):
    pass


class MaterialNotFoundError(Exception):
    pass


def create_material(db: Session, data: MaterialCreate) -> Material:
    material = Material(
        sku=data.sku,
        name=data.name,
        description=data.description,
        unit=data.unit.value,
        unit_cost=data.unit_cost,
        quantity_on_hand=data.quantity_on_hand,
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


def receive_material_stock(
    db: Session, material_id: int, data: MaterialReceiveRequest
) -> StockMovement:
    material = db.get(Material, material_id)
    if material is None:
        raise MaterialNotFoundError

    material.quantity_on_hand += data.quantity
    movement = StockMovement(
        material_id=material_id,
        quantity=data.quantity,
        movement_type=MovementType.RECEIPT,
        reference=data.reference,
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement


def list_stock_movements(db: Session, material_id: int) -> list[StockMovement]:
    statement = (
        select(StockMovement)
        .where(StockMovement.material_id == material_id)
        .order_by(StockMovement.created_at.asc())
    )
    return list(db.execute(statement).scalars().all())