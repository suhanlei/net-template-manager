from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ntm.core.database import get_db
from ntm.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from ntm.services import category_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    cats = category_service.list_categories(db)
    result = []
    for c in cats:
        out = CategoryOut.model_validate(c)
        out.template_count = len(c.templates)
        result.append(out)
    return result


@router.post("/", response_model=CategoryOut, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    cat = category_service.create_category(db, data)
    out = CategoryOut.model_validate(cat)
    out.template_count = 0
    return out


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    cat = category_service.get_category(db, category_id)
    if not cat:
        raise HTTPException(404, "Category not found")
    cat = category_service.update_category(db, cat, data)
    out = CategoryOut.model_validate(cat)
    out.template_count = len(cat.templates)
    return out


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    cat = category_service.get_category(db, category_id)
    if not cat:
        raise HTTPException(404, "Category not found")
    deleted = category_service.delete_category(db, cat)
    if not deleted:
        raise HTTPException(409, "Category has templates, cannot delete")
