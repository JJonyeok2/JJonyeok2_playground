"""Tests for demo example files used by the workbench README flow."""

from pathlib import Path

from editflow.models import MarkerGrade
from editflow.pipeline import AnalysisSettings, run_pipeline

ROOT = Path(__file__).resolve().parents[1]


def test_pexels_action_demo_examples_generate_ranked_markers(tmp_path):
    result = run_pipeline(
        chat_path=ROOT / "examples" / "pexels_action_chat.csv",
        heatmap_path=ROOT / "examples" / "pexels_action_heatmap.csv",
        output_dir=tmp_path,
        settings=AnalysisSettings(
            max_markers=6,
            overlap_seconds=1,
            peak_merge_seconds=1,
            min_marker_gap_seconds=2,
            pre_roll_seconds=2,
            marker_duration_seconds=2,
        ),
    )

    grades = {marker.grade for marker in result.markers}

    assert result.marker_count >= 4
    assert MarkerGrade.S in grades
    assert MarkerGrade.A in grades
    assert MarkerGrade.B in grades
    assert result.markers[0].second >= 0
    assert "S급 하이라이트" in result.csv_text
