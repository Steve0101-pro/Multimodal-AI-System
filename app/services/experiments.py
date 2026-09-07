"""Deterministic experiment assignment for safe prompt/model rollouts."""

import hashlib

from app.config import settings


def assign_variant(subject_id: str, experiment: str = "multimodal-prompt") -> str:
    variants = [item.strip() for item in settings.AB_TEST_VARIANTS.split(",") if item.strip()]
    if not settings.AB_TEST_ENABLED or len(variants) < 2:
        return variants[0] if variants else "control"
    digest = hashlib.sha256(f"{experiment}:{subject_id}".encode()).digest()
    return variants[int.from_bytes(digest[:4], "big") % len(variants)]