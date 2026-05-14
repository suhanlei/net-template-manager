from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ntm.core.database import get_db
from ntm.models.template import Template, TemplateVersion
from ntm.models.release import Release
from ntm.models.category import Category
from ntm.models.git_log import GitLog

router = APIRouter(tags=["system"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/dashboard/stats")
def dashboard_stats(db: Session = Depends(get_db)):
    template_count = db.execute(select(func.count()).select_from(Template)).scalar()
    version_count = db.execute(select(func.count()).select_from(TemplateVersion)).scalar()
    release_count = db.execute(select(func.count()).select_from(Release)).scalar()
    category_count = db.execute(select(func.count()).select_from(Category)).scalar()

    recent_logs = list(db.execute(
        select(GitLog).order_by(GitLog.created_at.desc()).limit(10)
    ).scalars().all())

    recent_templates = list(db.execute(
        select(Template).order_by(Template.updated_at.desc()).limit(5)
    ).scalars().all())

    return {
        "counts": {
            "templates": template_count,
            "versions": version_count,
            "releases": release_count,
            "categories": category_count,
        },
        "recent_templates": [
            {
                "id": t.id,
                "name": t.name,
                "status": t.status,
                "current_version": t.current_version,
                "updated_at": t.updated_at.isoformat(),
            }
            for t in recent_templates
        ],
        "recent_logs": [
            {
                "id": log.id,
                "action": log.action,
                "target_type": log.target_type,
                "detail": log.detail,
                "status": log.status,
                "created_at": log.created_at.isoformat(),
            }
            for log in recent_logs
        ],
    }
