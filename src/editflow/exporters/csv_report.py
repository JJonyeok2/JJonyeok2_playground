"""CSV sidecar report exporter."""

from __future__ import annotations

import csv
from io import StringIO
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from editflow.models import Marker

from editflow.timecode import format_timecode

CSV_FIELDS = [
    "second",
    "timecode",
    "grade",
    "color",
    "title",
    "memo",
    "evidence",
    "confidence",
]


def build_marker_csv(markers: list[Marker], *, fps: int = 30) -> str:
    """Build CSV report text for detected markers."""
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_FIELDS)
    writer.writeheader()

    for marker in markers:
        writer.writerow(
            {
                "second": marker.second,
                "timecode": format_timecode(marker.second, fps=fps),
                "grade": marker.grade.value,
                "color": marker.color.value,
                "title": marker.title,
                "memo": marker.memo,
                "evidence": ",".join(marker.evidence),
                "confidence": f"{marker.confidence:.4f}",
            }
        )

    return buffer.getvalue()


def write_marker_csv(markers: list[Marker], path: Path, *, fps: int = 30) -> None:
    """Write marker CSV report to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_marker_csv(markers, fps=fps), encoding="utf-8")
