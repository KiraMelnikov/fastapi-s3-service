import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.routers import main_router


def get_app() -> FastAPI:
    application = FastAPI(title="JSON receiver", docs_url="/api/v1/docs")
    application.add_middleware(CORSMiddleware)
    application.include_router(main_router)
    return application


app = get_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
