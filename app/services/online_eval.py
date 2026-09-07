"""Privacy-preserving online response evaluation."""

import hashlib
import logging
from typing import Any

from app.config import settings
from app.services.judge import judge_response
from app.services.metrics import EVALUATIONS, JUDGE_FAILURES

logger = logging.getLogger(__name__)


def _sampled(sample_key: str) -> bool:
    digest = hashlib.sha256(sample_key.encode("utf-8")).digest()
    bucket = int.from_bytes(digest[:8], "big") / float(2**64)
    return bucket < settings.ONLINE_EVAL_SAMPLE_RATE


async def evaluate_response(
    request_text: str,
    response_text: str,
    context: str,
    sample_key: str,
    variant: str,
) -> dict[str, Any]:
    """Run the optional judge without allowing evaluation to break user traffic."""
    if not settings.ONLINE_EVAL_ENABLED:
        EVALUATIONS.labels("disabled", variant).inc()
        return {"status": "disabled"}
    if not _sampled(sample_key):
        EVALUATIONS.labels("sampled_out", variant).inc()
        return {"status": "sampled_out"}
    if not settings.OPENAI_API_KEY.get_secret_value():
        EVALUATIONS.labels("unconfigured", variant).inc()
        return {"status": "unconfigured"}

    try:
        scores = await judge_response(request_text, response_text, context)
        EVALUATIONS.labels("completed", variant).inc()
        return {"status": "completed", "scores": scores}
    except Exception:
        JUDGE_FAILURES.inc()
        EVALUATIONS.labels("failed", variant).inc()
        logger.exception("Online response evaluation failed")
        return {"status": "failed"}