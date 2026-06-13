# utils

Standalone utility skills.

## Skills

| Skill | What it does |
|-------|--------------|
| `ollama-vision` | Look at a local image: OCR, describe screenshots/photos, read diagrams or charts via a local vision model. Needs `python3`, `uv`, and a running Ollama. |
| `prune-projects` | Find stale `~/.claude/projects/` folders whose source dirs are gone, then merge renamed / delete dead. |

`prune-projects` is `user-invocable` (e.g. `/utils:prune-projects`); `ollama-vision` triggers automatically when you point at an image.
