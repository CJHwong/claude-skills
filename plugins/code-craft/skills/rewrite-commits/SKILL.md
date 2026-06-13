---
name: rewrite-commits
description: |
  Use this skill when the user wants to clean up commits that already exist on
  the current branch: "squash commits", "rewrite history", "reword commit
  messages", "fold fixup commits", "autosquash", "clean up WIP commits",
  "organize branch history", or "prepare this branch for PR". Compare against
  the base branch, propose a safe rewrite plan, and wait for approval before
  rebasing or resetting. Do not use for uncommitted-only changes, creating new
  work commits, PR comments, CI checks, or GitHub remote operations.
user-invocable: true
argument-hint: "[optional: base branch, defaults to main]"
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
---

# Rewrite Commits

## When to Apply

- Use when the user asks to "rewrite commits", "clean up commits", "organize commits", "squash commits", or "prepare for PR".
- Use before creating a PR when the commit history has WIP or messy commits.
- Use when the user wants to consolidate fixup commits or reformat commit messages to the repo's conventions.
- Do not use when the branch has been pushed and others are working on it (rewriting shared history).
- Do not use when there are only 1-2 clean, well-formatted commits already.

Clean up commit history before PR. Reorganize messy WIP commits into logical,
well-formatted commits that tell a clear story.

## Arguments

$ARGUMENTS — Optional: base branch to compare against (defaults to `main` or repo default).

## Step 1: Analyze Current Commits

Resolve the base branch: use `$ARGUMENTS` if provided, otherwise detect the
repo default with `git remote show origin | grep 'HEAD branch' | awk '{print $NF}'`
and fall back to `main`. Store as `BASE_BRANCH`.

```bash
BASE_BRANCH="${ARGUMENTS:-$(git remote show origin 2>/dev/null | grep 'HEAD branch' | awk '{print $NF}' || echo main)}"
git log --oneline $(git merge-base HEAD origin/${BASE_BRANCH})..HEAD
```

```bash
git diff --stat $(git merge-base HEAD origin/${BASE_BRANCH})..HEAD
```

```bash
git log --format="%H %s" $(git merge-base HEAD origin/${BASE_BRANCH})..HEAD
```

Understand:
- How many commits exist on this branch
- What files each commit touches
- Which commits are WIP, fixup, or messy

If there's only 1 commit and it's already well-formatted, say so and stop.

## Step 2: Determine Ticket Key

Look for a ticket key in:
1. Branch name (e.g., `feat/PROJ-42-cancel-flow` -> `PROJ-42`)
2. Existing commit messages
3. Ask the user if not found

## Step 3: Propose Logical Splits

Group the changes into logical commits. Rules:

1. **One concern per commit.** A feature change and its tests can be together
   or split — follow the repo's convention (check `git log` for patterns).
2. **Migrations separate.** Schema migrations get their own commit.
3. **Refactors separate.** If you refactored existing code to enable the feature,
   that's a separate commit before the feature commit.
4. **Config/infra separate.** New dependencies, CI changes, config changes.
5. **Order matters.** Commits should build on each other — earlier commits
   don't depend on later ones.

Present the proposal:

```
## Proposed Commits (N total)

### Commit 1: refactor(payments): extract payment query helper [PROJ-42]
Files: src/payments/query.py
[why] ...
[how] ...

### Commit 2: feat(payments): add refund validation for voided charges [PROJ-42]
Files: src/payments/refund.py, src/payments/validators.py
[why] ...
[how] ...

### Commit 3: test(payments): add tests for refund on voided charges [PROJ-42]
Files: tests/payments/test_refund.py
[why] ...
[how] ...
```

Wait for user approval. The user may:
- Approve as-is
- Ask to merge some commits
- Ask to split differently
- Edit commit messages

## Step 3a: Autosquash Pre-Existing Fixup Commits (alternative to Step 4)

When the branch already contains `fixup!` / `squash!` commits (e.g. from
review-fix loops), prefer autosquash over a full
soft-reset rewrite — it preserves the logical commits and only folds the
fixups in.

