from fastapi import APIRouter, HTTPException

from ntm.services.github_service import (
    test_connection,
    get_repo_info,
    sync_recent_commits,
)

router = APIRouter(prefix="/github", tags=["github"])


@router.get("/status")
async def github_status():
    return test_connection()


@router.post("/test-connection")
async def test_github_connection():
    result = test_connection()
    if not result.get("connected"):
        raise HTTPException(502, f"Connection failed: {result.get('error')}")
    return result


@router.get("/repo-info")
async def repo_info():
    info = get_repo_info()
    if not info:
        raise HTTPException(502, "Cannot access repository")
    return info


@router.post("/sync")
async def sync():
    result = sync_recent_commits()
    if not result.get("success"):
        raise HTTPException(502, f"Sync failed: {result.get('error')}")
    return result
