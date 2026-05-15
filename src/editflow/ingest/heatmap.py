"""Replay heatmap ingestion."""

from __future__ import annotations

import csv
import json
from typing import TYPE_CHECKING

from editflow.models import HeatmapPoint

if TYPE_CHECKING:
    from pathlib import Path


def load_heatmap_points(path: Path) -> list[HeatmapPoint]:
    """Load heatmap rows from CSV or JSON sorted by playback second."""
    points = [
        HeatmapPoint(second=int(row["second"]), score=float(row["score"]))
        for row in _read_rows(path)
    ]
    return sorted(points, key=lambda point: point.second)


def _read_rows(path: Path) -> list[dict[str, object]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8", newline="") as file:
            return list(csv.DictReader(file))
    if suffix == ".json":
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            message = "heatmap JSON must be a list of objects"
            raise ValueError(message)
        return data
    message = f"unsupported heatmap file extension: {suffix}"
    raise ValueError(message)
