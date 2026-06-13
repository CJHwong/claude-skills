---
name: ollama-vision
description: >-
  Use this skill whenever the user asks you to look at an image on their
  machine — extract text (OCR), describe a screenshot or photo, read a diagram
  or chart, or answer questions about visual content. Trigger even if the
  user doesn't explicitly say "vision" or "OCR" — phrases like "what's in this
  screenshot", "read this image", "transcribe this photo", "what does this
  diagram show", or "can you see what's in this picture" all qualify. Also
  trigger when the user references an image file (.png, .jpg, .webp, .gif)
  with information they need extracted.
compatibility:
  requires: [python3, uv]
---

# Ollama Vision Skill

Route image understanding through a local Ollama vision model. Handles OCR, description, analysis, and visual Q&A.

## Workflow

### 1. Run the resize script

Images must be resized before sending to Ollama or they'll blow past context. The bundled `vision_helper.py` does this.

**First, `cd` into the skill directory** — the script path is relative to the skill dir, not its parent:

```
cd ollama-vision
uv run scripts/vision_helper.py /path/to/image.jpg "your prompt here"
```

The script resizes (area-target, minimum 700px short side, capped at 4096px long), compresses to JPEG, auto-selects `gemma4:31b-cloud`, calls the API, and prints the response.

**Set a generous bash timeout:** The 31B model on large images can take 60–120+ seconds. Always set the bash tool's `timeout` parameter to 180 (or higher) — **not** a `--timeout` flag on the script (the script doesn't accept one). Use it like this:

```json
{
  "command": "cd ollama-vision && uv run scripts/vision_helper.py /path/to/image.jpg \"your prompt\"",
  "timeout": 180
}
```

**If auto-detect fails, specify the model explicitly:** The auto-detection parses `ollama list` output and can silently fail (empty result). If you get a "no vision model found" error or a hang, pass `--model`:

```
uv run scripts/vision_helper.py /path/to/image.jpg "your prompt here" --model gemma4:31b-cloud
```

This also avoids the startup delay of listing all models — mildly faster.

### 2. Tailor the prompt to the user's intent

Don't default to OCR — match the prompt to what the user asked for:

- **OCR / text extraction:** "Transcribe all visible text exactly as written. Preserve the layout. Return only the text."
- **Description:** "Describe this image in detail. Include objects, people, setting, colors, text, and any notable details."
- **Analysis:** "Analyze this chart/diagram/screenshot — what key information does it convey?"
- **Q&A:** Ask the user's question directly.
- **Structured extraction:** "Extract all data from this image as a JSON object with keys: ..."

Pass a specific model with `--model gemma4:31b-cloud` if auto-detect doesn't pick the right one.

### 3. Present results cleanly

Present OCR text as-is (formatted tables, code blocks, or raw text depending on the content). For descriptions and analysis, add brief context about what was found. Let the user's request determine the format.

## Gotchas

- **Always `cd` into the skill directory first** — `uv run scripts/vision_helper.py` is a relative path, so you need to be inside the skill directory (not its parent).
- **Set the bash tool's `timeout` to 180+** — `vision_helper.py` has no `--timeout` flag; the bash tool's built-in `timeout` parameter controls how long the command may run. The script's internal API timeout is 300s, and large images on the 31B model routinely take >60s. A short bash timeout kills the command prematurely.
- **Pass `--model gemma4:31b-cloud` explicitly if auto-detect fails.** The auto-detection silently returns `None` if `ollama list` output doesn't parse cleanly.
- If the image is still too large (400 Bad Request), shrink it further with ImageMagick first: `magick convert -resize 50% input.png output.jpg`
- `gemma4:31b-cloud` must be pulled locally (`ollama pull gemma4:31b-cloud`) or the script will fail with "no vision model found."
- If the image path has spaces, quote it.
- For follow-up questions about the same image, cache the base64 string and reuse it — see `references/multi_turn.md`.

## When NOT to use this skill

- The image is a URL (use WebFetch instead)
- The user wants Claude's built-in vision (sensitive analysis, complex reasoning)
- The image format is corrupted or exotic (normalize with `magick convert` first)

## Troubleshooting

If the script fails or times out, follow this diagnostic chain:

1. **"No such file or directory" for the script** → You're in the wrong CWD. `cd` into the skill directory:
   ```
   cd ollama-vision
   ```

2. **Tool command times out** → Increase the bash tool's `timeout` parameter. A 2872×1730 image (~5MP) on `gemma4:31b-cloud` takes 60–120+ seconds. Start with `timeout: 180`. The script itself has no `--timeout` flag.

3. **"no vision model found"** → Either the model isn't pulled (`ollama pull gemma4:31b-cloud`), or auto-detect parsing failed. Explicitly pass `--model gemma4:31b-cloud`.

4. **403/400 Bad Request** → Image still too large. Shrink with ImageMagick:
   ```
   magick convert -resize 50% input.png output.jpg
   ```

5. **Still slow?** The default image at 2872×1730 exceeds MAX_PIXELS (4MP) and triggers resize+compress loops. For large screenshots, manually shrink first.