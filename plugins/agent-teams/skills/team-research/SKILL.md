---
name: "team-research"
description: "Spin up a research agent team to explore a topic from multiple angles. No code changes."
user-invocable: true
argument-hint: "<topic or question>"
---

# Team Research

Create an agent team to research a topic from multiple angles. No code changes.

## Workflow

### Phase 1: FRAME (Lead only)
1. Read AGENTS.md at repo root for project context
2. Break the question into 2-4 independent research angles
3. If the question is too vague, ask the user for clarity before spawning

### Phase 2: SCAFFOLD (Lead only)
1. Use spawn_agent to create one agent per research angle
2. Each agent's prompt must include:
   - Their specific research questions
   - File paths and module names to investigate
   - Instruction: read-only, no code changes, cite file:line for all claims

### Phase 3: INVESTIGATE (Teammates)
1. Teammates explore code, read docs, run queries, but change nothing
2. Teammates share findings that affect other angles
3. Lead can redirect teammates mid-investigation if user provides new context

### Phase 4: SYNTHESIZE (Lead)
1. Wait for ALL teammates to report back
2. Collect findings, identify agreements and contradictions
3. Present to the user:
   - Key findings per angle
   - Where teammates agreed
   - Where they disagreed and why
   - 2-3 concrete options with trade-offs and a recommendation

### Phase 5: CLEANUP (Lead)
1. Close all teammates

## Team structure

- Default to 3 teammates
- Each gets a clear research role

## Rules

- NO code changes. Read-only exploration only
- NO git operations
- Teammates must cite file:line when stating facts about the codebase
