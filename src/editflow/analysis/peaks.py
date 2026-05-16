"""Threshold-based peak detection."""

from __future__ import annotations

from editflow.models import ChatBucket, HeatmapPoint, Peak


def detect_chat_peaks(
    buckets: list[ChatBucket],
    *,
    min_messages: int = 3,
    min_laughs: int = 2,
) -> list[Peak]:
    """Detect chat reaction peaks from message and laugh velocity."""
    peaks: list[Peak] = []
    max_count = max((bucket.message_count for bucket in buckets), default=1)

    for bucket in buckets:
        if bucket.message_count >= min_messages or bucket.laugh_count >= min_laughs:
            strength = round(bucket.message_count / max_count, 4)
            peaks.append(
                Peak(second=bucket.second, source="chat_peak", strength=strength)
            )

    return peaks


def detect_heatmap_peaks(
    points: list[HeatmapPoint],
    *,
    min_score: float = 0.75,
) -> list[Peak]:
    """Detect replay heatmap peaks above a normalized score threshold."""
    return [
        Peak(second=point.second, source="heatmap_peak", strength=point.score)
        for point in points
        if point.score >= min_score
    ]
