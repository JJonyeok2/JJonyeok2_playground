"""Marker post-processing for editor-friendly output volume."""

from __future__ import annotations

from editflow.models import Marker, MarkerGrade

GRADE_PRIORITY = {
    MarkerGrade.S: 3,
    MarkerGrade.A: 2,
    MarkerGrade.B: 1,
}


def select_markers(
    markers: list[Marker],
    *,
    min_gap_seconds: int = 0,
    max_markers: int | None = None,
) -> list[Marker]:
    """Select the strongest markers while enforcing spacing and count limits."""
    if min_gap_seconds < 0:
        message = "min_gap_seconds must be 0 or greater"
        raise ValueError(message)
    if max_markers is not None and max_markers < 1:
        message = "max_markers must be 1 or greater"
        raise ValueError(message)

    selected: list[Marker] = []
    for marker in sorted(markers, key=_marker_rank):
        if _is_far_enough(marker, selected, min_gap_seconds):
            selected.append(marker)
        if max_markers is not None and len(selected) >= max_markers:
            break

    return sorted(selected, key=lambda marker: marker.second)


def _marker_rank(marker: Marker) -> tuple[int, float, int]:
    return (
        -GRADE_PRIORITY[marker.grade],
        -marker.confidence,
        marker.second,
    )


def _is_far_enough(
    marker: Marker,
    selected: list[Marker],
    min_gap_seconds: int,
) -> bool:
    if min_gap_seconds == 0:
        return True
    return all(
        abs(marker.second - selected_marker.second) >= min_gap_seconds
        for selected_marker in selected
    )
