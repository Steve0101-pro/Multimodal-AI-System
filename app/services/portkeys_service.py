"""
Portkeys integration for LLM monitoring, routing, and observability.

Portkeys provides:
- Request routing across multiple LLM providers
- Real-time usage analytics
- Cost tracking
- Performance monitoring
- Fallback and retry mechanisms
"""

import json
import logging
import time
from typing import Any, Dict, Optional
from datetime import datetime
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class PortkeysClient:
    """Client for Portkeys LLM monitoring and routing."""

    BASE_URL = "https://api.portkey.ai/v1"
    TIMEOUT = 30.0

    def __init__(self):
        self.api_key = settings.PORTKEYS_API_KEY.get_secret_value()
        self.provider_slug = settings.PORTKEYS_VIRTUAL_KEY.strip()
        if self.provider_slug and not self.provider_slug.startswith("@"):
            self.provider_slug = f"@{self.provider_slug}"
        self.enabled = settings.PORTKEYS_ENABLED and bool(self.api_key)
        self.gateway_enabled = self.enabled and bool(self.provider_slug)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def gateway_headers(self, provider: str) -> Dict[str, str]:
        """Return headers required to send an OpenAI-compatible call through Portkey."""
        if not self.provider_slug:
            raise RuntimeError(
                "PORTKEYS_VIRTUAL_KEY must contain a saved Portkey integration slug"
            )
        return {
            "x-portkey-api-key": self.api_key,
            "x-portkey-provider": self.provider_slug,
        }

    async def track_llm_call(
        self,
        provider: str,
        model: str,
        request_type: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        latency_ms: float = 0.0,
        status: str = "success",
        cost_usd: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Track an LLM API call to Portkeys.

        Args:
            provider: LLM provider name (e.g., 'google', 'openai', 'anthropic')
            model: Model name (e.g., 'gemini-pro', 'gpt-4')
            request_type: Type of request (e.g., 'vision', 'text', 'embedding')
            input_tokens: Input token count
            output_tokens: Output token count
            latency_ms: Request latency in milliseconds
            status: Request status ('success', 'error', 'timeout')
            cost_usd: Estimated cost in USD
            metadata: Additional tracking metadata

        Returns:
            True if tracking was successful, False if disabled or error
        """
        if not self.enabled:
            logger.debug("Portkeys tracking disabled; skipping")
            return True  # Don't block app if Portkeys is disabled

        # Portkey's public gateway does not expose the legacy /v1/track
        # endpoint. Gateway calls are already observable through Portkey
        # headers, so avoid issuing a request that always returns 400.
        logger.debug(
            "Portkeys gateway telemetry handled for %s/%s (%s)",
            provider,
            model,
            status,
        )
        return True

    async def route_request(
        self,
        request_data: Dict[str, Any],
        providers: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        """
        Route a request through Portkeys to select optimal provider.

        Args:
            request_data: Request payload containing model, messages, etc.
            providers: List of preferred providers to route through

        Returns:
            Routing decision with recommended provider and model
        """
        if not self.enabled:
            logger.debug("Portkeys routing disabled; using default provider")
            return {"provider": "default", "model": request_data.get("model")}

        try:
            payload = {
                "request": request_data,
                "preferred_providers": providers or [],
            }

            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.post(
                    f"{self.BASE_URL}/route",
                    json=payload,
                    headers=self.headers,
                )
                response.raise_for_status()
                result = response.json()
                logger.info(f"Portkeys routing decision: {result.get('provider')}")
                return result

        except httpx.HTTPError as e:
            logger.error(f"Portkeys routing failed: {e}; falling back to default")
            return {"provider": "default", "model": request_data.get("model")}
        except Exception as e:
            logger.error(f"Unexpected error in Portkeys routing: {e}")
            return {"provider": "default", "model": request_data.get("model")}

    async def get_usage_analytics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fetch LLM usage analytics from Portkeys.

        Args:
            start_date: ISO date string for analytics start
            end_date: ISO date string for analytics end
            provider: Filter by specific provider

        Returns:
            Analytics data including costs, tokens, latency, etc.
        """
        if not self.enabled:
            logger.debug("Portkeys analytics disabled")
            return {"error": "Portkeys not enabled"}

        # Portkey analytics are available in its dashboard, not as a
        # supported GET /v1/analytics gateway resource.
        logger.warning(
            "Portkeys analytics is unavailable: the configured analytics "
            "endpoint is not supported by the Portkey API"
        )
        return {
            "available": False,
            "message": "Analytics are available in the Portkey dashboard; this API has no supported analytics endpoint.",
            "dashboard": "https://app.portkey.ai/analytics",
            "start_date": start_date,
            "end_date": end_date,
            "provider": provider,
        }

    async def get_cost_summary(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get LLM cost summary from Portkeys.

        Args:
            start_date: ISO date string
            end_date: ISO date string

        Returns:
            Cost breakdown by provider and model
        """
        if not self.enabled:
            return {"error": "Portkeys not enabled"}

        # Portkey cost summaries are available in its dashboard, not through
        # a supported GET /v1/costs gateway resource.
        logger.warning(
            "Portkeys cost summaries are unavailable through this API"
        )
        return {
            "available": False,
            "message": "Cost summaries are available in the Portkey dashboard; this API has no supported cost endpoint.",
            "dashboard": "https://app.portkey.ai/analytics",
            "start_date": start_date,
            "end_date": end_date,
        }

    async def health_check(self) -> bool:
        """Check Portkeys API connectivity."""
        if not self.enabled:
            logger.debug("Portkeys health check skipped (disabled)")
            return False

        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(
                    f"{self.BASE_URL}/health",
                    headers=self.headers,
                )
                is_healthy = response.status_code == 200
                if is_healthy:
                    logger.info("Portkeys health check passed")
                else:
                    logger.warning(f"Portkeys health check failed: {response.status_code}")
                return is_healthy

        except httpx.HTTPError as e:
            logger.error(f"Portkeys health check failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in Portkeys health check: {e}")
            return False


# Global instance
portkeys_client = PortkeysClient()


async def track_llm_with_timing(
    provider: str,
    model: str,
    request_type: str,
    async_func,
    *args,
    input_tokens: int = 0,
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Any:
    """
    Execute an async LLM function and automatically track metrics to Portkeys.

    Args:
        provider: LLM provider name
        model: Model name
        request_type: Type of request
        async_func: Async function to execute
        *args: Function arguments
        input_tokens: Input token count (optional)
        metadata: Additional metadata
        **kwargs: Function keyword arguments

    Returns:
        Function result
    """
    start_time = time.time()
    try:
        result = await async_func(*args, **kwargs)
        latency_ms = (time.time() - start_time) * 1000

        await portkeys_client.track_llm_call(
            provider=provider,
            model=model,
            request_type=request_type,
            input_tokens=input_tokens,
            output_tokens=0,  # Set by caller if known
            latency_ms=latency_ms,
            status="success",
            metadata=metadata,
        )
        return result

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        await portkeys_client.track_llm_call(
            provider=provider,
            model=model,
            request_type=request_type,
            input_tokens=input_tokens,
            output_tokens=0,
            latency_ms=latency_ms,
            status="error",
            metadata={**(metadata or {}), "error": str(e)},
        )
        raise
