import logging
from sqlalchemy import select
from sqlalchemy.orm import Session

from ntm.models.release import Release, ReleaseTemplateSnapshot
from ntm.models.template import Template, TemplateVersion
from ntm.schemas.release import ReleaseCreate, ReleaseUpdate, ReleaseTemplateAdd

logger = logging.getLogger(__name__)


def list_releases(db: Session) -> list[Release]:
    releases = list(db.execute(
        select(Release).order_by(Release.created_at.desc())
    ).scalars().all())
    for r in releases:
        r.template_count = len(r.snapshots)
    return releases


def get_release(db: Session, release_id: int) -> Release | None:
    return db.get(Release, release_id)


def create_release(db: Session, data: ReleaseCreate) -> Release:
    release = Release(**data.model_dump())
    db.add(release)
    db.flush()
    db.refresh(release)
    return release


def update_release(db: Session, release: Release, data: ReleaseUpdate) -> Release:
    update_data = data.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(release, k, v)
    db.flush()
    db.refresh(release)
    return release


def add_template_to_release(db: Session, release: Release, data: ReleaseTemplateAdd) -> ReleaseTemplateSnapshot | None:
    existing = db.execute(
        select(ReleaseTemplateSnapshot).where(
            ReleaseTemplateSnapshot.release_id == release.id,
            ReleaseTemplateSnapshot.template_id == data.template_id,
        )
    ).scalar_one_or_none()
    if existing:
        return None

    snapshot = ReleaseTemplateSnapshot(
        release_id=release.id,
        template_id=data.template_id,
        template_version_id=data.template_version_id,
    )
    db.add(snapshot)
    db.flush()
    db.refresh(snapshot)
    return snapshot


def remove_template_from_release(db: Session, release: Release, template_id: int) -> bool:
    snapshot = db.execute(
        select(ReleaseTemplateSnapshot).where(
            ReleaseTemplateSnapshot.release_id == release.id,
            ReleaseTemplateSnapshot.template_id == template_id,
        )
    ).scalar_one_or_none()
    if not snapshot:
        return False
    db.delete(snapshot)
    db.flush()
    return True


def generate_changelog(db: Session, release: Release) -> str:
    lines = [f"# {release.name}", f"\n## v{release.version}\n"]
    lines.append("### Included Templates\n")

    for snap in release.snapshots:
        tv = db.get(TemplateVersion, snap.template_version_id)
        tpl = db.get(Template, snap.template_id)
        if tv and tpl:
            change_icon = {"major": "🔥", "minor": "✨", "patch": "🐛"}.get(tv.change_type, "📝")
            lines.append(f"- **{tpl.name}** `v{tv.version}` ({tv.change_type})")
            if tv.diff_summary:
                lines.append(f"  - {tv.diff_summary}")

    return "\n".join(lines)


def publish_release(db: Session, release: Release) -> Release:
    release.status = "published"
    release.github_tag = f"v{release.version}"
    db.flush()
    db.refresh(release)

    for snap in release.snapshots:
        tv = db.get(TemplateVersion, snap.template_version_id)
        if tv and tv.status != "released":
            tv.status = "released"
    db.flush()

    return release
