"""Tests for highlight marker classification."""

from editflow.analysis.markers import build_markers
from editflow.models import MarkerColor, MarkerGrade, Peak


def test_build_markers_creates_s_grade_when_sources_overlap():
    markers = build_markers(
        chat_peaks=[Peak(second=10, source="chat_peak", strength=1.0)],
        heatmap_peaks=[Peak(second=12, source="heatmap_peak", strength=0.9)],
        overlap_seconds=3,
    )

    assert len(markers) == 1
    assert markers[0].second == 10
    assert markers[0].grade == MarkerGrade.S
    assert markers[0].color == MarkerColor.PURPLE
    assert markers[0].evidence == ["chat_peak", "heatmap_peak"]


def test_build_markers_keeps_single_source_markers():
    markers = build_markers(
        chat_peaks=[Peak(second=30, source="chat_peak", strength=0.8)],
        heatmap_peaks=[Peak(second=90, source="heatmap_peak", strength=0.76)],
        overlap_seconds=3,
    )

    assert [marker.grade for marker in markers] == [MarkerGrade.A, MarkerGrade.B]
    assert [marker.second for marker in markers] == [30, 90]
