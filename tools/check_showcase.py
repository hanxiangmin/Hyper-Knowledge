"""Verify media hashes, dimensions, timing, decode health, and local README links."""

import argparse
import hashlib
import io
import json
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "docs" / "assets" / "showcase"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ffmpeg", required=True)
    parser.add_argument("--contact-sheet", type=Path)
    args = parser.parse_args()
    manifest = json.loads((MEDIA / "manifest.json").read_text(encoding="utf-8"))
    for collection, folder in (("source_captures", ROOT), ("outputs", MEDIA)):
        for record in manifest[collection]:
            path = folder / record["file"]
            assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"], (
                path
            )
    summary = []
    for lang in ("en", "zh"):
        for stage in ("enclosure", "incidence", "sources", "matrix"):
            with Image.open(MEDIA / f"{stage}-{lang}.png") as image:
                assert image.size == (1600, 1000)
                image.load()
        with Image.open(MEDIA / f"tour-{lang}.gif") as gif:
            assert gif.size == (960, 600)
            assert gif.info["loop"] == 0
            duration = 0
            frames = gif.n_frames
            for i in range(frames):
                gif.seek(i)
                gif.load()
                duration += gif.info["duration"]
            assert abs(duration - 24000) <= 20, duration
        video = MEDIA / f"tour-{lang}.mp4"
        result = subprocess.run(
            [
                args.ffmpeg,
                "-v",
                "error",
                "-i",
                str(video),
                "-progress",
                "pipe:1",
                "-f",
                "null",
                "-",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        assert not result.stderr.strip(), result.stderr
        assert "progress=end" in result.stdout
        assert int(re.findall(r"frame=(\d+)", result.stdout)[-1]) == 576
        summary.append(
            {
                "locale": lang,
                "gif_frames": frames,
                "gif_duration_ms": duration,
                "video_frames": 576,
                "decode": "passed",
            }
        )
    for name in ("README.md", "README_ZH.md", "docs/assets/showcase/README.md"):
        file = ROOT / name
        content = file.read_text(encoding="utf-8")
        for target in re.findall(r"\]\((\.[^\s)]+)\)", content):
            assert (file.parent / target.split("#")[0]).exists(), (name, target)
    if args.contact_sheet:
        args.contact_sheet.parent.mkdir(parents=True, exist_ok=True)
        # Includes the held scenes and both sides of one cut in the encoded video.
        times = (3.8, 5.88, 6.12, 9.8, 15.8, 21.8)
        sheet = Image.new("RGB", (1800, 820), "#182333")
        draw = ImageDraw.Draw(sheet)
        for row, lang in enumerate(("en", "zh")):
            for col, seconds in enumerate(times):
                raw = subprocess.run(
                    [
                        args.ffmpeg,
                        "-v",
                        "error",
                        "-ss",
                        str(seconds),
                        "-i",
                        str(MEDIA / f"tour-{lang}.mp4"),
                        "-frames:v",
                        "1",
                        "-vf",
                        "scale=600:-1",
                        "-f",
                        "image2pipe",
                        "-vcodec",
                        "png",
                        "-",
                    ],
                    check=True,
                    capture_output=True,
                ).stdout
                image = Image.open(io.BytesIO(raw)).convert("RGB")
                # The contact sheet shows the first cut; all sampled frames are exported.
                if col < 3:
                    x, y = col * 600, row * 410
                    sheet.paste(image, (x, y + 30))
                    draw.text(
                        (x + 12, y + 8),
                        f"{lang.upper()} / {seconds:.2f}s",
                        fill="white",
                    )
                image.save(args.contact_sheet.parent / f"tour-frame-{lang}-{col}.png")
        sheet.save(args.contact_sheet)
    print(
        json.dumps({"hashes": "passed", "links": "passed", "media": summary}, indent=2)
    )


if __name__ == "__main__":
    main()
