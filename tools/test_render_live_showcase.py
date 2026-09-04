"""Unit-test trim choices without invoking FFmpeg or fabricating footage."""

from __future__ import annotations

import unittest

from render_live_showcase import SHORT_SCENES, clip_window


class ClipWindowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scene = {
            "id": "edge-incidence",
            "startSec": 10.0,
            "endSec": 15.5,
            "settledSec": 12.0,
        }

    def test_short_edit_uses_one_second_after_settling(self) -> None:
        self.assertEqual(clip_window(self.scene, "short"), (12.25, 13.25))

    def test_hover_preserves_second_real_mouse_in(self) -> None:
        self.scene.update(id="hover-enclosure", endSec=18.0)
        self.assertEqual(clip_window(self.scene, "short"), (14.8, 15.8))

    def test_hover_requires_enough_source_footage_for_second_mouse_in(self) -> None:
        self.scene["id"] = "hover-enclosure"
        with self.assertRaisesRegex(ValueError, "Not enough settled footage"):
            clip_window(self.scene, "short")

    def test_full_edit_preserves_the_entire_scene(self) -> None:
        self.assertEqual(clip_window(self.scene, "full"), (10.0, 15.5))

    def test_insufficient_footage_raises_instead_of_silent_padding(self) -> None:
        self.scene["endSec"] = 13.0
        with self.assertRaisesRegex(ValueError, "Not enough settled footage"):
            clip_window(self.scene, "short")

    def test_exactly_one_second_of_footage_is_allowed(self) -> None:
        self.scene["endSec"] = 13.25
        self.assertEqual(clip_window(self.scene, "short"), (12.25, 13.25))

    def test_invalid_source_timestamps_are_rejected(self) -> None:
        for field, value in (
            ("startSec", -1),
            ("startSec", 13),
            ("settledSec", 16),
            ("endSec", 9),
        ):
            with self.subTest(field=field, value=value):
                scene = {**self.scene, field: value}
                with self.assertRaisesRegex(ValueError, "Invalid source timestamps"):
                    clip_window(scene, "short")

    def test_unknown_edit_profile_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown edit profile"):
            clip_window(self.scene, "accelerated")

    def test_short_story_contains_the_four_chapters(self) -> None:
        self.assertEqual(
            SHORT_SCENES,
            (
                "overview-enclosure",
                "overview-matrix",
                "edge-enclosure",
                "edge-incidence",
                "node-matrix",
                "node-incidence",
                "hover-enclosure",
            ),
        )


if __name__ == "__main__":
    unittest.main()
