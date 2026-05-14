from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ntm.core.database import get_db
from ntm.schemas.release import (
    ReleaseCreate, ReleaseUpdate, ReleaseTemplateAdd,
    ReleaseOut, ReleaseDetailOut, SnapshotOut,
)
from ntm.services import release_service

router = APIRouter(prefix="/releases", tags=["releases"])


@router.get("/", response_model=list[ReleaseOut])
def list_releases(db: Session = Depends(get_db)):
    releases = release_service.list_releases(db)
    return [ReleaseOut.model_validate(r) for r in releases]


@router.post("/", response_model=ReleaseOut, status_code=201)
def create_release(data: ReleaseCreate, db: Session = Depends(get_db)):
    release = release_service.create_release(db, data)
    return ReleaseOut.model_validate(release)


@router.get("/{release_id}", response_model=ReleaseDetailOut)
def get_release(release_id: int, db: Session = Depends(get_db)):
    release = release_service.get_release(db, release_id)
    if not release:
        raise HTTPException(404, "Release not found")
    detail = ReleaseDetailOut.model_validate(release)
    detail.template_count = len(release.snapshots)
    snapshots = []
    for snap in release.snapshots:
        s = SnapshotOut.model_validate(snap)
        if snap.template:
            s.template_name = snap.template.name
            s.template_filename = snap.template.filename
        if snap.template_version:
            s.version = snap.template_version.version
        snapshots.append(s)
    detail.snapshots = snapshots
    return detail


@router.put("/{release_id}", response_model=ReleaseOut)
def update_release(release_id: int, data: ReleaseUpdate, db: Session = Depends(get_db)):
    release = release_service.get_release(db, release_id)
    if not release:
        raise HTTPException(404, "Release not found")
    release = release_service.update_release(db, release, data)
    return ReleaseOut.model_validate(release)


@router.post("/{release_id}/add-template", response_model=SnapshotOut)
def add_template(release_id: int, data: ReleaseTemplateAdd, db: Session = Depends(get_db)):
    release = release_service.get_release(db, release_id)
    if not release:
        raise HTTPException(404, "Release not found")
    snapshot = release_service.add_template_to_release(db, release, data)
    if not snapshot:
        raise HTTPException(409, "Template already in this release")
    s = SnapshotOut.model_validate(snapshot)
    if snapshot.template:
        s.template_name = snapshot.template.name
        s.template_filename = snapshot.template.filename
    if snapshot.template_version:
        s.version = snapshot.template_version.version
    return s


@router.delete("/{release_id}/templates/{template_id}", status_code=204)
def remove_template(release_id: int, template_id: int, db: Session = Depends(get_db)):
    release = release_service.get_release(db, release_id)
    if not release:
        raise HTTPException(404, "Release not found")
    removed = release_service.remove_template_from_release(db, release, template_id)
    if not removed:
        raise HTTPException(404, "Template not in this release")


@router.post("/{release_id}/generate-changelog")
def generate_changelog(release_id: int, db: Session = Depends(get_db)):
    release = release_service.get_release(db, release_id)
    if not release:
        raise HTTPException(404, "Release not found")
    changelog = release_service.generate_changelog(db, release)
    release.changelog = changelog
    db.flush()
    return {"changelog": changelog}


@router.post("/{release_id}/publish")
def publish_release(release_id: int, db: Session = Depends(get_db)):
    from ntm.services.github_service import create_tag, create_release as gh_create_release

    release = release_service.get_release(db, release_id)
    if not release:
        raise HTTPException(404, "Release not found")
    if release.status == "published":
        raise HTTPException(409, "Release already published")

    tag_result = create_tag(release.version)
    if not tag_result.get("success"):
        raise HTTPException(502, f"Tag creation failed: {tag_result.get('error')}")

    release_result = gh_create_release(
        release.version,
        release.name,
        release.changelog or "",
    )
    if not release_result.get("success"):
        raise HTTPException(502, f"GitHub Release creation failed: {release_result.get('error')}")

    release.github_release_url = release_result.get("release_url")
    release = release_service.publish_release(db, release)

    return {
        "status": "published",
        "tag": release.github_tag,
        "release_url": release.github_release_url,
    }
