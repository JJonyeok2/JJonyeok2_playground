"""Chat log ingestion."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

from editflow.models import ChatBucket

REQUIRED_COLUMNS = {"second", "message"}


def load_chat_buckets(path: Path) -> list[ChatBucket]:
    """Load chat rows from CSV or JSON and group them by second."""
    return _rows_to_buckets(_read_rows(path))


def load_chat_buckets_from_text(text: str, filename: str) -> list[ChatBucket]:
    """Load chat rows from uploaded CSV or JSON text."""
    return _rows_to_buckets(_read_rows_from_text(text, filename))


def _rows_to_buckets(rows: list[dict[str, object]]) -> list[ChatBucket]:
    grouped: dict[int, list[str]] = defaultdict(list)

    for row_number, row in enumerate(rows, start=1):
        _validate_columns(row, "chat", row_number)
        try:
            second = int(row["second"])
        except (TypeError, ValueError) as error:
            message = f"chat row {row_number} second must be an integer"
            raise ValueError(message) from error
        message = str(row["message"]).strip()
        if message:
            grouped[second].append(message)

    return [
        ChatBucket(second=second, messages=grouped[second])
        for second in sorted(grouped)
    ]


def _read_rows(path: Path) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8")
    return _read_rows_from_text(text, path.name)


def _read_rows_from_text(text: str, filename: str) -> list[dict[str, object]]:
    suffix = Path(filename).suffix.lower()
    if suffix == ".csv":
        reader = csv.DictReader(text.splitlines())
        _validate_header(reader.fieldnames, "chat")
        return list(reader)
    if suffix == ".json":
        data = json.loads(text)
        if not isinstance(data, list):
            message = "chat JSON must be a list of objects"
            raise ValueError(message)
        return data
    message = f"unsupported chat file extension: {suffix}"
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
