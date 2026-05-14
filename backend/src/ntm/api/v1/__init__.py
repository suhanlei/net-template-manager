from fastapi import APIRouter

from ntm.api.v1.categories import router as categories_router
from ntm.api.v1.templates import router as templates_router
from ntm.api.v1.releases import router as releases_router
from ntm.api.v1.github import router as github_router
from ntm.api.v1.system import router as system_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(categories_router)
api_router.include_router(templates_router)
api_router.include_router(releases_router)
api_router.include_router(github_router)
api_router.include_router(system_router)
