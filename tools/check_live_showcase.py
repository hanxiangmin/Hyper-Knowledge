"""Validate live-tour edits and the complete ten-state source gallery.

Technical checks are separate from visual acceptance. The generated contact
sheets assist review; they do not claim to detect every overlap or tiny label.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

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


def check_edit(item: dict, timeline: dict | None = None) -> int:
    """Check editorial timing independently of decoding or source-file access."""
    profile = item.get("edit_profile", "full")
    assert profile in {"short", "full"}, f"Unknown edit profile: {profile}"
    # Older short manifests use seven normal-speed clips. Only the final hover
    # may be slowed, and its declared rate must match its measured duration.
    hover_rate = item.get("short_hover_playback_rate", 1)
    if profile == "short":
        assert hover_rate in {0.5, 1}, f"Unsupported hover rate: {hover_rate}"
    expected = SHORT_SCENES if profile == "short" else SCENES
    assert tuple(segment["id"] for segment in item["segments"]) == expected
    assert tuple(shot["scene"] for shot in item["screenshots"]) == SCENES
    source_scenes = {}
    if timeline is not None:
        assert tuple(scene["id"] for scene in timeline["scenes"]) == SCENES
        source_scenes = {scene["id"]: scene for scene in timeline["scenes"]}
    video = next(output for output in item["outputs"] if output["kind"] == "video")
    cursor = 0
    for segment in item["segments"]:
        assert segment["output_start_frame"] == cursor
        assert (
            isinstance(segment["output_frames"], int) and segment["output_frames"] > 0
        )
        assert 1 <= segment["editorial_camera"]["maximum_scale"] <= 1.15
        assert (
            abs(
                segment["output_frames"] / video["fps"] - segment["output_duration_sec"]
            )
            < 0.001
        )
        raw_start, raw_end = segment["raw_start_sec"], segment["raw_end_sec"]
        assert raw_end > raw_start >= 0
        if profile == "short":
            rate = hover_rate if segment["id"] == "hover-enclosure" else 1
            seconds = 1 / rate
            assert video["fps"] == 24
            assert segment["output_frames"] == int(seconds * 24)
            assert abs(segment["output_duration_sec"] - seconds) < 0.001
            assert abs(raw_end - raw_start - 1) < 0.001
            assert segment["playback_rate"] == rate
            assert segment["fade_through_background_sec"] == 0
        if source_scenes:
            scene = source_scenes[segment["id"]]
            assert raw_start >= scene["startSec"] - 0.001
            assert raw_end <= scene["endSec"] + 0.001
            assert abs(segment["raw_settled_sec"] - scene["settledSec"]) < 0.001
        cursor += segment["output_frames"]
    assert cursor == video["frames"]
    assert abs(cursor / video["fps"] - video["duration_sec"]) < 0.001
    if profile == "short":
        duration = len(SHORT_SCENES) - 1 + 1 / hover_rate
        assert cursor == int(duration * 24)
        assert abs(video["duration_sec"] - duration) < 0.001
    return cursor


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def decode_frames(ffmpeg: Path, path: Path) -> tuple[int, list[int], float]:
    """Decode every MP4 frame, not just a header or a thumbnail."""
    result = subprocess.run(
        [
            str(ffmpeg),
            "-v",
            "error",
            "-i",
            str(path),
            "-map",
            "0:v:0",
            "-an",
            "-f",
            "framemd5",
            "-",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0 and not result.stderr.strip(), result.stderr[-5000:]
    dimension_match = re.search(r"#dimensions 0:\s*(\d+)x(\d+)", result.stdout)
    timebase_match = re.search(r"#tb 0:\s*(\d+)/(\d+)", result.stdout)
    assert dimension_match and timebase_match, result.stdout[:1000]
    rows = [
        line for line in result.stdout.splitlines() if line and not line.startswith("#")
    ]
    assert rows
    numerator, denominator = map(int, timebase_match.groups())
    ticks = sum(int(row.split(",")[3]) for row in rows)
    return (
        len(rows),
        list(map(int, dimension_match.groups())),
        ticks * numerator / denominator,
    )


def check_pixel_aspect(ffmpeg: Path, path: Path, dimensions: list[int]) -> None:
    """Check actual H.264/container display metadata, not encoded size alone."""
    result = subprocess.run(
        [
            str(ffmpeg),
            "-hide_banner",
            "-i",
            str(path),
            "-map",
            "0:v:0",
            "-frames:v",
            "1",
            "-an",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0, result.stderr[-5000:]
    input_header = result.stderr.split("Output #0", 1)[0]
    stream_line = next(line for line in input_header.splitlines() if "Video:" in line)
    assert f"{dimensions[0]}x{dimensions[1]}" in stream_line, stream_line
    ratios = re.findall(r"SAR (\d+):(\d+)", stream_line)
    assert ratios and all(int(n) == int(d) for n, d in ratios), stream_line
    display_ratios = re.findall(r"DAR (\d+):(\d+)", stream_line)
    assert display_ratios and all(
        int(n) * dimensions[1] == int(d) * dimensions[0] for n, d in display_ratios
    ), stream_line


def frame_image(ffmpeg: Path, path: Path, second: float) -> Image.Image:
    result = subprocess.run(
        [
            str(ffmpeg),
            "-v",
            "error",
            "-ss",
            f"{second:.6f}",
            "-i",
            str(path),
            "-frames:v",
            "1",
            "-f",
            "image2pipe",
            "-vcodec",
            "png",
            "-",
        ],
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr.decode("utf-8", "replace")
    return Image.open(io.BytesIO(result.stdout)).convert("RGB")


def contact_sheet(
    ffmpeg: Path, root: Path, locale: str, item: dict, destination: Path
) -> Path:
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 20)
    rows = (len(item["segments"]) + 1) // 2
    sheet = Image.new("RGB", (1336, 90 + rows * 472), "#f4f7f6")
    draw = ImageDraw.Draw(sheet)
    draw.text(
        (24, 18),
        f"Hyper-Knowledge / {locale.upper()} / real recording samples",
        fill="#142e2a",
        font=font,
    )
    video_entry = next(
        output for output in item["outputs"] if output["kind"] == "video"
    )
    video = root / video_entry["file"]
    for index, segment in enumerate(item["segments"]):
        start = segment["output_start_frame"] / video_entry["fps"]
        duration = segment["output_duration_sec"]
        # Short cuts show the midpoint; full clips sample beyond the camera move.
        offset = (
            duration / 2
            if duration <= 1
            else min(duration - 0.65, max(duration * 0.68, 2.7))
        )
        if item.get("edit_profile") == "short" and segment["id"] == "hover-enclosure":
            offset = duration * 0.85
        second = start + offset
        picture = ImageOps.contain(
            frame_image(ffmpeg, video, second), (632, 422), Image.Resampling.LANCZOS
        )
        x, y = 24 + (index % 2) * 664, 68 + (index // 2) * 472
        sheet.paste(picture, (x, y))
        draw.text(
            (x, y + 429),
            f"{index + 1:02d}  {segment['id']}  /  {second:.1f}s",
            fill="#142e2a",
            font=font,
        )
    destination.mkdir(parents=True, exist_ok=True)
    path = destination / f"contact-sheet-{locale}.jpg"
    sheet.save(path, quality=93)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--ffmpeg", type=Path, required=True)
    parser.add_argument(
        "--capture",
        type=Path,
        help="Optional raw-recording root for source hash checks",
    )
    parser.add_argument("--contact-sheet", type=Path)
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Validate a single locale while the other renders",
    )
    parser.add_argument(
        "--skip-decode",
        action="store_true",
        help="Hash-only pass; not full technical acceptance",
    )
    args = parser.parse_args()
    manifest = json.loads(
        (args.assets / "live-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["schema"] == "hyper-knowledge.live-tour/v1"
    if not args.allow_partial:
        assert set(manifest["locales"]) == {"en", "zh"}
    checks = []
    edits = {}
    count = 0
    for locale, item in manifest["locales"].items():
        assert locale in {"en", "zh"}
        check_edit(item)
        assert len(item["screenshots"]) == 10
        for shot in item["screenshots"]:
            path = args.assets / shot["file"]
            assert path.is_file(), path
            assert sha256(path) == shot["sha256"], f"Screenshot hash mismatch: {path}"
            with Image.open(path) as image:
                image.load()
                assert list(image.size) == shot["size"]
                assert image.width >= 1600 and image.height >= 900, (
                    f"Unexpected capture size: {path}"
                )
            count += 1
        if args.capture:
            source = args.capture / locale
            timeline_path = source / "timeline.json"
            assert sha256(timeline_path) == item["timeline_sha256"]
            timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
            check_edit(item, timeline)
            assert sha256(source / timeline["video"]) == item["source_recording_sha256"]
            for shot, scene in zip(
                item["screenshots"], timeline["scenes"], strict=True
            ):
                assert sha256(source / scene["screenshot"]) == shot["sha256"]
        cursor = check_edit(item)
        kinds = {entry["kind"] for entry in item["outputs"]}
        if not args.allow_partial:
            assert kinds == {"video", "gif"}
        video_duration = next(
            output["duration_sec"]
            for output in item["outputs"]
            if output["kind"] == "video"
        )
        edits[locale] = {
            "profile": item.get("edit_profile", "full"),
            "short_hover_playback_rate": item.get("short_hover_playback_rate", 1),
            "video_scenes": len(item["segments"]),
            "video_duration_sec": video_duration,
            "gallery_states": len(item["screenshots"]),
        }
        for output in item["outputs"]:
            path = args.assets / output["file"]
            assert sha256(path) == output["sha256"], f"Media hash mismatch: {path}"
            assert path.stat().st_size == output["bytes"]
            if output["kind"] == "video":
                assert cursor == output["frames"]
                assert abs(cursor / output["fps"] - output["duration_sec"]) < 0.001
                check_pixel_aspect(args.ffmpeg, path, output["size"])
                assert output["sample_aspect_ratio"] == "1:1"
                assert output["display_aspect_ratio"] == "3:2"
                if not args.skip_decode:
                    frames, dimensions, duration = decode_frames(args.ffmpeg, path)
                    assert frames == output["frames"], (path, frames, output["frames"])
                    assert dimensions == output["size"]
                    assert abs(duration - output["duration_sec"]) < 0.06, (
                        duration,
                        output["duration_sec"],
                    )
            elif output["kind"] == "gif":
                with Image.open(path) as image:
                    assert image.info.get("loop") == 0, (
                        f"GIF must loop continuously: {path}"
                    )
                    assert image.n_frames == output["frames"]
                    assert list(image.size) == output["size"]
                    milliseconds = 0
                    for index in range(image.n_frames):
                        image.seek(index)
                        image.load()
                        milliseconds += image.info.get("duration", 0)
                duration = milliseconds / 1000
                assert abs(duration - output["duration_sec"]) < 0.011
                assert abs(duration - video_duration) < 0.3
                assert abs(output["frames"] - video_duration * output["fps"]) <= 2
            checks.append(
                {
                    "file": path.name,
                    "hash": "passed",
                    "square_pixels": "passed"
                    if output["kind"] == "video"
                    else "not applicable",
                    "decode": "passed"
                    if not args.skip_decode or output["kind"] == "gif"
                    else "not run",
                }
            )
        if args.contact_sheet:
            print(
                contact_sheet(
                    args.ffmpeg, args.assets, locale, item, args.contact_sheet
                )
            )
    report = {
        "schema": "hyper-knowledge.live-tour-qa/v1",
        "screenshots_checked": count,
        "ten_gallery_states_per_locale": True,
        "edits": edits,
        "media": checks,
        "source_hashes_checked": bool(args.capture),
        "visual_review": "Manual review is separate; no collision-free claim is implied.",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    (args.assets / "live-qa.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
