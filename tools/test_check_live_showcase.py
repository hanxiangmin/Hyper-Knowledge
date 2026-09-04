"""Bounded editorial-contract tests; media decoding is covered by the CLI."""

from __future__ import annotations

import copy
import unittest

from check_live_showcase import SCENES, SHORT_SCENES, check_edit


def fixture(
    profile: str = "short", hover_rate: float | None = None
) -> tuple[dict, dict]:
    timeline = {
        "scenes": [
            {
                "id": scene,
                "startSec": index * 6.0,
                "endSec": index * 6.0 + 5.5,
                "settledSec": index * 6.0 + 1.4,
            }
            for index, scene in enumerate(SCENES)
        ]
    }
    source = {scene["id"]: scene for scene in timeline["scenes"]}
    order = SHORT_SCENES if profile == "short" else SCENES
    seconds = 1 if profile == "short" else 5.5
    segments = []
    cursor = 0
    for key in order:
        scene = source[key]
        if profile == "short":
            start = scene["settledSec"] + (2.8 if key == "hover-enclosure" else 0.25)
        else:
            start = scene["startSec"]
        rate = (
            hover_rate
            if profile == "short"
            and key == "hover-enclosure"
            and hover_rate is not None
            else 1
        )
        output_seconds = seconds / rate
        segment = {
            "id": key,
            "raw_start_sec": start,
            "raw_end_sec": start + seconds,
            "raw_settled_sec": scene["settledSec"],
            "output_start_frame": cursor,
            "output_frames": int(output_seconds * 24),
            "output_duration_sec": output_seconds,
            "editorial_camera": {"maximum_scale": 1},
            "playback_rate": rate,
            "fade_through_background_sec": 0 if profile == "short" else 0.2,
        }
        segments.append(segment)
        cursor += segment["output_frames"]
    duration = cursor / 24
    item = {
        "edit_profile": profile,
        "screenshots": [{"scene": key} for key in SCENES],
        "segments": segments,
        "outputs": [
            {
                "kind": "video",
                "fps": 24,
                "frames": int(duration * 24),
                "duration_sec": duration,
            }
        ],
    }
    if hover_rate is not None:
        item["short_hover_playback_rate"] = hover_rate
    return item, timeline


class CheckEditTests(unittest.TestCase):
    def test_short_edit_has_seven_one_second_clips(self) -> None:
        item, timeline = fixture()
        self.assertEqual(check_edit(item, timeline), 168)

    def test_final_hover_can_be_half_speed_for_two_seconds(self) -> None:
        item, timeline = fixture(hover_rate=0.5)
        self.assertEqual(check_edit(item, timeline), 192)
        self.assertEqual(item["segments"][-1]["output_duration_sec"], 2)
        self.assertTrue(
            all(segment["playback_rate"] == 1 for segment in item["segments"][:-1])
        )
        self.assertTrue(
            all(segment["output_frames"] == 24 for segment in item["segments"][:-1])
        )

    def test_slow_hover_must_be_explicit_in_manifest(self) -> None:
        item, _ = fixture(hover_rate=0.5)
        del item["short_hover_playback_rate"]
        with self.assertRaises(AssertionError):
            check_edit(item)

    def test_hover_rate_must_match_segment_rate(self) -> None:
        item, _ = fixture(hover_rate=0.5)
        item["segments"][-1]["playback_rate"] = 1
        with self.assertRaises(AssertionError):
            check_edit(item)

    def test_only_hover_can_be_slowed(self) -> None:
        item, _ = fixture(hover_rate=0.5)
        for index in range(len(item["segments"]) - 1):
            with self.subTest(scene=item["segments"][index]["id"]):
                changed = copy.deepcopy(item)
                changed["segments"][index]["playback_rate"] = 0.5
                with self.assertRaises(AssertionError):
                    check_edit(changed)

    def test_hover_rejects_unrequested_rates(self) -> None:
        item, _ = fixture(hover_rate=0.5)
        for rate in (0, 0.25, 2):
            with self.subTest(rate=rate):
                changed = copy.deepcopy(item)
                changed["short_hover_playback_rate"] = rate
                with self.assertRaises(AssertionError):
                    check_edit(changed)

    def test_nonchronological_edit_order_is_supported(self) -> None:
        item, timeline = fixture()
        self.assertGreater(
            item["segments"][0]["raw_start_sec"],
            item["segments"][1]["raw_start_sec"],
        )
        self.assertEqual(check_edit(item, timeline), 168)

    def test_full_source_gallery_is_required_even_for_short_edit(self) -> None:
        item, _ = fixture()
        item["screenshots"].pop()
        with self.assertRaises(AssertionError):
            check_edit(item)

    def test_edit_order_cannot_change_silently(self) -> None:
        item, _ = fixture()
        item["segments"][0]["id"] = "overview-incidence"
        with self.assertRaises(AssertionError):
            check_edit(item)

    def test_one_second_cannot_be_replaced_with_sped_up_footage(self) -> None:
        item, _ = fixture()
        item["segments"][0]["raw_end_sec"] += 1
        with self.assertRaises(AssertionError):
            check_edit(item)

    def test_short_edit_rejects_fades_speed_changes_and_extra_frames(self) -> None:
        item, _ = fixture()
        for key, value in (
            ("fade_through_background_sec", 0.2),
            ("playback_rate", 2),
            ("output_frames", 25),
            ("output_duration_sec", 1.5),
        ):
            with self.subTest(field=key):
                changed = copy.deepcopy(item)
                changed["segments"][0][key] = value
                with self.assertRaises(AssertionError):
                    check_edit(changed)

    def test_trim_must_remain_inside_its_source_scene(self) -> None:
        item, timeline = fixture()
        target = item["segments"][0]
        target["raw_start_sec"] += 4
        target["raw_end_sec"] += 4
        with self.assertRaises(AssertionError):
            check_edit(item, timeline)

    def test_original_settled_time_may_precede_trim_start(self) -> None:
        item, timeline = fixture()
        target = item["segments"][0]
        self.assertLess(target["raw_settled_sec"], target["raw_start_sec"])
        self.assertEqual(check_edit(item, timeline), 168)

    def test_source_settling_timestamp_cannot_be_rewritten(self) -> None:
        item, timeline = fixture()
        item["segments"][0]["raw_settled_sec"] += 1
        with self.assertRaises(AssertionError):
            check_edit(item, timeline)

    def test_output_frame_sequence_has_no_gap(self) -> None:
        item, _ = fixture()
        item["segments"][2]["output_start_frame"] += 1
        with self.assertRaises(AssertionError):
            check_edit(item)

    def test_old_full_edit_profile_remains_compatible(self) -> None:
        item, timeline = fixture("full")
        del item["edit_profile"]
        for segment in item["segments"]:
            del segment["playback_rate"]
        self.assertEqual(check_edit(item, timeline), 1320)

    def test_unknown_profile_is_not_treated_as_full(self) -> None:
        item, _ = fixture()
        item["edit_profile"] = "unknown"
        with self.assertRaises(AssertionError):
            check_edit(item)


if __name__ == "__main__":
    unittest.main()
