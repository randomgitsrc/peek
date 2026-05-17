"""API Key management routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlmodel import Session, select

from peekview.auth import require_auth
from peekview.exceptions import ConflictError
from peekview.models import ApiKey, ApiKeyCreate, ApiKeyCreateResponse, User
from peekview.services.apikey_service import ApiKeyService, get_apikey_service

router = APIRouter(prefix="/api/v1/apikeys", tags=["apikeys"])


def _get_service(request: Request) -> ApiKeyService:
    return get_apikey_service(request.app)


@router.post("", status_code=201)
async def create_api_key(
    data: ApiKeyCreate,
    request: Request,
    service: ApiKeyService = Depends(_get_service),
    current_user: User = Depends(require_auth),
) -> ApiKeyCreateResponse:
    """Create a new API key. Returns 201 with the plaintext key (shown only once)."""
    # Check name uniqueness for this user
    engine = request.app.state.engine
    with Session(engine) as session:
        existing = session.exec(
            select(ApiKey).where(
                ApiKey.user_id == current_user.id,
                ApiKey.name == data.name,
            )
        ).first()
        if existing:
            raise ConflictError(f"API key with name '{data.name}' already exists")

    return service.create_api_key(
        user_id=current_user.id,
        name=data.name,
        expires_in=data.expires_in,
    )


@router.get("")
async def list_api_keys(
    service: ApiKeyService = Depends(_get_service),
    current_user: User = Depends(require_auth),
) -> dict:
    """List current user's API keys (no secrets or hashes)."""
    keys = service.list_api_keys(current_user.id)
    return {"items": keys}


@router.delete("/expired")
async def cleanup_expired_keys(
    service: ApiKeyService = Depends(_get_service),
    current_user: User = Depends(require_auth),
) -> dict:
    """Delete all expired API keys for the current user."""
    count = service.cleanup_expired_keys(current_user.id)
    return {"deleted": count}


@router.delete("/{key_id}")
async def revoke_api_key(
    key_id: int,
    service: ApiKeyService = Depends(_get_service),
    current_user: User = Depends(require_auth),
) -> dict:
    """Revoke (delete) an API key. Only owner or admin can revoke."""
    service.revoke_api_key(
        key_id=key_id,
        user_id=current_user.id,
        is_admin=current_user.is_admin,
    )
    return {"ok": True}
