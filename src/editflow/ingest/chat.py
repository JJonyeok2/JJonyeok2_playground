"""Chat log ingestion."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

from editflow.models import ChatBucket


def load_chat_buckets(path: Path) -> list[ChatBucket]:
    """Load chat rows from CSV or JSON and group them by second."""
    return _rows_to_buckets(_read_rows(path))


def load_chat_buckets_from_text(text: str, filename: str) -> list[ChatBucket]:
    """Load chat rows from uploaded CSV or JSON text."""
    return _rows_to_buckets(_read_rows_from_text(text, filename))


def _rows_to_buckets(rows: list[dict[str, object]]) -> list[ChatBucket]:
    grouped: dict[int, list[str]] = defaultdict(list)

    for row in rows:
        second = int(row["second"])
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
        return list(csv.DictReader(text.splitlines()))
    if suffix == ".json":
        data = json.loads(text)
        if not isinstance(data, list):
            message = "chat JSON must be a list of objects"
            raise ValueError(message)
        return data
    message = f"unsupported chat file extension: {suffix}"
    raise ValueError(message)
