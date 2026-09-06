"""Edit genuine browser recordings into bilingual Hyper-Knowledge tours.

The input is a Playwright recordVideo WebM and a timestamped interaction
timeline, not a sequence of still images. The default eight-second cut uses
six one-second scenes and a two-second, half-speed hover finale, with clean cuts.
The optional full edit retains the longer takes and restrained camera moves.
Requires Pillow and FFmpeg; neither is a package runtime dependency.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SIZE = (1920, 1280)
FPS = 24
GIF_FPS = 12
SHORT_HOVER_PLAYBACK_RATE = 0.5
BACKGROUND = "#f4f7f6"
INK = "#142e2a"
MUTED = "#61766f"
ACCENT = "#287460"
SCENES = (
    "overview-matrix",
    "overview-incidence",
    "overview-enclosure",
    "edge-enclosure",
    "edge-incidence",
    "edge-matrix",
    "node-matrix",
    "node-incidence",
    "node-enclosure",
    "hover-enclosure",
)
SHORT_SCENES = (
    "overview-enclosure",
    "overview-matrix",
    "edge-enclosure",
    "edge-incidence",
    "node-matrix",
    "node-incidence",
    "hover-enclosure",
)
SHORT_COPY = {
    "zh": {
        "titles": (
            "包络总览",
            "矩阵总览",
            "超边成员",
            "成员角色",
            "节点定位",
            "所属超边",
            "悬停高亮",
        ),
        "captions": (
            "一圈，一条超边",
            "一格，一次关联",
            "三苏 · 四个成员",
            "谁，在关系中扮演什么角色",
            "苏轼 · 定位关联",
            "一个节点，18 条超边",
            "当前关系清晰，其余淡出",
        ),
        "chapters": ("总览", "总览", "超边", "超边", "节点", "节点", "悬停"),
    },
    "en": {
        "titles": (
            "Enclosure overview",
            "Matrix overview",
            "Hyperedge members",
            "Member roles",
            "Locate a node",
            "Its hyperedges",
            "Hover to focus",
        ),
        "captions": (
            "One enclosure, one hyperedge",
            "One cell, one membership",
            "Three Su family · Four members",
            "Each member has a role",
            "Su Shi · Locate memberships",
            "One node, 18 hyperedges",
            "One relation in focus; the rest fades",
        ),
        "chapters": (
            "OVERVIEW",
            "OVERVIEW",
            "HYPEREDGE",
            "HYPEREDGE",
            "NODE",
            "NODE",
            "HOVER",
        ),
    },
}
COPY = {
    "en": {
        "titles": (
            "Read the whole graph",
            "See the membership structure",
            "Explore the enclosures",
            "Choose one hyperedge",
            "Every member, every role",
            "Locate the same hyperedge",
            "Follow one node",
            "Just its 18 hyperedges",
            "See the shared context",
            "Hover to bring one relation forward",
        ),
        "captions": (
            "Matrix overview: nodes in rows, hyperedges in columns.",
            "Incidence overview starts from the shared node and its hyperedges.",
            "Each colored enclosure represents one hyperedge.",
            "Select the Three Su family hyperedge to reveal its four members.",
            "The same four members, connected through their roles in one relation.",
            "Switch to the matrix without losing the selected hyperedge.",
            "Select Su Shi and locate his memberships across the matrix.",
            "Focus on Su Shi and the 18 hyperedges he belongs to.",
            "The enclosure view preserves the context of those memberships.",
            "A light fill highlights this hyperedge; unrelated elements fade back.",
        ),
        "chapters": (
            "OVERVIEW",
            "OVERVIEW",
            "OVERVIEW",
            "ONE HYPEREDGE",
            "ONE HYPEREDGE",
            "ONE HYPEREDGE",
            "ONE NODE",
            "ONE NODE",
            "ONE NODE",
            "HOVER FOCUS",
        ),
    },
    "zh": {
        "titles": (
            "先读清整张图",
            "看见成员与关系",
            "展开高阶结构",
            "选中一条超边",
            "成员与角色，一一对应",
            "在矩阵中定位同一条超边",
            "沿着一个节点阅读",
            "只看它所属的 18 条超边",
            "保留共享的关系上下文",
            "鼠标移入，让当前关系浮现",
        ),
        "captions": (
            "关联矩阵总览：行对应节点，列对应超边。",
            "关联总览：从共享节点出发，查看它所属的超边。",
            "每个彩色包络，对应一条完整的超边。",
            "选中“三苏家族与文学群体”，只展示这条超边的四个成员。",
            "同样的四个成员，以各自在关系中的角色连接。",
            "切换到关联矩阵，保留当前选中的超边。",
            "选中苏轼，在矩阵中定位他所属的关系。",
            "聚焦苏轼，以及他所属的 18 条超边。",
            "包络视图保留这些成员关系的共享上下文。",
            "超边浅色填充，关联节点保持清晰，其余元素退到背景。",
        ),
        "chapters": (
            "结构总览",
            "结构总览",
            "结构总览",
            "一条超边",
            "一条超边",
            "一条超边",
            "一个节点",
            "一个节点",
            "一个节点",
            "悬停聚焦",
        ),
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command: list[str]) -> None:
    completed = subprocess.run(
        command, capture_output=True, text=True, encoding="utf-8", check=False
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr[-10000:])


def overlay(
    locale: str, number: int, out: Path, font: Path, bold: Path, edit: str = "short"
) -> None:
    """Draw only editorial furniture; the center stays transparent for video."""
    copy = (SHORT_COPY if edit == "short" else COPY)[locale]
    total = len(copy["titles"])
    image = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    brand_font = ImageFont.truetype(str(bold), 25)
    title_font = ImageFont.truetype(str(bold), 30)
    caption_font = ImageFont.truetype(str(font), 24)
    micro_font = ImageFont.truetype(str(font), 16)
    draw.rectangle((0, 0, 1919, 72), fill=BACKGROUND)
    draw.rectangle((0, 1206, 1919, 1279), fill=BACKGROUND)
    draw.text((38, 25), "Hyper-Knowledge", font=brand_font, fill=INK)
    draw.line((290, 23, 290, 51), fill="#d2dfd8", width=2)
    title = copy["titles"][number]
    assert title_font.getlength(title) <= 1180, title
    draw.text((316, 22), title, font=title_font, fill=INK)
    draw.text(
        (1880, 14), copy["chapters"][number], font=micro_font, fill=MUTED, anchor="ra"
    )
    draw.text(
        (1880, 37),
        f"{number + 1:02d} / {total:02d}",
        font=micro_font,
        fill=ACCENT,
        anchor="ra",
    )
    draw.line((38, 1219, 1881, 1219), fill="#d9e3dd", width=1)
    caption = copy["captions"][number]
    assert caption_font.getlength(caption) <= 1800, caption
    draw.text((38, 1235), caption, font=caption_font, fill=MUTED)
    # A compact chapter strip is independent of the application's own controls.
    for index in range(total):
        step = 1844 / total
        left = 38 + index * step
        draw.rectangle(
            (left, 69, left + step - 12, 72),
            fill=ACCENT if index == number else "#dce6e0",
        )
    image.save(out)


def fit_frame(width: int, height: int) -> tuple[int, int, int, int]:
    scale = min(1880 / width, 1132 / height)
    fitted_width = int(width * scale) // 2 * 2
    fitted_height = int(height * scale) // 2 * 2
    return (
        fitted_width,
        fitted_height,
        (SIZE[0] - fitted_width) // 2,
        74 + (1132 - fitted_height) // 2,
    )


def zoom_filter(
    scene: dict, width: int, height: int, local_settle: float
) -> tuple[str, dict]:
    # The raw interaction always appears unzoomed first. The subsequent camera
    # move is explicitly editorial and does not alter the DOM or graph geometry.
    amount = 0.10 if scene["id"] in {"edge-incidence", "node-incidence"} else 0.0
    canvas = scene.get("bounds", {}).get("canvas", {})
    center_x = float(canvas.get("x", 0)) + float(canvas.get("width", width)) / 2
    center_y = float(canvas.get("y", 0)) + float(canvas.get("height", height)) / 2
    center_x = min(width, max(0, center_x))
    center_y = min(height, max(0, center_y))
    begin = max(0.5, local_settle + 0.25)
    progress = f"min(1,max(0,(on/{FPS}-{begin:.6f})/1.8))"
    ease = f"({progress})*({progress})*(3-2*({progress}))"
    expression = (
        f"zoompan=z='1+{amount}*({ease})':"
        f"x='max(0,min(iw-iw/zoom,{center_x:.4f}-iw/zoom/2))':"
        f"y='max(0,min(ih-ih/zoom,{center_y:.4f}-ih/zoom/2))':"
        f"d=1:s={width}x{height}:fps={FPS}"
    )
    return expression, {
        "maximum_scale": 1 + amount,
        "starts_after_sec": begin,
        "center": [center_x, center_y],
        "duration_sec": 1.8,
    }


def make_gif(ffmpeg: Path, video: Path, target: Path, work: Path) -> None:
    palette = work / f"{video.stem}-palette.png"
    base = f"fps={GIF_FPS},scale=1200:800:flags=lanczos"
    run(
        [
            str(ffmpeg),
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(video),
            "-vf",
            f"{base},palettegen=max_colors=128:stats_mode=diff",
            "-frames:v",
            "1",
            str(palette),
        ]
    )
    run(
        [
            str(ffmpeg),
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(video),
            "-i",
            str(palette),
            "-lavfi",
            f"{base}[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3",
            "-loop",
            "0",
            str(target),
        ]
    )


def clip_window(scene: dict, edit: str) -> tuple[float, float]:
    """Trim waiting, not playback speed; keep the second real mouse-in on hover."""
    start, end, settled = (
        float(scene[key]) for key in ("startSec", "endSec", "settledSec")
    )
    if not (0 <= start <= settled <= end and start < end):
        raise ValueError(f"Invalid source timestamps: {scene['id']}")
    if edit == "full":
        return start, end
    if edit != "short":
        raise ValueError(f"Unknown edit profile: {edit}")
    clip_start = settled + 2.8 if scene["id"] == "hover-enclosure" else settled + 0.25
    if clip_start + 1.0 > end:
        raise ValueError(
            f"Not enough settled footage for a one-second cut: {scene['id']}"
        )
    return clip_start, clip_start + 1.0


def render_locale(args: argparse.Namespace, locale: str) -> dict:
    source = args.capture / locale
    timeline_path = source / "timeline.json"
    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
    assert timeline["locale"] == locale
    scenes = timeline["scenes"]
    assert tuple(scene["id"] for scene in scenes) == SCENES, (
        "Expected ten ordered real interaction scenes"
    )
    video_path = source / timeline["video"]
    assert video_path.is_file(), video_path
    raw_sha256 = sha256(video_path)
    source_workbench = timeline.get("source")
    if source_workbench:
        try:
            source_workbench = (
                Path(source_workbench).resolve().relative_to(ROOT).as_posix()
            )
        except ValueError:
            source_workbench = str(source_workbench)
    else:
        source_workbench = "examples/sushi-document-test/views/workbench.html"
    source_bundle = timeline.get("bundle")
    if source_bundle:
        try:
            source_bundle = Path(source_bundle).resolve().relative_to(ROOT).as_posix()
        except ValueError:
            source_bundle = str(source_bundle)
    old_manifest_path = args.out / "live-manifest.json"
    old_locale = {}
    if args.reuse_segments and old_manifest_path.exists():
        old_manifest = json.loads(old_manifest_path.read_text(encoding="utf-8"))
        old_locale = old_manifest.get("locales", {}).get(locale, {})
    reusable_source = (
        old_locale.get("source_recording_sha256") == raw_sha256
        and old_locale.get("edit_profile", "full") == args.edit
    )
    width, height = (
        int(timeline["viewport"]["width"]),
        int(timeline["viewport"]["height"]),
    )
    assert width % 2 == height % 2 == 0
    work = args.out / ".render-work" / locale / args.edit
    work.mkdir(parents=True, exist_ok=True)
    segments = []
    source_stills = []
    output_files = []
    current_frame = 0
    previous_end = 0.0
    fitted_w, fitted_h, frame_x, frame_y = fit_frame(width, height)
    # The gallery keeps every captured state, independent of the shorter film.
    for scene in scenes:
        start, end, settled = (
            float(scene[key]) for key in ("startSec", "endSec", "settledSec")
        )
        assert 0 <= start < end and start <= settled <= end
        assert start >= previous_end - 0.1, "Scene timestamps overlap unexpectedly"
        previous_end = end
        shot_path = source / scene["screenshot"]
        assert shot_path.is_file(), shot_path
        target_shot = args.out / f"{scene['id']}-{locale}.png"
        if shot_path.resolve() != target_shot.resolve():
            shutil.copy2(shot_path, target_shot)
        with Image.open(target_shot) as screenshot:
            dimensions = list(screenshot.size)
        source_stills.append(
            {
                "scene": scene["id"],
                "file": target_shot.name,
                "sha256": sha256(target_shot),
                "size": dimensions,
                "capture_time_sec": settled,
                "state": scene.get("state", {}),
            }
        )
    by_id = {scene["id"]: scene for scene in scenes}
    edit_ids = SHORT_SCENES if args.edit == "short" else SCENES
    for number, scene_id in enumerate(edit_ids):
        scene = by_id[scene_id]
        start, end = clip_window(scene, args.edit)
        settled = float(scene["settledSec"])
        playback_rate = (
            SHORT_HOVER_PLAYBACK_RATE
            if args.edit == "short" and scene_id == "hover-enclosure"
            else 1
        )
        count = math.floor((end - start) / playback_rate * FPS + 0.5)
        assert count >= FPS, "Each scene must have at least one second of footage"
        duration = count / FPS
        title_path = work / f"{number:02d}-overlay.png"
        segment_path = work / f"{number:02d}.mp4"
        previous_overlay_hash = sha256(title_path) if title_path.exists() else None
        overlay(locale, number, title_path, args.font, args.font_bold, args.edit)
        if args.edit == "short":
            zoom = "null"
            camera = {"maximum_scale": 1.0, "starts_after_sec": 0, "duration_sec": 0}
            transitions = ""
        else:
            zoom, camera = zoom_filter(scene, width, height, settled - start)
            transitions = (
                f"fade=t=in:st=0:d=0.20:color={BACKGROUND},"
                f"fade=t=out:st={duration - 0.20:.6f}:d=0.20:color={BACKGROUND},"
            )
        timing = (
            "setpts=PTS-STARTPTS"
            if playback_rate == 1
            else f"setpts=(PTS-STARTPTS)/{playback_rate}"
        )
        filters = (
            f"[0:v]trim=duration={end - start:.6f},{timing},fps={FPS},"
            f"{zoom},"
            f"scale={fitted_w}:{fitted_h}:flags=lanczos,"
            f"pad={SIZE[0]}:{SIZE[1]}:{frame_x}:{frame_y}:color={BACKGROUND}[video];"
            f"[video][1:v]overlay=0:0,"
            f"{transitions}"
            "setsar=1,format=yuv420p[out]"
        )
        filter_hash = hashlib.sha256(filters.encode("utf-8")).hexdigest()
        old_segments = old_locale.get("segments", [])
        old_segment = old_segments[number] if len(old_segments) > number else {}
        reuse = (
            reusable_source
            and segment_path.exists()
            and previous_overlay_hash == sha256(title_path)
            and old_segment.get("raw_start_sec") == start
            and old_segment.get("raw_end_sec") == end
            and old_segment.get("output_frames") == count
            and old_segment.get("editorial_camera") == camera
            and old_segment.get("filter_sha256") == filter_hash
        )
        print(
            f"{locale} {number + 1}/{len(edit_ids)} {scene['id']} ({duration:.2f}s){' [reused]' if reuse else ''}",
            flush=True,
        )
        if not reuse:
            run(
                [
                    str(args.ffmpeg),
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-y",
                    "-ss",
                    f"{start:.6f}",
                    "-i",
                    str(video_path),
                    "-i",
                    str(title_path),
                    "-filter_complex",
                    filters,
                    "-map",
                    "[out]",
                    "-an",
                    "-frames:v",
                    str(count),
                    "-r",
                    str(FPS),
                    "-c:v",
                    "libx264",
                    "-preset",
                    "fast",
                    "-crf",
                    "19",
                    "-pix_fmt",
                    "yuv420p",
                    "-movflags",
                    "+faststart",
                    str(segment_path),
                ]
            )
        segments.append(
            {
                "id": scene["id"],
                "raw_start_sec": start,
                "raw_end_sec": end,
                "raw_settled_sec": settled,
                "output_start_frame": current_frame,
                "output_frames": count,
                "output_duration_sec": duration,
                "editorial_camera": camera,
                "fade_through_background_sec": 0 if args.edit == "short" else 0.2,
                "playback_rate": playback_rate,
                "filter_sha256": filter_hash,
            }
        )
        current_frame += count
    concat_path = work / "segments.txt"
    # FFmpeg concat paths are relative to this file, avoiding shell quoting.
    concat_path.write_text(
        "".join(f"file '{index:02d}.mp4'\n" for index in range(len(edit_ids))),
        encoding="utf-8",
    )
    video = args.out / f"tour-{locale}.mp4"
    run(
        [
            str(args.ffmpeg),
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_path),
            "-c",
            "copy",
            "-bsf:v",
            "h264_metadata=sample_aspect_ratio=1/1",
            "-aspect",
            "3:2",
            "-movflags",
            "+faststart",
            str(video),
        ]
    )
    output_files.append(
        {
            "file": video.name,
            "sha256": sha256(video),
            "bytes": video.stat().st_size,
            "kind": "video",
            "size": list(SIZE),
            "fps": FPS,
            "frames": current_frame,
            "duration_sec": current_frame / FPS,
            "sample_aspect_ratio": "1:1",
            "display_aspect_ratio": "3:2",
        }
    )
    if not args.skip_gif:
        gif = args.out / f"tour-{locale}.gif"
        print(f"{locale}: encoding the {len(edit_ids)}-scene GIF", flush=True)
        make_gif(args.ffmpeg, video, gif, work)
        with Image.open(gif) as animation:
            gif_duration = 0
            for index in range(animation.n_frames):
                animation.seek(index)
                gif_duration += animation.info.get("duration", 0)
            output_files.append(
                {
                    "file": gif.name,
                    "sha256": sha256(gif),
                    "bytes": gif.stat().st_size,
                    "kind": "gif",
                    "size": list(animation.size),
                    "fps": GIF_FPS,
                    "frames": animation.n_frames,
                    "duration_sec": gif_duration / 1000,
                }
            )
    return {
        "locale": locale,
        "edit_profile": args.edit,
        "short_hover_playback_rate": SHORT_HOVER_PLAYBACK_RATE
        if args.edit == "short"
        else 1,
        "source_recording": f"capture/{locale}/{video_path.name}",
        "source_recording_sha256": raw_sha256,
        "timeline": f"capture/{locale}/timeline.json",
        "timeline_sha256": sha256(timeline_path),
        "source_workbench": source_workbench,
        "source_bundle": source_bundle,
        "source_counts": timeline.get("sourceCounts"),
        "source_workbench_sha256": timeline.get("sourceSha256"),
        "source_viewport": [width, height],
        "screenshots": source_stills,
        "segments": segments,
        "outputs": output_files,
    }


def fix_pixel_aspect(args: argparse.Namespace, manifest: dict, locale: str) -> None:
    """Repair an existing MP4 losslessly without touching its recorded frames."""
    item = manifest["locales"][locale]
    output = next(entry for entry in item["outputs"] if entry["kind"] == "video")
    video = args.out / output["file"]
    work = args.out / ".render-work" / locale
    work.mkdir(parents=True, exist_ok=True)
    backup = work / "before-square-pixels.mp4"
    if not backup.exists():
        shutil.copy2(video, backup)
    repaired = work / "square-pixels.mp4"
    run(
        [
            str(args.ffmpeg),
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(video),
            "-map",
            "0:v:0",
            "-an",
            "-c:v",
            "copy",
            "-bsf:v",
            "h264_metadata=sample_aspect_ratio=1/1",
            "-aspect",
            "3:2",
            "-movflags",
            "+faststart",
            str(repaired),
        ]
    )
    shutil.copy2(repaired, video)
    output.update(
        {
            "sha256": sha256(video),
            "bytes": video.stat().st_size,
            "sample_aspect_ratio": "1:1",
            "display_aspect_ratio": "3:2",
        }
    )
    print(f"{locale}: MP4 pixel aspect corrected losslessly; GIF unchanged", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--ffmpeg", type=Path, required=True)
    parser.add_argument("--locale", choices=("en", "zh"), action="append")
    parser.add_argument(
        "--edit",
        choices=("short", "full"),
        default="short",
        help="Six one-second scenes plus a half-speed hover (default), or ten full takes",
    )
    parser.add_argument("--font", type=Path, default=Path("C:/Windows/Fonts/msyh.ttc"))
    parser.add_argument(
        "--font-bold", type=Path, default=Path("C:/Windows/Fonts/msyhbd.ttc")
    )
    parser.add_argument("--skip-gif", action="store_true")
    parser.add_argument(
        "--fix-pixel-aspect",
        action="store_true",
        help="Losslessly repair existing MP4 display metadata; do not render or touch GIFs",
    )
    parser.add_argument(
        "--reuse-segments",
        action="store_true",
        help="Reuse existing segments with matching source, timing, caption and camera",
    )
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    manifest_path = args.out / "live-manifest.json"
    manifest = (
        json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest_path.exists()
        else {
            "schema": "hyper-knowledge.live-tour/v1",
            "provenance": "Real isolated-browser interaction recordings; no screenshot-based reenactments.",
            "editorial_changes": [
                "caption overlays",
                "aspect-preserving framing",
                "up to 1.10x camera zoom after settling",
                "fades through a plain background",
            ],
            "source_labels": "Original Chinese source labels are retained in both interface languages.",
            "qa": {
                "visual_review": "pending; use contact sheets and full-size captures"
            },
            "locales": {},
        }
    )
    # A new render invalidates previous perceptual approval, even when segment
    # caching reuses most frames. Review the newly assembled outputs again.
    manifest["qa"] = {"visual_review": "pending; review the newly rendered outputs"}
    if not args.fix_pixel_aspect:
        manifest["editorial_changes"] = [
            "caption overlays",
            "aspect-preserving framing",
            "six one-second scenes plus a two-second hover at half speed, with clean cuts"
            if args.edit == "short"
            else "ten longer takes with restrained camera zoom and background fades",
        ]
    for locale in args.locale or ("en", "zh"):
        if args.fix_pixel_aspect:
            fix_pixel_aspect(args, manifest, locale)
        else:
            manifest["locales"][locale] = render_locale(args, locale)
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(manifest_path, flush=True)


if __name__ == "__main__":
    main()
