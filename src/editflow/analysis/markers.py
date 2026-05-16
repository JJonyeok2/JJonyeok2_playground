"""Marker classification from detected evidence peaks."""

from __future__ import annotations

from editflow.models import Marker, MarkerGrade, Peak


def build_markers(
    *,
    chat_peaks: list[Peak],
    heatmap_peaks: list[Peak],
    overlap_seconds: int = 5,
) -> list[Marker]:
    """Build graded highlight markers from chat and heatmap evidence."""
    markers: list[Marker] = []
    used_heatmap_seconds: set[int] = set()

    for chat_peak in chat_peaks:
        matching_heatmap = _nearest_peak(chat_peak, heatmap_peaks, overlap_seconds)
        if matching_heatmap is not None:
            used_heatmap_seconds.add(matching_heatmap.second)
            confidence = round((chat_peak.strength + matching_heatmap.strength) / 2, 4)
            markers.append(
                Marker.from_grade(
                    second=chat_peak.second,
                    grade=MarkerGrade.S,
                    evidence=["chat_peak", "heatmap_peak"],
                    confidence=confidence,
                )
            )
        else:
            markers.append(
                Marker.from_grade(
                    second=chat_peak.second,
                    grade=MarkerGrade.A,
                    evidence=["chat_peak"],
                    confidence=chat_peak.strength,
                )
            )

    for heatmap_peak in heatmap_peaks:
        if heatmap_peak.second in used_heatmap_seconds:
            continue
        markers.append(
            Marker.from_grade(
                second=heatmap_peak.second,
                grade=MarkerGrade.B,
                evidence=["heatmap_peak"],
                confidence=heatmap_peak.strength,
            )
        )

    return sorted(markers, key=lambda marker: marker.second)


def _nearest_peak(
    reference: Peak,
    candidates: list[Peak],
    overlap_seconds: int,
) -> Peak | None:
    overlapping = [
        candidate
        for candidate in candidates
        if abs(candidate.second - reference.second) <= overlap_seconds
    ]
    if not overlapping:
        return None
    return min(
        overlapping,
        key=lambda candidate: abs(candidate.second - reference.second),
    )
