"""CSV sidecar report exporter."""

from __future__ import annotations

import csv
from io import StringIO
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from editflow.models import Marker


CSV_FIELDS = ["second", "grade", "color", "title", "memo", "evidence", "confidence"]


def build_marker_csv(markers: list[Marker]) -> str:
    """Build CSV report text for detected markers."""
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_FIELDS)
    writer.writeheader()

    for marker in markers:
        writer.writerow(
            {
                "second": marker.second,
                "grade": marker.grade.value,
                "color": marker.color.value,
                "title": marker.title,
                "memo": marker.memo,
                "evidence": ",".join(marker.evidence),
                "confidence": f"{marker.confidence:.4f}",
            }
        )

    return buffer.getvalue()


def write_marker_csv(markers: list[Marker], path: Path) -> None:
    """Write marker CSV report to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_marker_csv(markers), encoding="utf-8")
