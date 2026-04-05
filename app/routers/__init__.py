from fastapi import APIRouter, Depends

from app.auth import verify_token
from app.routers.auth import router as auth_router
from app.routers.base import router as base_router
from app.routers.local import router as local_router
from app.routers.root import router as root_router
from app.routers.s3 import router as s3_router

main_router = APIRouter()
main_router.include_router(root_router)
main_router.include_router(auth_router)
base_router.include_router(s3_router, dependencies=[Depends(verify_token)])
base_router.include_router(local_router, dependencies=[Depends(verify_token)])
main_router.include_router(base_router)

__all__ = ["main_router"]
