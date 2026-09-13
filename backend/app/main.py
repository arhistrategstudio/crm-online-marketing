from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    auth_router,
    campaigns_router,
    contacts_router,
    conversations_router,
    dashboard_router,
    integrations_router,
    leads_router,
    meetings_router,
    viber_webhook_router,
    webhooks_router,
)
from app.config import get_settings
from app.database import engine
from app.models import Base
from app.security import get_current_user


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


settings = get_settings()

app = FastAPI(
    title="CRM Online Marketing API",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, prefix="/api/v1")
app.include_router(webhooks_router, prefix="/api/v1")
app.include_router(viber_webhook_router, prefix="/api/v1")

protected = [Depends(get_current_user)]
app.include_router(contacts_router, prefix="/api/v1", dependencies=protected)
app.include_router(conversations_router, prefix="/api/v1", dependencies=protected)
app.include_router(dashboard_router, prefix="/api/v1", dependencies=protected)
app.include_router(integrations_router, prefix="/api/v1", dependencies=protected)
app.include_router(leads_router, prefix="/api/v1", dependencies=protected)
app.include_router(campaigns_router, prefix="/api/v1", dependencies=protected)
app.include_router(meetings_router, prefix="/api/v1", dependencies=protected)


@app.get("/api/v1/health")
def health_check() -> dict[str, str]:
    """Returns a simple confirmation that the backend is running."""
    return {"status": "ok"}
