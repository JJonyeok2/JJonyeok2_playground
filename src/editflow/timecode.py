"""Timeline timecode helpers."""

from __future__ import annotations


def format_timecode(total_seconds: int, *, fps: int = 30) -> str:
    """Format whole seconds as non-drop-frame HH:MM:SS:FF timecode."""
    if fps < 1:
        message = "fps must be 1 or greater"
        raise ValueError(message)
    seconds = max(0, int(total_seconds))
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remainder = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{remainder:02d}:00"
