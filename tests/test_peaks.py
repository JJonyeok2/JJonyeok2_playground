"""Tests for highlight peak detection."""

from editflow.analysis.peaks import detect_chat_peaks, detect_heatmap_peaks
from editflow.models import ChatBucket, HeatmapPoint


def test_detect_chat_peaks_uses_message_and_laugh_velocity():
    buckets = [
        ChatBucket(second=1, messages=["좋다"]),
        ChatBucket(second=2, messages=["ㅋㅋ", "ㅋㅋㅋ", "미쳤다", "와"]),
        ChatBucket(second=3, messages=["음"]),
    ]

    peaks = detect_chat_peaks(buckets, min_messages=3, min_laughs=2)

    assert len(peaks) == 1
    assert peaks[0].second == 2
    assert peaks[0].source == "chat_peak"
    assert peaks[0].strength == 1.0


def test_detect_heatmap_peaks_uses_minimum_score():
    points = [
        HeatmapPoint(second=10, score=0.4),
        HeatmapPoint(second=20, score=0.82),
    ]

    peaks = detect_heatmap_peaks(points, min_score=0.8)

    assert len(peaks) == 1
    assert peaks[0].second == 20
    assert peaks[0].source == "heatmap_peak"
    assert peaks[0].strength == 0.82
