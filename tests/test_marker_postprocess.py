"""Tests for marker post-processing controls."""

from editflow.analysis.postprocess import select_markers
from editflow.models import Marker, MarkerGrade


def test_select_markers_prefers_stronger_marker_inside_minimum_gap():
    markers = [
        Marker.from_grade(
            second=10,
            grade=MarkerGrade.A,
            evidence=["chat_peak"],
            confidence=0.95,
        ),
        Marker.from_grade(
            second=13,
            grade=MarkerGrade.S,
            evidence=["chat_peak", "heatmap_peak"],
            confidence=0.8,
        ),
        Marker.from_grade(
            second=40,
            grade=MarkerGrade.B,
            evidence=["heatmap_peak"],
            confidence=0.9,
        ),
    ]

    selected = select_markers(markers, min_gap_seconds=5)

    assert [marker.second for marker in selected] == [13, 40]


def test_select_markers_limits_to_best_candidates_then_sorts_by_time():
    markers = [
        Marker.from_grade(
            second=30,
            grade=MarkerGrade.B,
            evidence=["heatmap_peak"],
            confidence=0.95,
        ),
        Marker.from_grade(
            second=10,
            grade=MarkerGrade.S,
            evidence=["chat_peak", "heatmap_peak"],
            confidence=0.8,
        ),
        Marker.from_grade(
            second=20,
            grade=MarkerGrade.A,
            evidence=["chat_peak"],
            confidence=0.9,
        ),
    ]

    selected = select_markers(markers, max_markers=2)

    assert [marker.second for marker in selected] == [10, 20]
