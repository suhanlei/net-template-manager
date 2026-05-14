from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ntm.core.database import get_db
from ntm.schemas.template import (
    TemplateCreate, TemplateUpdate, TemplateOut, TemplateDetailOut,
    TemplateVersionCreate, TemplateVersionOut, TemplateVersionContentOut, DiffOut,
)
from ntm.services import template_service
from ntm.utils.diff import unified_diff

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/", response_model=list[TemplateOut])
def list_templates(
    category_id: int | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    templates, _ = template_service.list_templates(db, category_id, status, page, page_size)
    return [TemplateOut.model_validate(t) for t in templates]


@router.post("/", response_model=TemplateOut, status_code=201)
def create_template(data: TemplateCreate, db: Session = Depends(get_db)):
    tpl = template_service.create_template(db, data)
    return TemplateOut.model_validate(tpl)


@router.get("/{template_id}", response_model=TemplateDetailOut)
def get_template(template_id: int, db: Session = Depends(get_db)):
    tpl = template_service.get_template(db, template_id)
    if not tpl:
        raise HTTPException(404, "Template not found")
    detail = TemplateDetailOut.model_validate(tpl)
    detail.versions = [TemplateVersionOut.model_validate(v) for v in tpl.versions]
    return detail


@router.put("/{template_id}", response_model=TemplateOut)
def update_template(template_id: int, data: TemplateUpdate, db: Session = Depends(get_db)):
    tpl = template_service.get_template(db, template_id)
    if not tpl:
        raise HTTPException(404, "Template not found")
    tpl = template_service.update_template(db, tpl, data)
    return TemplateOut.model_validate(tpl)


@router.delete("/{template_id}", status_code=204)
def archive_template(template_id: int, db: Session = Depends(get_db)):
    tpl = template_service.get_template(db, template_id)
    if not tpl:
        raise HTTPException(404, "Template not found")
    template_service.archive_template(db, tpl)


@router.get("/{template_id}/versions", response_model=list[TemplateVersionOut])
def list_versions(template_id: int, db: Session = Depends(get_db)):
    versions = template_service.list_versions(db, template_id)
    return [TemplateVersionOut.model_validate(v) for v in versions]


@router.post("/{template_id}/versions", response_model=TemplateVersionOut, status_code=201)
def create_version(template_id: int, data: TemplateVersionCreate, db: Session = Depends(get_db)):
    tpl = template_service.get_template(db, template_id)
    if not tpl:
        raise HTTPException(404, "Template not found")
    tv = template_service.create_version(db, tpl, data)
    return TemplateVersionOut.model_validate(tv)


@router.get("/{template_id}/versions/{version}", response_model=TemplateVersionContentOut)
def get_version_content(template_id: int, version: str, db: Session = Depends(get_db)):
    tv = template_service.get_version_content(db, template_id, version)
    if not tv:
        raise HTTPException(404, "Version not found")
    return TemplateVersionContentOut.model_validate(tv)


@router.get("/{template_id}/versions/{v1}/diff/{v2}", response_model=DiffOut)
def diff_versions(template_id: int, v1: str, v2: str, db: Session = Depends(get_db)):
    tv1 = template_service.get_version_content(db, template_id, v1)
    tv2 = template_service.get_version_content(db, template_id, v2)
    if not tv1 or not tv2:
        raise HTTPException(404, "One or both versions not found")
    diff_text = unified_diff(tv1.content, tv2.content, filename=tv1.template.filename if tv1.template else "config")
    return DiffOut(template_id=template_id, version1=v1, version2=v2, unified_diff=diff_text)


@router.post("/{template_id}/versions/{version}/commit")
def commit_version(template_id: int, version: str, db: Session = Depends(get_db)):
    from ntm.services.github_service import commit_file
    tpl = template_service.get_template(db, template_id)
    if not tpl:
        raise HTTPException(404, "Template not found")
    tv = template_service.get_version_content(db, template_id, version)
    if not tv:
        raise HTTPException(404, "Version not found")
    if tv.status != "draft":
        raise HTTPException(409, f"Version status is '{tv.status}', only 'draft' can be committed")

    path = tpl.github_path or f"{tpl.category.slug}/{tpl.filename}"
    message = tv.commit_message or f"Update {tpl.name} to v{tv.version}"
    result = commit_file(path, tv.content, message)

    if result.get("success"):
        tv.status = "committed"
        tv.github_commit_sha = result["commit_sha"]
        db.flush()
        return {"status": "committed", "commit_sha": result["commit_sha"]}
    else:
        raise HTTPException(502, f"GitHub commit failed: {result.get('error')}")
