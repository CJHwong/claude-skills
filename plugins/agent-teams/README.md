# agent-teams

Multi-agent orchestration skills.

## Skills

| Skill | What it does |
|-------|--------------|
| `team-research` | Spin up a read-only research agent team to explore a topic from multiple angles, then synthesize agreements, disagreements, and options. |
| `team-implement` | Spin up an agent team to implement a task using a phased PRAR workflow (perceive, scaffold, reason, act, refine, cleanup). |

Both skills are `user-invocable`, so you can call them directly (e.g. `/agent-teams:team-research <topic>`) or just describe the task and let the skill trigger.
