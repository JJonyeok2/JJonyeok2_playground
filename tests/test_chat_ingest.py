"""Tests for chat log ingestion."""

from pathlib import Path

import pytest

from editflow.ingest.chat import load_chat_buckets


def test_load_chat_csv_groups_messages_by_second(tmp_path: Path):
    path = tmp_path / "chat.csv"
    path.write_text(
        "second,message\n"
        "10,ㅋㅋㅋ\n"
        "10,미쳤다\n"
        "11,좋다\n",
        encoding="utf-8",
    )

    buckets = load_chat_buckets(path)

    assert buckets[0].second == 10
    assert buckets[0].message_count == 2
    assert buckets[0].laugh_count == 1
    assert buckets[1].second == 11


def test_load_chat_json_groups_messages_by_second(tmp_path: Path):
    path = tmp_path / "chat.json"
    path.write_text(
        '[{"second": 5, "message": "ㅋㅋ"}, {"second": 5, "message": "나이스"}]',
        encoding="utf-8",
    )

    buckets = load_chat_buckets(path)

    assert len(buckets) == 1
    assert buckets[0].messages == ["ㅋㅋ", "나이스"]


def test_load_chat_rejects_missing_required_columns(tmp_path: Path):
    path = tmp_path / "chat.csv"
    path.write_text("time,text\n10,ㅋㅋㅋ\n", encoding="utf-8")

    with pytest.raises(ValueError, match="chat rows must include columns"):
        load_chat_buckets(path)


def test_load_chat_rejects_invalid_second_value(tmp_path: Path):
    path = tmp_path / "chat.csv"
    path.write_text("second,message\nlater,ㅋㅋㅋ\n", encoding="utf-8")

    with pytest.raises(ValueError, match="chat row 1 second must be an integer"):
        load_chat_buckets(path)
