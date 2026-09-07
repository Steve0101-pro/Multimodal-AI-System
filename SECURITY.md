# Security and assurance runbook

## Release gates

- Run the unit and offline evaluation suites.
- Run `pip-audit` and `bandit -r app -ll` in CI.
- Run `scripts/load_test.py` against staging with representative limits.
- Run an authenticated dynamic scan such as OWASP ZAP against staging.
- Commission an annual independent penetration test before handling regulated data.

## AI abuse cases

Test prompt injection through transcript, image OCR, and uploaded documents. Verify
that system instructions are not disclosed, credentials are never returned, and
model output cannot initiate arbitrary outbound requests. Keep attack fixtures in
the evaluation suite and block releases on critical regressions.

## Incident response

Disable the affected experiment variant, rotate compromised credentials, preserve
the audit event IDs, remove affected storage objects, and record the incident,
scope, remediation, and notification decision.