Before running autosquash, ensure the working tree is clean:

```bash
git status --short
```

If there are uncommitted changes, STOP and ask the user to stash or commit
them first — `git rebase` will abort on a dirty tree.

Then verify each fixup's target actually contains
the lines the fixup modifies. A fixup targeted at a commit that doesn't
yet contain those lines will hit a merge conflict during autosquash
(shape: `<<<<<<< HEAD` / empty section / `>>>>>>> <fixup-sha>`).

```bash
# For each fixup commit and the file(s) it touches:
git log --oneline $(git merge-base HEAD origin/${BASE_BRANCH})..HEAD -- <path>
git show <target-sha> -- <path>   # confirm patched lines exist in target
```

Then propose the squash plan to the user and get explicit confirmation —
`git rebase -i --autosquash` rewrites history and is not trivially reversible.
Only after the user approves:

```bash
GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash \
  $(git merge-base HEAD origin/${BASE_BRANCH})
```

If the rebase surfaces the conflict shape above, do NOT try to hand-resolve it
— abort and re-target instead:

```bash
git rebase --abort
# re-identify the correct target — the commit whose diff introduced the patched lines:
git log --oneline $(git merge-base HEAD origin/${BASE_BRANCH})..HEAD -- <path>
# Re-target the mis-aimed fixup. If it is the CURRENT TIP, un-commit and re-make it:
git reset --soft HEAD~1
git commit --fixup=<correct-target-sha>
# If other commits sit on top of the bad fixup, do NOT `reset --soft HEAD~1`
# (that rewrites the wrong commit). Instead reword the bad fixup's subject to
# `fixup! <correct target subject>` via `git rebase -i \
#   $(git merge-base HEAD origin/${BASE_BRANCH})` — autosquash matches fixups to
# targets by subject line, so a corrected subject re-targets it in place.
# Then retry the autosquash:
GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash \
  $(git merge-base HEAD origin/${BASE_BRANCH})
```

(`git commit --amend --fixup` is NOT valid — `--amend` and `--fixup` are
mutually exclusive. Re-create the fixup with `reset --soft` + `commit --fixup`.)

Step 3a is an ALTERNATIVE to Step 4 — not a precursor. Once autosquash succeeds,
go straight to **Step 5 (Verify)**; do NOT also run the Step 4 soft-reset
rewrite.

## Step 4: Execute Rewrite

Before resetting, check for any uncommitted changes in the working tree:

```bash
git status --short
```

If there are uncommitted changes (tracked or untracked), STOP and tell the
user to stash or commit them first. `git reset --soft` preserves staged and
unstaged changes but mixing them with the branch history can cause unintended
groupings in the new commits.

After the user confirms the working tree is clean (or explicitly says to
proceed anyway), use `git reset --soft` to the merge base, then create the
commits in order:

```bash
# Soft reset to preserve all changes
git reset --soft $(git merge-base HEAD origin/${BASE_BRANCH})

# Create each commit in order
git add <files for commit 1>
git commit -m "$(cat <<'EOF'
<commit 1 message>
EOF
)"

git add <files for commit 2>
git commit -m "$(cat <<'EOF'
<commit 2 message>
EOF
)"

# ... repeat
```

After all commits:

```bash
git log --oneline $(git merge-base HEAD origin/${BASE_BRANCH})..HEAD
```

Show the result to the user.

## Step 5: Verify

Run the test suite to make sure the rewrite didn't break anything:

```bash
<project test command>
```

If tests fail, investigate — the rewrite may have created a commit where
tests don't pass (bisect-unfriendly). Fix the ordering.

## Commit Message Format

Same as the `git-commit` skill:

```
<type>(<scope>): <subject> [<TICKET-KEY>]

[why]
<1-2 sentences>

[how]
<1-2 sentences>
```

## When NOT to Rewrite

- Branch has been pushed and others are working on it (rewriting shared history)
- Only 1-2 clean commits that already follow conventions
- User explicitly says "don't rewrite"
