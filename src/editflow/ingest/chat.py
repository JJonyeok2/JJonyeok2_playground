"""Chat log ingestion."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from typing import TYPE_CHECKING

from editflow.models import ChatBucket

if TYPE_CHECKING:
    from pathlib import Path


def load_chat_buckets(path: Path) -> list[ChatBucket]:
    """Load chat rows from CSV or JSON and group them by second."""
    grouped: dict[int, list[str]] = defaultdict(list)

    for row in _read_rows(path):
        second = int(row["second"])
        message = str(row["message"]).strip()
        if message:
            grouped[second].append(message)

    return [
        ChatBucket(second=second, messages=grouped[second])
        for second in sorted(grouped)
    ]


def _read_rows(path: Path) -> list[dict[str, object]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8", newline="") as file:
            return list(csv.DictReader(file))
    if suffix == ".json":
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            message = "chat JSON must be a list of objects"
            raise ValueError(message)
        return data
    message = f"unsupported chat file extension: {suffix}"
    raise ValueError(message)
