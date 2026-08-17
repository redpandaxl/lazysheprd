# Agent Coordination Protocol

## Communication (non-negotiable)

**All agent-to-agent communication goes through Herdr.**

- Status updates, assignments, unblocks, review requests, and handoffs use Herdr agent messaging (`herdr agent prompt`), not “they’ll see my pane.”
- When you finish or unblock something, **explicitly notify** the relevant agents **and Ops**.
- Do **not** assume other agents are watching your pane.
- Read and follow **`protocols/herdr-messaging.md`** for commands and message shape.

If you are not messaging via Herdr, you are not coordinating correctly.

## Task Board Rules

- Ops owns TASKS.md (create, assign, reorder).
- Every agent updates their own tasks only (status + notes).
- Statuses: `todo` | `in-progress` | `blocked` | `review` | `done`
- Board updates do **not** replace Herdr messages. Do both: update TASKS.md **and** prompt the right agents.

## Definition of Done

A task may only be marked `done` after QA has reviewed it (or Ops explicitly waives QA).

QA review is requested and returned **via Herdr prompts**, not by silent TASKS.md edits alone.

## Git Policy

- Only Ops decides when to commit and push.
- Agents may stage changes, but do not commit unless Ops instructs them to.
- Prefer small, reviewable commits with clear messages.

## Escalation

Only escalate to the human when:

- You are blocked on a decision that requires product judgment
- Something is ready for final human review
- A critical risk appears (security, data loss, etc.)

Ops escalates to the human. Other agents escalate to Ops **via Herdr**, not by pinging the human first.
