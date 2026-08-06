# Harness Updates (P0 Critical Gaps)

This skill implements the top‑priority actionable changes identified in `HARNESS_ENGINEERING_AUDIT.md`.

## Findings addressed

| # | Gap | Recommendation | Implementation |
|---|-----|----------------|------------------|
| 1 | **Model Fusion** | Build a fusion Kanban workflow that dispatches two agents with different models and merges their outputs. | Added placeholder `hooks/fusion_workflow.py` (see below) and a skill entry documenting the workflow.
| 2 | **Validation Gates Before Execution** | Introduce a validation‑gate phase that must pass before any builder task runs. | Added `hooks/validation_gate.py` and a simple `gate.yaml` example.
| 3 | **Autonomous Issue‑to‑PR Loop** | Create a cron‑triggered pipeline that fetches open GitHub issues, triages, implements, validates, and opens a PR. | Added `cron/issue_pr_loop.sh` (placeholder) and a minimal test.

## Usage

- **Model Fusion**: Run `hermes run hooks/fusion_workflow.py` to see a stub fusion process.
- **Validation Gate**: Place a `gate.yaml` in the workspace root; run `hermes run hooks/validation_gate.py` to validate.
- **Issue‑to‑PR Loop**: Enable the cron job `issue_pr_loop.sh` via `hermes cron enable` to schedule.

## Acceptance Criteria

- Code compiles (Python scripts are syntactically correct).
- Tests in `tests/test_harness_updates.py` pass.
- PR description will map each file to the corresponding audit finding.
