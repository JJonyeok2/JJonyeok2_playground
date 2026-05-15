"""Tests for editflow.models module."""

from editflow.models import Marker, MarkerColor, MarkerGrade


def test_marker_creation():
    """Test creating a Marker instance."""
    marker = Marker(
        second=10,
        grade=MarkerGrade.S,
        color=MarkerColor.PURPLE,
        title="S급 하이라이트",
        memo="무조건 살려야 하는 핵심 구간! 숏폼 제작 1순위 후보입니다.",
        evidence=["chat_peak", "heatmap_peak"],
        confidence=1.0,
    )
    assert marker.second == 10
    assert marker.grade == MarkerGrade.S
    assert marker.color == MarkerColor.PURPLE
    assert marker.title == "S급 하이라이트"
    assert marker.memo == "무조건 살려야 하는 핵심 구간! 숏폼 제작 1순위 후보입니다."
    assert marker.evidence == ["chat_peak", "heatmap_peak"]
    assert marker.confidence == 1.0


def test_marker_grade_enum():
    """Test MarkerGrade enum values."""
    assert MarkerGrade.S.value == "S"
    assert MarkerGrade.A.value == "A"
    assert MarkerGrade.B.value == "B"


def test_marker_color_enum():
    """Test MarkerColor enum values."""
    assert MarkerColor.PURPLE.value == "purple"
    assert MarkerColor.RED.value == "red"
    assert MarkerColor.YELLOW.value == "yellow"
