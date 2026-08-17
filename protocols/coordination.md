# Agent Coordination Protocol

## Communication
- All status updates and unblocks go through Herdr (agent messaging / pane prompts).
- When you finish or unblock something, explicitly notify the relevant agents and Ops.
- Do not assume other agents are watching your pane.

## Task Board Rules
- Ops owns TASKS.md (create, assign, reorder).
- Every agent updates their own tasks only (status + notes).
- Statuses: `todo` | `in-progress` | `blocked` | `review` | `done`

## Definition of Done
A task may only be marked `done` after QA has reviewed it (or Ops explicitly waives QA).

## Git Policy
- Only Ops decides when to commit and push.
- Agents may stage changes, but do not commit unless Ops instructs them to.
- Prefer small, reviewable commits with clear messages.

## Escalation
Only escalate to the human when:
- You are blocked on a decision that requires product judgment
- Something is ready for final human review
- A critical risk appears (security, data loss, etc.)
