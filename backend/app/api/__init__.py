from app.api.auth import router as auth_router
from app.api.campaigns import router as campaigns_router
from app.api.contacts import router as contacts_router
from app.api.conversations import router as conversations_router
from app.api.dashboard import router as dashboard_router
from app.api.integrations import router as integrations_router
from app.api.leads import router as leads_router

__all__ = [
    "auth_router",
    "campaigns_router",
    "contacts_router",
    "conversations_router",
    "dashboard_router",
    "integrations_router",
    "leads_router",
]
