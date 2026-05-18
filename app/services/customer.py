from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate


def create_customer(db: Session, data: CustomerCreate) -> Customer:
    customer = Customer(
        name=data.name,
        email=data.email,
        phone=data.phone,
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def list_customers(db: Session) -> list[Customer]:
    statement = select(Customer).order_by(Customer.id.asc())
    return list(db.execute(statement).scalars().all())


def get_customer_by_id(db: Session, customer_id: int) -> Customer | None:
    statement = select(Customer).where(Customer.id == customer_id)
    return db.execute(statement).scalars().first()
