---
name: "team-implement"
description: "Spin up an agent team for a task with structured workflow. Provide a ticket reference, task description, or both."
user-invocable: true
argument-hint: "<ticket reference and/or task description>"
---

# Team Implement

Create an agent team for a task. Provide a ticket reference, task description, or both.

## Workflow (PRAR)

The team follows a phased workflow. Do NOT skip phases.

### Phase 1: PERCEIVE (Lead only)
1. If a ticket reference is provided, fetch it for full context
2. Read AGENTS.md at repo root and in relevant directories
3. Identify the scope of work and split into parallel-safe pieces
4. If requirements are vague, ask the user for clarity before proceeding

### Phase 2: SCAFFOLD (Lead only)
1. Use spawn_agent to create each teammate
2. Each teammate's prompt must include:
   - File paths they own (no overlap between teammates)
   - Architecture context and interfaces they need to implement or consume
   - Existing files they MUST read before planning
   - Instructions to present plan, then wait for approval before coding

### Phase 3: REASON (Lead + Teammates)
1. Teammates investigate their area and submit plans
2. Lead reviews plans and approves or rejects
3. If a teammate raises a blocking question, lead investigates before answering
4. Lead presents the combined plan to the user and waits for approval
5. After user approval, teammates proceed to coding

### Phase 4: ACT (Teammates)
1. Each teammate writes tests alongside implementation
2. Each teammate runs tests on their own work before marking tasks complete
3. If a teammate gets stuck after 2-3 attempts, message the lead
4. Lead monitors progress and redirects as needed. Lead does NOT implement tasks
5. Teammates coordinate when their work produces shared interfaces

### Phase 5: REFINE (Lead)
1. Wait for ALL teammates to finish
2. Verify no file conflicts between teammates
3. Run the full test suite
4. Present a summary to the user of what was done

### Phase 6: CLEANUP (Lead)
1. Close all teammates

## Team structure

- Default to 3 teammates unless the task clearly needs more or fewer
- Each teammate gets a clear role name (e.g., "backend", "frontend", "tests")

## Rules

- Do NOT push, create PRs, or run git operations beyond what's needed for implementation
- Do NOT modify files outside the teammate's assigned scope
- Minimal changes only. No refactoring beyond what the task requires
- Stick to the repo's existing stack and patterns
