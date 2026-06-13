---
name: git-commit
description: |
  Use this skill when the user wants to turn current uncommitted local changes
  into one or more commits: "commit my changes", "make a commit", "split this
  work into commits", "organize staged/unstaged changes", "write commit
  messages", or "use [why]/[how] commit format". Inspect git status and
  diffs, group files by logical change, propose a commit plan, and wait for
  approval before staging or committing. Do not use for rewriting existing
  commits, rebasing, pushing, creating PRs, or remote GitHub operations.
user-invocable: true
argument-hint: "[optional high-level instructions or ticket number]"
---

# Git Commit Organization

## When to Apply

- Use when the user asks to organize and commit current work, especially with multiple unstaged files.
- Use when the user wants commits grouped logically by feature, business flow, or architecture layer.
- Use when the user wants repository-style commit messages with [why] and [how] sections.
- Do not use for branch management, rebasing, conflict resolution, or pull request description writing.

Analyze all unstaged changes and organize them into logical, well-structured commits.

You MUST present a commit plan for review and wait for explicit approval.
DO NOT run git add or git commit until the user replies with "yes" or "proceed".

## Arguments

$ARGUMENTS - Optional high-level instructions, grouping preference, or ticket key.

## Guiding Principles

- Follow user instructions first when provided in $ARGUMENTS.
- Learn and match style from recent commit messages in this repository.
- Group commits by feature, layer, or business logic.
- Keep tests with their implementation in the same commit.
- Respect the architecture boundaries used by the project.

## Step 0: Auto-fix with prek (pre-commit)

Before analyzing diffs, run:

```bash
git add -A && if command -v prek &>/dev/null; then prek run; else pre-commit run; fi; git reset
```

Purpose:
- Stage all files temporarily so prek or pre-commit can auto-fix formatting/imports/lint.
- Keep resulting fixes in the working tree.
- Unstage everything again before planning commits.

If unfixable errors are reported, show the errors and ask whether to continue.

## Step 1: Learn Repository Commit Style

Collect context:

```bash
git branch --show-current
```

```bash
git log --format="%B" -5 | head -100
```

```bash
git status --short
```

```bash
git diff --stat
```

```bash
git diff
```

Identify:
- Subject format and common types
- [why] and [how] body style
- Footer usage (ticket/reference)
- How tests are grouped with implementation

## Step 2: Extract Ticket Key

Resolve ticket key in this order:
1. From $ARGUMENTS
2. From branch name, for example feat/PROJ-42-add-thing -> PROJ-42
3. If none found, omit ticket reference

## Step 3: Analyze and Group Changes

Use git diff to group files logically.

Grouping rules:
- Group by feature or business purpose
- Group by architecture layer when relevant
- Keep tests with implementation in the same commit
- Keep pure refactors separate from behavior changes
- Prefer lower-layer foundational changes before upper-layer integration

Common ordering pattern:
1. Refactor or fix baseline code
2. Domain or use-case changes with tests
3. Adapter or integration layer updates
4. Framework or API integration with integration tests
5. Tooling or configuration changes

## Step 4: Draft Commit Messages

For each planned commit, draft message using repository style.

Standard format:

```text
<type>(<scope>): <concise description>

[why]
<1-3 sentences on motivation>

[how]
<2-5 concise bullets or sentences on implementation>

<optional notes>

<TICKET-KEY>
```

Type guidance:
- feat: new feature
- fix: bug fix
- refactor: structure-only change
- test: test-first commit where tests are the primary change
- docs: documentation-only change
- style: formatting-only change
- perf: performance improvement
- build: build tooling or dependencies
- ci: CI workflow changes
- chore: maintenance or config updates

Body rules:
- Include [why] and [how] for non-trivial commits
- Mention test coverage when tests are included
- Keep concise and specific
- If change is obvious from diff, subject-only message is acceptable

## Step 5: Present Plan and Request Confirmation

Show the full plan in this exact structure:

```text
=== Commit Organization Plan ===

Base: <branch>
Ticket: <TICKET or none>
Total commits: <N>

----------------------------------------

Commit 1: <type>(<scope>): <description>

Files:
  - path/to/file1
  - path/to/file2

Message:
---
<full commit message>
---

----------------------------------------

Commit 2: ...

----------------------------------------

Do you want to proceed with executing this plan? (yes/no)
```

Do not run git add or git commit before explicit user approval.

## Step 6: Execute Plan (Only After "yes" or "proceed")

For each commit in order:

```bash
git add <file1> <file2> <file3>
git commit -m "$(cat <<'EOF'
<approved commit message>
EOF
)"
```

After all commits:

```bash
git log --oneline -<N>
```

Report:
- Number of commits created
- Any remaining unstaged files
- Readiness to push

Never use --no-verify. If hooks fail, show errors and ask how to proceed.

## Examples

```text
feat(auth): add password reset token validation

[why]
Reset links could be reused after expiration in edge cases.
That created a security and support burden.

[how]
Added server-side validation for token expiration and one-time use.
Invalidated token records immediately after successful password change.
Added tests for valid, expired, reused, and malformed token cases.

PROJ-123
```

## Troubleshooting

If user rejects the plan:
- Ask what should change (grouping, order, message content)
- Revise and present updated plan

If execution fails:
- Show error output
- Suggest recovery steps
- Ask whether to retry, adjust, or stop

If files remain unstaged after planned commits:
- List remaining files
- Ask whether to create another commit or discard changes

## Important Rules

- MUST study recent commits before drafting messages
- MUST keep tests with implementation
- MUST include [why] and [how] for substantial changes
- MUST use heredoc format for multi-line commit messages
- MUST wait for explicit yes or proceed before execution
- MUST NOT commit without approval
- MUST NOT split implementation and related tests into separate commits
