# Multi-turn conversation with the same image

When the user asks follow-up questions about the same image, cache the base64-encoded image instead of re-running the resize script. This avoids the 5-10 second resize penalty and the token cost of re-encoding.

1. First call (run the script to get resized image bytes):
   ```bash
   uv run scripts/vision_helper.py image.png "your prompt here" --output /tmp/result.txt
   cat /tmp/result.txt
   ```
   The script prints the response. For subsequent turns, you need the raw base64 — so run the resize manually and cache it:

   ```bash
   # Resize once, cache in a variable
   B64=$(python3 -c "
   from scripts.vision_helper import smart_resize
   import base64
   print(base64.b64encode(smart_resize('image.png')).decode())" 2>/dev/null)

   curl -s http://localhost:11434/api/generate \
     -d "{\"model\": \"gemma4:31b-cloud\", \"prompt\": \"follow-up question\", \"images\": [\"$B64\"]}"
   ```

2. Follow-up (reuse cached base64, no image data needed):
   ```bash
   curl -s http://localhost:11434/api/generate \
     -d "{\"model\": \"gemma4:31b-cloud\", \"prompt\": \"follow-up question\"}"
   ```