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
) -> str:
    """Build Premiere Pro xmeml marker XML text."""
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
        frame = marker.second * fps
        marker_node = ET.SubElement(sequence, "marker")
        ET.SubElement(marker_node, "name").text = (
            f"[{marker.color.value.upper()}] {marker.title}"
        )
        ET.SubElement(marker_node, "comment").text = (
            f"{marker.memo} | evidence={','.join(marker.evidence)} | "
            f"confidence={marker.confidence:.2f}"
        )
        ET.SubElement(marker_node, "in").text = str(frame)
        ET.SubElement(marker_node, "out").text = str(frame + fps)

    return ET.tostring(root, encoding="unicode", xml_declaration=True)


def _duration_frames(markers: list[Marker], fps: int) -> int:
    if not markers:
        return fps
    return (max(marker.second for marker in markers) + 60) * fps
