# code-craft

Helpers for the inner coding loop: research, verify, test, commit.

## Skills

| Skill | What it does |
|-------|--------------|
| `git-commit` | Organize current uncommitted changes into logical, well-formatted commits with `[why]`/`[how]` bodies. Plans first, waits for approval before staging. |
| `rewrite-commits` | Clean up existing branch history before a PR: squash, reword, fold fixups, autosquash. Compares against the base branch and waits for approval before rewriting. |

## Agents

- `researcher` — deep read-only codebase research with persistent memory
- `verifier` — confirm changes actually work at runtime (endpoints, logs, containers)
- `test-runner` — run the project's native test command and report failures with root cause
- `git-organizer` — propose logical commit splits with proper formatting
- `scope-guard` — flag file changes that fall outside the stated task scope
