"""Low-cardinality Prometheus metrics for online evaluation and operations."""

from prometheus_client import Counter, Histogram, generate_latest

REQUESTS = Counter("document_intelligence_requests_total", "Requests by workflow and status", ["workflow", "status"])
FEEDBACK = Counter("document_intelligence_feedback_total", "Submitted feedback", ["rating", "variant"])
LATENCY = Histogram("document_intelligence_workflow_latency_seconds", "Workflow latency", ["workflow"])
EVALUATIONS = Counter("document_intelligence_evaluations_total", "Online evaluations by status", ["status", "variant"])
JUDGE_FAILURES = Counter("document_intelligence_judge_failures_total", "LLM judge failures")


def metrics_payload() -> bytes:
    return generate_latest()