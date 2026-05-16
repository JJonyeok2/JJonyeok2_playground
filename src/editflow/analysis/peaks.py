"""Threshold-based peak detection."""

from __future__ import annotations

from editflow.models import ChatBucket, HeatmapPoint, Peak


def detect_chat_peaks(
    buckets: list[ChatBucket],
    *,
    min_messages: int = 3,
    min_laughs: int = 2,
    merge_gap_seconds: int = 0,
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

    return _merge_nearby_peaks(peaks, merge_gap_seconds=merge_gap_seconds)


def detect_heatmap_peaks(
    points: list[HeatmapPoint],
    *,
    min_score: float = 0.75,
    merge_gap_seconds: int = 0,
) -> list[Peak]:
    """Detect replay heatmap peaks above a normalized score threshold."""
    peaks = [
        Peak(second=point.second, source="heatmap_peak", strength=point.score)
        for point in points
        if point.score >= min_score
    ]
    return _merge_nearby_peaks(peaks, merge_gap_seconds=merge_gap_seconds)


def _merge_nearby_peaks(
    peaks: list[Peak],
    *,
    merge_gap_seconds: int,
) -> list[Peak]:
    if merge_gap_seconds < 0:
        message = "merge_gap_seconds must be 0 or greater"
        raise ValueError(message)
    if merge_gap_seconds == 0:
        return peaks

    merged: list[Peak] = []
    cluster: list[Peak] = []
    for peak in sorted(peaks, key=lambda item: item.second):
        if not cluster or peak.second - cluster[-1].second <= merge_gap_seconds:
            cluster.append(peak)
            continue
        merged.append(_best_peak(cluster))
        cluster = [peak]

    if cluster:
        merged.append(_best_peak(cluster))
    return merged


def _best_peak(peaks: list[Peak]) -> Peak:
    return max(peaks, key=lambda peak: (peak.strength, peak.second))
