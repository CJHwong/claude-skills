---
name: "prune-projects"
description: "Find stale .claude/projects/ folders whose source directories no longer exist on the filesystem, then clean them up (merge renamed, delete dead)."
user-invocable: true
---

# Prune Projects

Scan `~/.claude/projects/` for project folders that point to directories no longer on the filesystem. Present findings and clean up based on user instructions.

## Path Encoding

Claude Code encodes project paths by replacing `/`, `.`, and `_` with `-`. This means `--` in a folder name could decode to `/.`, `/_`, or `/-`.

Decoding strategy: for each `--` segment, try all three prefixes (`_`, `.`, `-`) against the filesystem. A single encoded name may have multiple `--` segments requiring independent resolution.

## Execution

### Step 1: Scan

For each directory in `~/.claude/projects/`:

1. Skip `.DS_Store` and non-directories.
2. Decode the folder name back to a filesystem path:
   - Replace `--` with a placeholder (e.g., `\x00`)
   - Replace `-` with `/`
   - For each placeholder, try restoring as `/_`, `/.`, and `/-` (check filesystem existence at each level)
3. If the decoded path exists on the filesystem, skip it.
4. If no valid decoding exists, mark it as **stale**.

### Step 2: Categorize

Group stale folders into:

- **Worktrees**: folders containing `.claude-worktrees` or `.claude/worktrees`
- **Workspace subpaths**: folders whose encoded name is a subpath of another project folder that still exists
- **Temp**: folders under `/private/tmp/` or `/var/folders/`
- **Regular**: everything else.

### Step 3: Present

Show findings in a table, then ask which to delete and which were renamed/moved.

### Step 4: Act on user instructions

For **deletes**: Use `rm`.

For **merges** (renamed/moved projects):
1. Identify the target project folder (create if needed).
2. Move session files (`*.jsonl`) and session dirs (UUID-named) to the target.
3. Move `memory/` contents if present (don't overwrite existing).
4. Remove the now-empty source folder.

For **worktrees**: merge session files into the parent project folder, then delete.

## Rules

- Always present findings first. Do NOT delete or merge without user confirmation.
- After cleanup, list remaining project folders so user can verify.
