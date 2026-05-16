"""Tests for timeline timecode formatting."""

from editflow.timecode import format_timecode


def test_format_timecode_uses_non_drop_frame_shape():
    assert format_timecode(3661, fps=30) == "01:01:01:00"
