"""
Observability and LLM monitoring endpoints powered by Portkeys.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models import AuditLog, User
from app.services.portkeys_service import portkeys_client
from app.services.metrics import metrics_payload

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["Monitoring & Analytics"])


@router.get("/metrics", include_in_schema=False)
async def prometheus_metrics():
    return Response(content=metrics_payload(), media_type="text/plain; version=0.0.4")


@router.get("/health/portkeys", tags=["Health"])
async def portkeys_health():
    """Check Portkeys connectivity and status."""
    if not portkeys_client.enabled:
        return {
            "portkeys_status": "disabled",
            "enabled": False,
            "timestamp": datetime.utcnow().isoformat(),
        }

    is_healthy = await portkeys_client.health_check()
    status = "healthy" if is_healthy else "unhealthy"
    return {
        "portkeys_status": status,
        "enabled": portkeys_client.enabled,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/evaluations")
async def list_online_evaluations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return recent online evaluation metadata for administrators."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.action == "online_evaluation.completed")
        .order_by(AuditLog.created_at.desc())
        .limit(100)
    )
    return [
        {
            "id": str(event.id),
            "conversation_id": event.resource_id,
            "metadata": event.metadata_json or {},
            "created_at": event.created_at,
        }
        for event in result.scalars().all()
    ]


@router.get("/llm/analytics")
async def get_llm_analytics(
    days: int = 7,
    provider: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Fetch LLM usage analytics for the past N days.

    - **days**: Number of days to look back (default: 7)
    - **provider**: Filter by specific provider (e.g., 'google', 'openai')
    
    Returns: Cost, token usage, latency, and performance metrics
    """
    if not portkeys_client.enabled:
        raise HTTPException(
            status_code=503,
            detail="Portkeys monitoring is not enabled",
        )

    try:
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)

        analytics = await portkeys_client.get_usage_analytics(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            provider=provider,
        )

        logger.info(f"Analytics fetched for user {current_user.id}")
        return analytics

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch LLM analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch analytics from Portkeys",
        )


@router.get("/llm/costs")
async def get_llm_costs(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Fetch LLM cost summary for the past N days.

    - **days**: Number of days to look back (default: 30)
    
    Returns: Cost breakdown by provider and model
    """
    if not portkeys_client.enabled:
        raise HTTPException(
            status_code=503,
            detail="Portkeys monitoring is not enabled",
        )

    try:
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)

        costs = await portkeys_client.get_cost_summary(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
        )

        logger.info(f"Cost summary fetched for user {current_user.id}")
        return costs

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch LLM costs: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch costs from Portkeys",
        )


@router.post("/llm/track")
async def track_llm_call(
    provider: str,
    model: str,
    request_type: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    latency_ms: float = 0.0,
    status: str = "success",
    cost_usd: float = 0.0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Manually log an LLM call to Portkeys.

    This endpoint allows applications to track custom LLM calls that aren't
    automatically instrumented.

    Args:
        provider: LLM provider (e.g., 'openai', 'google', 'anthropic')
        model: Model name
        request_type: Type of request ('vision', 'text', 'embedding', etc.)
        input_tokens: Input token count
        output_tokens: Output token count
        latency_ms: Request latency in milliseconds
        status: Request status ('success', 'error', 'timeout')
        cost_usd: Estimated cost in USD

    Returns: Confirmation of tracking
    """
    if not portkeys_client.enabled:
        raise HTTPException(
            status_code=503,
            detail="Portkeys monitoring is not enabled",
        )

    try:
        success = await portkeys_client.track_llm_call(
            provider=provider,
            model=model,
            request_type=request_type,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            status=status,
            cost_usd=cost_usd,
            metadata={"tracked_by": "api", "user_id": current_user.id},
        )

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to track LLM call",
            )

        logger.info(
            f"LLM call tracked: {provider}/{model} by user {current_user.id}"
        )
        return {
            "message": "LLM call tracked successfully",
            "provider": provider,
            "model": model,
            "tracked_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to track LLM call: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to track LLM call to Portkeys",
        )


@router.post("/llm/route")
async def route_llm_request(
    request_data: dict,
    providers: Optional[list[str]] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Route an LLM request through Portkeys for optimal provider selection.

    Portkeys intelligently selects the best provider based on:
    - Latency and availability
    - Cost optimization
    - Model capabilities
    - User preferences

    Args:
        request_data: Request payload (model, messages, etc.)
        providers: Preferred providers to route through

    Returns: Routing decision with recommended provider and model
    """
    if not portkeys_client.enabled:
        raise HTTPException(
            status_code=503,
            detail="Portkeys routing is not enabled",
        )

    try:
        routing_decision = await portkeys_client.route_request(
            request_data=request_data,
            providers=providers,
        )

        logger.info(
            f"Routed LLM request to {routing_decision.get('provider')} "
            f"for user {current_user.id}"
        )
        return routing_decision

    except Exception as e:
        logger.error(f"Failed to route LLM request: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to route request through Portkeys",
        )
