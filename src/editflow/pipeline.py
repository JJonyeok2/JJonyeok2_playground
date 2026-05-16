"""EditFlow analysis pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from editflow.analysis.markers import build_markers
from editflow.analysis.peaks import detect_chat_peaks, detect_heatmap_peaks
from editflow.analysis.postprocess import select_markers
from editflow.exporters.csv_report import build_marker_csv, write_marker_csv
from editflow.exporters.premiere_xml import build_premiere_xml
from editflow.ingest.chat import load_chat_buckets, load_chat_buckets_from_text
from editflow.ingest.heatmap import (
    load_heatmap_points,
    load_heatmap_points_from_text,
)

if TYPE_CHECKING:
    from pathlib import Path

    from editflow.models import ChatBucket, HeatmapPoint, Marker


@dataclass(frozen=True)
class AnalysisSettings:
    """Tuning knobs shared by API, CLI, and browser workbench."""

    fps: int = 30
    min_messages: int = 3
    min_laughs: int = 2
    min_heatmap_score: float = 0.75
    overlap_seconds: int = 5
    max_markers: int | None = None
    min_marker_gap_seconds: int = 0


@dataclass(frozen=True)
class AnalysisResult:
    """In-memory analysis result used by the API and frontend."""

    markers: list[Marker]
    xml_text: str
    csv_text: str

    @property
    def marker_count(self) -> int:
        return len(self.markers)


@dataclass(frozen=True)
class PipelineResult(AnalysisResult):
    """Analysis result with files written to disk."""

    xml_path: Path
    csv_path: Path


def run_analysis(
    *,
    chat_buckets: list[ChatBucket],
    heatmap_points: list[HeatmapPoint],
    settings: AnalysisSettings | None = None,
) -> AnalysisResult:
    """Run marker analysis from parsed chat buckets and heatmap points."""
    resolved_settings = settings or AnalysisSettings()
    chat_peaks = detect_chat_peaks(
        chat_buckets,
        min_messages=resolved_settings.min_messages,
        min_laughs=resolved_settings.min_laughs,
    )
    heatmap_peaks = detect_heatmap_peaks(
        heatmap_points,
        min_score=resolved_settings.min_heatmap_score,
    )
    markers = build_markers(
        chat_peaks=chat_peaks,
        heatmap_peaks=heatmap_peaks,
        overlap_seconds=resolved_settings.overlap_seconds,
    )
    selected_markers = select_markers(
        markers,
        min_gap_seconds=resolved_settings.min_marker_gap_seconds,
        max_markers=resolved_settings.max_markers,
    )
    return AnalysisResult(
        markers=selected_markers,
        xml_text=build_premiere_xml(selected_markers, fps=resolved_settings.fps),
        csv_text=build_marker_csv(selected_markers),
    )


def run_analysis_from_text(
    *,
    chat_text: str,
    chat_filename: str,
    heatmap_text: str,
    heatmap_filename: str,
    settings: AnalysisSettings | None = None,
) -> AnalysisResult:
    """Run marker analysis from uploaded CSV or JSON text."""
    return run_analysis(
        chat_buckets=load_chat_buckets_from_text(chat_text, chat_filename),
        heatmap_points=load_heatmap_points_from_text(heatmap_text, heatmap_filename),
        settings=settings,
    )


def run_pipeline(
    *,
    chat_path: Path,
    heatmap_path: Path,
    output_dir: Path,
    fps: int = 30,
    settings: AnalysisSettings | None = None,
) -> PipelineResult:
    """Run analysis from local files and write Premiere XML and CSV outputs."""
    analysis = run_analysis(
        chat_buckets=load_chat_buckets(chat_path),
        heatmap_points=load_heatmap_points(heatmap_path),
        settings=settings or AnalysisSettings(fps=fps),
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    xml_path = output_dir / "editflow_markers.xml"
    csv_path = output_dir / "editflow_markers.csv"
    xml_path.write_text(analysis.xml_text, encoding="utf-8")
    write_marker_csv(analysis.markers, csv_path)
    return PipelineResult(
        markers=analysis.markers,
        xml_text=analysis.xml_text,
        csv_text=analysis.csv_text,
        xml_path=xml_path,
        csv_path=csv_path,
    )
