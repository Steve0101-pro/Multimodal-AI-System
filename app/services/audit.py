"""Append-only audit event creation with no sensitive payloads."""

from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog
from app.services.safety import redact_sensitive_data


async def record_audit(
    db: AsyncSession,
    action: str,
    resource_type: str,
    actor_id=None,
    resource_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    db.add(AuditLog(
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata_json=redact_sensitive_data(metadata or {}),
    ))