"""Analysis run manifest exporter."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path


def build_manifest_json(
    *,
    marker_count: int,
    xml_path: Path,
    csv_path: Path,
    settings: dict[str, Any],
) -> str:
    """Build a machine-readable manifest for generated output files."""
    manifest = {
        "marker_count": marker_count,
        "outputs": {
            "premiere_xml": xml_path.name,
            "csv_report": csv_path.name,
        },
        "settings": settings,
    }
    return json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True)


def write_manifest(
    *,
    path: Path,
    marker_count: int,
    xml_path: Path,
    csv_path: Path,
    settings: dict[str, Any],
) -> None:
    """Write the analysis manifest to disk."""
    path.write_text(
        build_manifest_json(
            marker_count=marker_count,
            xml_path=xml_path,
            csv_path=csv_path,
            settings=settings,
        ),
        encoding="utf-8",
    )
