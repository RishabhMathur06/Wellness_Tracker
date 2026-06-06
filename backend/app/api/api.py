from fastapi import APIRouter

from app.api.v1.endpoints import health, tracker, chat, auth

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(tracker.router, prefix="/tracker", tags=["tracker"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
