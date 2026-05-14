import hashlib
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ntm.models.template import Template, TemplateVersion
from ntm.schemas.template import TemplateCreate, TemplateUpdate, TemplateVersionCreate
from ntm.utils.version import increment_version


def _content_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def list_templates(
    db: Session,
    category_id: int | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Template], int]:
    q = select(Template)
    count_q = select(func.count()).select_from(Template)

    if category_id:
        q = q.where(Template.category_id == category_id)
        count_q = count_q.where(Template.category_id == category_id)
    if status:
        q = q.where(Template.status == status)
        count_q = count_q.where(Template.status == status)

    total = db.execute(count_q).scalar()

    q = q.order_by(Template.updated_at.desc()).offset((page - 1) * page_size).limit(page_size)
    templates = list(db.execute(q).scalars().all())

    for t in templates:
        if t.category:
            t.category_name = t.category.name

    return templates, total


def get_template(db: Session, template_id: int) -> Template | None:
    t = db.get(Template, template_id)
    if t and t.category:
        t.category_name = t.category.name
    return t


def create_template(db: Session, data: TemplateCreate) -> Template:
    tpl = Template(**data.model_dump())
    db.add(tpl)
    db.flush()
    db.refresh(tpl)
    if tpl.category:
        tpl.category_name = tpl.category.name
    return tpl


def update_template(db: Session, tpl: Template, data: TemplateUpdate) -> Template:
    update_data = data.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(tpl, k, v)
    db.flush()
    db.refresh(tpl)
    if tpl.category:
        tpl.category_name = tpl.category.name
    return tpl


def archive_template(db: Session, tpl: Template) -> Template:
    tpl.status = "archived"
    db.flush()
    return tpl


def list_versions(db: Session, template_id: int) -> list[TemplateVersion]:
    return list(db.execute(
        select(TemplateVersion)
        .where(TemplateVersion.template_id == template_id)
        .order_by(TemplateVersion.created_at.desc())
    ).scalars().all())


def get_version(db: Session, version_id: int) -> TemplateVersion | None:
    return db.get(TemplateVersion, version_id)


def get_version_by_number(db: Session, template_id: int, version: str) -> TemplateVersion | None:
    return db.execute(
        select(TemplateVersion).where(
            TemplateVersion.template_id == template_id,
            TemplateVersion.version == version,
        )
    ).scalar_one_or_none()


def create_version(db: Session, template: Template, data: TemplateVersionCreate) -> TemplateVersion:
    if template.current_version:
        next_version = increment_version(template.current_version, data.change_type)
    else:
        next_version = "1.0.0" if data.change_type == "major" else "0.1.0" if data.change_type == "minor" else "0.0.1"

    content_hash = _content_hash(data.content)

    tv = TemplateVersion(
        template_id=template.id,
        version=next_version,
        content=data.content,
        content_hash=content_hash,
        change_type=data.change_type,
        commit_message=data.commit_message,
        diff_summary=data.diff_summary,
        created_by=data.created_by,
    )
    db.add(tv)

    template.current_version = next_version
    if template.status == "draft" or not template.current_version:
        template.status = "active"

    db.flush()
    db.refresh(tv)
    return tv


def get_version_content(db: Session, template_id: int, version: str) -> TemplateVersion | None:
    return db.execute(
        select(TemplateVersion).where(
            TemplateVersion.template_id == template_id,
            TemplateVersion.version == version,
        )
    ).scalar_one_or_none()
