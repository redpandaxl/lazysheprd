# Herdr Messaging (mandatory)

Agents do **not** coordinate by hoping someone is watching their pane.
Every status update, assignment, unblock, review request, and handoff goes through **Herdr agent messaging**.

## Rules

1. **Never assume pane watching.** If you need another agent to act, you must message them.
2. **Always name the target.** Use the unique agent name from `herdr agent list` (or the pane id if names collide).
3. **Always notify Ops** on finish, block, or review — plus any agent who must act next.
4. **Prefer `herdr agent prompt`** over raw terminal injection for agent-to-agent work.
5. **Wait when you need a result** (`--wait`) so you do not race an idle agent.

## Commands (from any agent pane with `HERDR_ENV=1`)

```bash
# Who is live?
herdr agent list

# Assign / notify / unblock (preferred)
herdr agent prompt <name-or-pane> "Your message..." --wait --timeout 120000

# Read their latest output if needed
herdr agent read <name-or-pane> --source recent-unwrapped --lines 80

# Lifecycle
herdr agent get <name-or-pane>
herdr agent wait <name-or-pane> --timeout 120000
```

## When you must message

| Event | Message who |
|-------|-------------|
| Task started | Ops (optional short note) |
| Task blocked | Ops + anyone waiting on you |
| Ready for review | Ops + QA |
| Review finished | Ops + implementer |
| Unblocked someone | That agent + Ops |
| Need a decision | Ops (Ops escalates to human if product judgment) |

## Message shape (keep it scannable)

```
TO: <role>
RE: <task id or topic>
STATUS: in-progress | blocked | review | done
NEED: <what you need from them, or "none">
NOTES: <1–5 lines>
```

## Anti-patterns

- Finishing work and only updating TASKS.md with no Herdr prompt
- Saying “see my pane” without messaging
- Addressing “grok” when two groks exist — rename or use pane ids
- Spamming prompts without `--wait` / without reading the reply
