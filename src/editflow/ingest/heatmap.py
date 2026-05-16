"""Replay heatmap ingestion."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from editflow.models import HeatmapPoint

REQUIRED_COLUMNS = {"second", "score"}


def load_heatmap_points(path: Path) -> list[HeatmapPoint]:
    """Load heatmap rows from CSV or JSON sorted by playback second."""
    return _rows_to_points(_read_rows(path))


def load_heatmap_points_from_text(text: str, filename: str) -> list[HeatmapPoint]:
    """Load heatmap rows from uploaded CSV or JSON text."""
    return _rows_to_points(_read_rows_from_text(text, filename))


def _rows_to_points(rows: list[dict[str, object]]) -> list[HeatmapPoint]:
    points: list[HeatmapPoint] = []
    for row_number, row in enumerate(rows, start=1):
        _validate_columns(row, "heatmap", row_number)
        try:
            second = int(row["second"])
        except (TypeError, ValueError) as error:
            message = f"heatmap row {row_number} second must be an integer"
            raise ValueError(message) from error
        try:
            score = float(row["score"])
        except (TypeError, ValueError) as error:
            message = f"heatmap row {row_number} score must be a number"
            raise ValueError(message) from error
        points.append(HeatmapPoint(second=second, score=score))
    return sorted(points, key=lambda point: point.second)


def _read_rows(path: Path) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8")
    return _read_rows_from_text(text, path.name)


def _read_rows_from_text(text: str, filename: str) -> list[dict[str, object]]:
    suffix = Path(filename).suffix.lower()
    if suffix == ".csv":
        reader = csv.DictReader(text.splitlines())
        _validate_header(reader.fieldnames, "heatmap")
        return list(reader)
    if suffix == ".json":
        data = json.loads(text)
        if not isinstance(data, list):
            message = "heatmap JSON must be a list of objects"
            raise ValueError(message)
        return data
    message = f"unsupported heatmap file extension: {suffix}"
    raise ValueError(message)


def _validate_header(fieldnames: list[str] | None, label: str) -> None:
    columns = set(fieldnames or [])
    if not REQUIRED_COLUMNS.issubset(columns):
        _raise_missing_columns(label)


def _validate_columns(row: dict[str, object], label: str, row_number: int) -> None:
    if not REQUIRED_COLUMNS.issubset(row):
        _raise_missing_columns(label, row_number)


def _raise_missing_columns(label: str, row_number: int | None = None) -> None:
    target = f"{label} row {row_number}" if row_number is not None else f"{label} rows"
    message = f"{target} must include columns: {', '.join(sorted(REQUIRED_COLUMNS))}"
    raise ValueError(message)
