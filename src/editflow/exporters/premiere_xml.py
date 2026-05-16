"""Premiere Pro XML marker exporter."""

from __future__ import annotations

from typing import TYPE_CHECKING
from xml.etree import ElementTree as ET

if TYPE_CHECKING:
    from editflow.models import Marker


def build_premiere_xml(
    markers: list[Marker],
    *,
    sequence_name: str = "EditFlow Markers",
    fps: int = 30,
    pre_roll_seconds: int = 0,
    marker_duration_seconds: int = 1,
) -> str:
    """Build Premiere Pro xmeml marker XML text."""
    if pre_roll_seconds < 0:
        message = "pre_roll_seconds must be 0 or greater"
        raise ValueError(message)
    if marker_duration_seconds < 1:
        message = "marker_duration_seconds must be 1 or greater"
        raise ValueError(message)

    root = ET.Element("xmeml", {"version": "5"})
    sequence = ET.SubElement(root, "sequence", {"id": "editflow-sequence"})
    ET.SubElement(sequence, "name").text = sequence_name
    ET.SubElement(sequence, "duration").text = str(
        _duration_frames(markers, fps)
    )

    rate = ET.SubElement(sequence, "rate")
    ET.SubElement(rate, "timebase").text = str(fps)
    ET.SubElement(rate, "ntsc").text = "FALSE"

    for marker in markers:
        frame = max(0, marker.second - pre_roll_seconds) * fps
        out_frame = frame + (marker_duration_seconds * fps)
        marker_node = ET.SubElement(sequence, "marker")
        ET.SubElement(marker_node, "name").text = (
            f"[{marker.color.value.upper()}] {marker.title}"
        )
        ET.SubElement(marker_node, "comment").text = (
            f"{marker.memo} | evidence={','.join(marker.evidence)} | "
            f"confidence={marker.confidence:.2f}"
        )
        ET.SubElement(marker_node, "in").text = str(frame)
        ET.SubElement(marker_node, "out").text = str(out_frame)

    return ET.tostring(root, encoding="unicode", xml_declaration=True)


def _duration_frames(markers: list[Marker], fps: int) -> int:
    if not markers:
        return fps
    return (max(marker.second for marker in markers) + 60) * fps
