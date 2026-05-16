"""Replay heatmap ingestion."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from editflow.models import HeatmapPoint


def load_heatmap_points(path: Path) -> list[HeatmapPoint]:
    """Load heatmap rows from CSV or JSON sorted by playback second."""
    return _rows_to_points(_read_rows(path))


def load_heatmap_points_from_text(text: str, filename: str) -> list[HeatmapPoint]:
    """Load heatmap rows from uploaded CSV or JSON text."""
    return _rows_to_points(_read_rows_from_text(text, filename))


def _rows_to_points(rows: list[dict[str, object]]) -> list[HeatmapPoint]:
    points = [
        HeatmapPoint(second=int(row["second"]), score=float(row["score"]))
        for row in rows
    ]
    return sorted(points, key=lambda point: point.second)


def _read_rows(path: Path) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8")
    return _read_rows_from_text(text, path.name)


def _read_rows_from_text(text: str, filename: str) -> list[dict[str, object]]:
    suffix = Path(filename).suffix.lower()
    if suffix == ".csv":
        return list(csv.DictReader(text.splitlines()))
    if suffix == ".json":
        data = json.loads(text)
        if not isinstance(data, list):
            message = "heatmap JSON must be a list of objects"
            raise ValueError(message)
        return data
    message = f"unsupported heatmap file extension: {suffix}"
    raise ValueError(message)
