from fastapi import APIRouter

router = APIRouter(prefix="/local")


@router.get("/local", tags=["local"])
async def local_router() -> dict[str, str]:
    return {"Hello": "World"}
