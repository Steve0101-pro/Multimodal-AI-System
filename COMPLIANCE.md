# Production compliance baseline

This project provides technical controls, not a compliance certification.

## Data handling

- Collect only the audio, image, and prompt data needed for the requested workflow.
- Redact common email, card, SSN, token, and password patterns before persistence.
- Keep provider tracing disabled unless a documented retention and processor review
  permits it.
- Set `RETENTION_DAYS` and run a scheduled deletion job for database, cache,
  object-storage, feedback, and evaluation copies.

## Governance

- Version prompts, models, evaluation cases, and experiment variants.
- Require offline evaluation approval before rollout.
- Use the feedback review queue for human escalation and record reviewer decisions.
- Keep audit records append-only and restrict review access to administrators.

## Required operational evidence

Maintain access reviews, backup/restore tests, vulnerability scan results,
penetration-test reports, incident records, data-subject deletion evidence, and
model-risk approvals. Map these controls to the specific legal regime and customer
contract before making regulatory claims.
