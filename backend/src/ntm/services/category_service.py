from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ntm.models.category import Category
from ntm.models.template import Template
from ntm.schemas.category import CategoryCreate, CategoryUpdate


def list_categories(db: Session) -> list[Category]:
    return list(db.execute(
        select(Category).order_by(Category.sort_order, Category.id)
    ).scalars().all())


def get_category(db: Session, category_id: int) -> Category | None:
    return db.get(Category, category_id)


def create_category(db: Session, data: CategoryCreate) -> Category:
    cat = Category(**data.model_dump())
    db.add(cat)
    db.flush()
    db.refresh(cat)
    return cat


def update_category(db: Session, cat: Category, data: CategoryUpdate) -> Category:
    update_data = data.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(cat, k, v)
    db.flush()
    db.refresh(cat)
    return cat


def delete_category(db: Session, cat: Category) -> bool:
    count = db.execute(
        select(func.count()).select_from(Template).where(Template.category_id == cat.id)
    ).scalar()
    if count > 0:
        return False
    db.delete(cat)
    db.flush()
    return True
