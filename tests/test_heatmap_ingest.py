"""Tests for replay heatmap ingestion."""

from pathlib import Path

import pytest

from editflow.ingest.heatmap import load_heatmap_points


def test_load_heatmap_csv_sorts_points(tmp_path: Path):
    path = tmp_path / "heatmap.csv"
    path.write_text("second,score\n12,0.5\n3,0.9\n", encoding="utf-8")

    points = load_heatmap_points(path)

    assert [point.second for point in points] == [3, 12]
    assert points[0].score == 0.9


def test_load_heatmap_rejects_score_outside_normalized_range(tmp_path: Path):
    path = tmp_path / "heatmap.csv"
    path.write_text("second,score\n12,1.5\n", encoding="utf-8")

    with pytest.raises(ValueError, match="between 0 and 1"):
        load_heatmap_points(path)
