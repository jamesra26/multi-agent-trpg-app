from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Multi-Agent TRPG API",
    description="多 Agent 文字 RPG 后端",
    version=settings.app_version,
)

app.include_router(health_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "TRPG API is running"}
