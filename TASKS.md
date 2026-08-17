# TASKS — herdr-agent-team (template repo)

Statuses: `todo` | `in-progress` | `blocked` | `review` | `done`

## Phase 1 — Scaffold matches recommended structure

| ID | Task | Owner | Status | Notes |
|----|------|-------|--------|-------|
| T1 | Create `agents/{ops,infrastructure,developers,design,qa}.md` (generic, short, stable). Move root `ops.md` content into `agents/ops.md`; remove root `ops.md`. | dev | done | QA PASS (T7). |
| T2 | Create `templates/CONVENTIONS.md` and `templates/TASKS.md` (generic blanks for new projects). | dev | done | QA PASS (T7). |
| T3 | Keep/refresh `protocols/coordination.md` to match human spec (already close). | dev | done | QA PASS (T7). |
| T4 | Rewrite `bootstrap.sh`: script-relative paths via `BASH_SOURCE`, copy templates/protocols/agents, refuse to clobber non-empty target, print next steps. | dev | done | QA PASS (T7). |
| T5 | Write root `README.md` (what this is, structure, how to bootstrap, how to improve template over time). | dev | done | QA PASS (T7). |
| T6 | Dry-run bootstrap into a temp dir under `/tmp`, verify tree, clean up. Mark ready for QA. | dev | done | QA PASS (T7). |

## Phase 2 — After QA

| ID | Task | Owner | Status | Notes |
|----|------|-------|--------|-------|
| T7 | QA review of scaffold + bootstrap dry-run | claude | done | PASS — report `/tmp/qa-t7-report.md`. |
| T8 | Ops commit decision | ops | done | Initial commit on `main`. No remote — not pushed. |
