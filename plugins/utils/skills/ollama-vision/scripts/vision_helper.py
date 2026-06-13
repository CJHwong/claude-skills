# /// script
# dependencies = [
#   "Pillow>=10.0",
# ]
# ///

"""
Ollama Vision Helper — resize image + call Ollama vision API in one shot.

Usage:
    uv run scripts/vision_helper.py <image_path> <prompt>
    uv run scripts/vision_helper.py <image_path> <prompt> --model <model_name>
    uv run scripts/vision_helper.py <image_path> <prompt> --output result.txt

The script automatically:
  1. Resizes/compresses the image to fit the model's context window (~100k token budget)
  2. Picks the best available vision model if none specified
  3. Reassembles streaming NDJSON output so you get clean text back

Options:
    --model NAME    Specify Ollama vision model (default: auto-detect)
    --output FILE   Write result to FILE instead of stdout
    --help          Show this help message and exit
"""

import argparse
import base64
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from io import BytesIO
from PIL import Image

OLLAMA_URL = "http://localhost:11434/api/generate"
MAX_IMAGE_FILE_SIZE = 350 * 1024
MAX_PIXELS = 2048 * 2048
MIN_SHORT = 700
MAX_LONG = 4096
VISION_MODEL_PRIORITY = [
    "gemma4:31b-cloud",
]


def find_vision_model() -> str | None:
    """Return the highest-priority vision model currently pulled in Ollama."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return None
        available = [line.split()[0] for line in result.stdout.strip().split("\n")[1:]
                     if line.strip()]
        for candidate in VISION_MODEL_PRIORITY:
            if candidate in available:
                return candidate
        return None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def smart_resize(image_path: str) -> bytes:
    """Resize and compress image to fit the token budget while preserving readability."""
    img = Image.open(image_path)
    w, h = img.size

    if w * h > MAX_PIXELS:
        scale = (MAX_PIXELS / (w * h)) ** 0.5
        new_w, new_h = int(w * scale), int(h * scale)
        if min(w, h) >= MIN_SHORT and min(new_w, new_h) < MIN_SHORT:
            fix = MIN_SHORT / min(new_w, new_h)
            new_w = int(new_w * fix)
            new_h = int(new_h * fix)
        if max(new_w, new_h) > MAX_LONG:
            cap = MAX_LONG / max(new_w, new_h)
            new_w, new_h = int(new_w * cap), int(new_h * cap)
        img = img.resize((new_w, new_h), Image.LANCZOS)

    if img.mode in ("RGBA", "P"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        alpha = img.split()[-1] if img.mode == "RGBA" else None
        bg.paste(img, mask=alpha)
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")

    buf = BytesIO()
    quality = 85
    img.save(buf, format="JPEG", quality=quality)
    data = buf.getvalue()

    while len(data) > MAX_IMAGE_FILE_SIZE:
        if quality > 15 and min(img.size) > 400:
            quality -= 10
        else:
            w, h = img.size
            img = img.resize((int(w * 0.85), int(h * 0.85)), Image.LANCZOS)
        buf.seek(0)
        buf.truncate()
        img.save(buf, format="JPEG", quality=max(quality, 10))
        data = buf.getvalue()

    return data


def call_ollama(model: str, image_b64: str, prompt: str) -> str:
    """Call Ollama generate API and reassemble streaming response."""
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "images": [image_b64],
        "stream": True,
    }).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            fragments = []
            for line in resp:
                raw = line.strip()
                if not raw:
                    continue
                try:
                    chunk = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                fragments.append(chunk.get("response", ""))
                if chunk.get("done"):
                    break
            return "".join(fragments)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Ollama API error {e.code}: {e.reason}\n{body}"
        ) from e
    except urllib.error.URLError as e:
        raise RuntimeError(
            f"Cannot connect to Ollama at {OLLAMA_URL}. Is it running?\n{e.reason}"
        ) from e


def main():
    parser = argparse.ArgumentParser(
        description="Resize image and call Ollama vision API in one shot.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run scripts/vision_helper.py screenshot.png "transcribe all text"
  uv run scripts/vision_helper.py photo.jpg "describe this image" --output result.txt
  uv run scripts/vision_helper.py chart.png "explain this chart" --model gemma4:31b-cloud
""",
    )
    parser.add_argument("image_path", help="Path to the image file (.png, .jpg, .webp, .gif)")
    parser.add_argument("prompt", help="What to ask about the image")
    parser.add_argument("--model", help="Ollama vision model to use (default: auto-detect)")
    parser.add_argument("--output", help="Write result to file instead of stdout")
    args = parser.parse_args()

    if not os.path.isfile(args.image_path):
        print(f"Error: image not found: {args.image_path}", file=sys.stderr)
        sys.exit(1)

    model = args.model or find_vision_model()
    if not model:
        print(
            "Error: no vision model found.\n"
            "  Run: ollama pull gemma4:31b-cloud",
            file=sys.stderr,
        )
        sys.exit(1)

    image_data = smart_resize(args.image_path)
    image_b64 = base64.b64encode(image_data).decode("utf-8")
    result = call_ollama(model, image_b64, args.prompt)

    if args.output:
        with open(args.output, "w") as f:
            f.write(result)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(result)


if __name__ == "__main__":
    main()