"""Compose a bilingual editorial tour from verified workbench screenshots.

This does not automate the app or simulate interactions. All zooms and fades
are editorial camera movements applied to the original, unchanged captures.
Requires Pillow and an FFmpeg executable; these are optional media tools, not
Hyper-Knowledge runtime dependencies. See docs/assets/showcase/README.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets"
SIZE = (1600, 1000)
FPS = 24
HOLD = 6
FRAME = (38, 160, 1562, 916)
STAGES = ("enclosure", "incidence", "sources", "matrix")
COPY = {
    "en": {
        "steps": ("Structure", "Membership", "Sources", "Matrix"),
        "titles": (
            "See the higher-order structure.",
            "Focus on the connections that matter.",
            "Keep roles and sources in view.",
            "Read dense relationships, row by row.",
        ),
        "captions": (
            "Each colored enclosure represents one hyperedge in the Su Shi example.",
            "Su Shi and the ten hyperedges it belongs to, in one focused view.",
            "Membership roles and source references remain available alongside the graph.",
            "Rows are nodes. Columns are hyperedges. Colored cells mark membership.",
        ),
        "note": "REAL CAPTURES / EDITORIAL ZOOM",
    },
    "zh": {
        "steps": ("结构总览", "关联聚焦", "角色与来源", "关联矩阵"),
        "titles": (
            "看见完整的高阶结构。",
            "聚焦当前节点，读清所属超边。",
            "关系之外，保留角色与来源。",
            "密集关系，也能逐行读清。",
        ),
        "captions": (
            "以苏轼生平为例：每个彩色包络对应一条超边。",
            "当前只展示苏轼与其所属的 10 条超边。",
            "图谱旁保留成员角色与原始文档的来源记录。",
            "行是节点，列是超边；彩色单元格表示成员关系。",
        ),
        "note": "真实截图 / 剪辑放大",
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def smooth(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3 - 2 * value)


def interpolate(a: tuple, b: tuple, t: float) -> tuple:
    return tuple(x + (y - x) * t for x, y in zip(a, b))


class Tour:
    def __init__(self, locale: str, regular: Path, bold: Path):
        self.locale = locale
        self.copy = COPY[locale]
        self.dark = locale == "zh"
        self.bg = "#080f1b" if self.dark else "#f5f6f8"
        self.surface = "#0f1b2f" if self.dark else "#ffffff"
        self.ink = "#e8eef9" if self.dark else "#172235"
        self.muted = "#91a3bf" if self.dark else "#67748a"
        self.line = "#24354d" if self.dark else "#dce2e9"
        self.accent = "#9992ff" if self.dark else "#386bc1"
        self.fonts = {
            "brand": ImageFont.truetype(str(bold), 23),
            "title": ImageFont.truetype(str(bold), 36),
            "body": ImageFont.truetype(str(regular), 20),
            "step": ImageFont.truetype(str(regular), 16),
            "micro": ImageFont.truetype(str(regular), 13),
        }
        self.images = {
            view: Image.open(ASSETS / f"hyper-knowledge-{view}-{locale}.png").convert(
                "RGB"
            )
            for view in ("enclosure", "incidence", "matrix")
        }
        self.static = Image.new("RGB", SIZE, self.bg)
        draw = ImageDraw.Draw(self.static)
        draw.text((38, 29), "Hyper-Knowledge", self.ink, self.fonts["brand"])
        draw.line((38, 75, 1562, 75), fill=self.line, width=1)
        draw.text(
            (1562, 947), self.copy["note"], self.muted, self.fonts["micro"], anchor="ra"
        )
        self.validate_text()

    def validate_text(self):
        """Fail instead of silently clipping translated captions."""
        for title in self.copy["titles"]:
            assert self.fonts["title"].getlength(title) <= 1410, title
        for caption in self.copy["captions"]:
            assert self.fonts["body"].getlength(caption) <= 1190, caption

    def panel(self, canvas: Image.Image, view: str, crop: tuple, target=FRAME):
        source = self.images[view]
        x0, y0, x1, y1 = crop
        assert 0 <= x0 < x1 <= source.width and 0 <= y0 < y1 <= source.height
        left, top, right, bottom = target
        dims = (right - left, bottom - top)
        # Contain rather than stretch: node circles and topology keep their geometry.
        shot = source.crop(tuple(round(v) for v in crop))
        shot = ImageOps.contain(shot, dims, Image.Resampling.LANCZOS)
        card = Image.new("RGB", dims, self.surface)
        card.paste(shot, ((dims[0] - shot.width) // 2, (dims[1] - shot.height) // 2))
        mask = Image.new("L", dims)
        ImageDraw.Draw(mask).rounded_rectangle(
            (0, 0, dims[0] - 1, dims[1] - 1), radius=18, fill=255
        )
        canvas.paste(card, (left, top), mask)
        ImageDraw.Draw(canvas).rounded_rectangle(
            target, radius=18, outline=self.line, width=1
        )

    def frame(self, stage: int, seconds: float) -> Image.Image:
        image = self.static.copy()
        draw = ImageDraw.Draw(image)
        for i, name in enumerate(self.copy["steps"]):
            x = 848 + i * 180
            color = self.accent if i == stage else self.muted
            draw.text((x, 38), f"{i + 1:02d}  {name}", color, self.fonts["step"])
            if i == stage:
                draw.line((x, 74, x + 145, 74), fill=self.accent, width=3)
        draw.text((38, 95), self.copy["titles"][stage], self.ink, self.fonts["title"])
        draw.text(
            (38, 944), self.copy["captions"][stage], self.muted, self.fonts["body"]
        )
        zoom = smooth((seconds - 0.8) / 2.5)
        if stage == 0:
            self.panel(
                image,
                "enclosure",
                interpolate((0, 0, 1920, 1080), (270, 297, 1570, 932), zoom),
            )
        elif stage == 1:
            self.panel(
                image,
                "incidence",
                interpolate((170, 275, 1420, 932), (245, 300, 1335, 932), zoom),
            )
        elif stage == 2:
            self.panel(image, "incidence", (240, 290, 1335, 932), (38, 160, 1026, 916))
            self.panel(
                image,
                "incidence",
                interpolate((1543, 445, 1882, 925), (1546, 456, 1878, 916), zoom),
                (1050, 160, 1562, 916),
            )
        else:
            self.panel(
                image,
                "matrix",
                interpolate((150, 305, 1700, 1055), (340, 315, 1645, 930), zoom),
            )
        # Fade through the background at cuts. No messy overlap of two graph states.
        opacity = min(smooth(seconds / 0.28), smooth((HOLD - seconds) / 0.28))
        if opacity < 1:
            image = Image.blend(self.static, image, opacity)
        return image


def write_video(tour: Tour, destination: Path, ffmpeg: str):
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{SIZE[0]}x{SIZE[1]}",
        "-r",
        str(FPS),
        "-i",
        "-",
        "-an",
        "-c:v",
        "libx264",
        "-crf",
        "19",
        "-preset",
        "fast",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(destination),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    try:
        for stage, name in enumerate(STAGES):
            print(f"{tour.locale}: {name}", flush=True)
            for frame_no in range(FPS * HOLD):
                frame = tour.frame(stage, frame_no / FPS)
                process.stdin.write(frame.tobytes())
    finally:
        process.stdin.close()
    if process.wait() != 0:
        raise RuntimeError(f"FFmpeg failed: {destination}")


def write_gif(source: Path, destination: Path, ffmpeg: str):
    filters = (
        "fps=8,scale=960:-2:flags=lanczos,split[a][b];"
        "[a]palettegen=max_colors=80:stats_mode=diff[p];"
        "[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle"
    )
    subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(source),
            "-filter_complex",
            filters,
            "-loop",
            "0",
            str(destination),
        ],
        check=True,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ffmpeg", default=shutil.which("ffmpeg"))
    parser.add_argument("--font", type=Path, default=Path("C:/Windows/Fonts/msyh.ttc"))
    parser.add_argument(
        "--font-bold", type=Path, default=Path("C:/Windows/Fonts/msyhbd.ttc")
    )
    parser.add_argument("--out", type=Path, default=ASSETS / "showcase")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--stills-only", action="store_true")
    modes.add_argument(
        "--gif-only", action="store_true", help="Reuse existing MP4 and still files"
    )
    args = parser.parse_args()
    if not args.stills_only and not args.ffmpeg:
        parser.error("Pass --ffmpeg /path/to/ffmpeg or put FFmpeg on PATH")
    for font in (args.font, args.font_bold):
        if not font.is_file():
            parser.error(f"Provide a CJK-capable font file: {font}")
    args.out.mkdir(parents=True, exist_ok=True)
    capture_manifest = json.loads(
        (ASSETS / "hyper-knowledge-promo-manifest.json").read_text()
    )
    verified = []
    for item in capture_manifest["captures"]:
        source = ASSETS / item["file"]
        if sha256(source) != item["sha256"]:
            raise ValueError(f"Capture hash mismatch: {source}")
        with Image.open(source) as shot:
            assert shot.size == (1920, 1080), source
        verified.append(
            {"file": source.relative_to(ROOT).as_posix(), "sha256": sha256(source)}
        )
    outputs = []
    for locale in COPY:
        tour = Tour(locale, args.font, args.font_bold)
        for stage, name in enumerate(STAGES):
            path = args.out / f"{name}-{locale}.png"
            if not args.gif_only:
                tour.frame(stage, 3.8).save(path, optimize=True)
            outputs.append(path)
        if not args.stills_only:
            video = args.out / f"tour-{locale}.mp4"
            gif = args.out / f"tour-{locale}.gif"
            if not args.gif_only:
                write_video(tour, video, args.ffmpeg)
            write_gif(video, gif, args.ffmpeg)
            outputs.extend((video, gif))
    manifest = {
        "schema": "hyper-knowledge.editorial-tour/v1",
        "source_captures": verified,
        "method": "Unmodified real captures; aspect-preserving crops, camera zoom and fade-through-background.",
        "not_a_live_recording": True,
        "new_browser_capture": False,
        "source_capture_date": capture_manifest["generated_at"],
        "source_schema": capture_manifest["source_schema"],
        "duration_seconds": len(STAGES) * HOLD,
        "video": {"size": list(SIZE), "fps": FPS, "codec": "H.264", "audio": False},
        "gif": {"width": 960, "fps": 8, "colors": 80, "loop": True},
        "storyboard": [
            {"scene": name, "start_seconds": i * HOLD, "duration_seconds": HOLD}
            for i, name in enumerate(STAGES)
        ],
        "outputs": [
            {"file": p.name, "bytes": p.stat().st_size, "sha256": sha256(p)}
            for p in outputs
        ],
        "qa": {
            "source_hashes": "passed",
            "caption_bounds": "passed",
            "visual_review": "pending",
            "interactive_review": "not_performed",
        },
    }
    (args.out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {"output": str(args.out), "files": len(outputs)}, ensure_ascii=False
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
