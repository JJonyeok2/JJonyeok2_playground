"""Command line interface for EditFlow."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from editflow.pipeline import AnalysisSettings, run_pipeline

app = typer.Typer(help="EditFlow analysis workflows.", no_args_is_help=True)
CHAT_OPTION = typer.Option(
    ...,
    "--chat",
    "-c",
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
    resolve_path=True,
    help="Chat CSV or JSON file.",
)
HEATMAP_OPTION = typer.Option(
    ...,
    "--heatmap",
    "-m",
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
    resolve_path=True,
    help="Replay heatmap CSV or JSON file.",
)
OUT_OPTION = typer.Option(
    Path("outputs"),
    "--out",
    "-o",
    file_okay=False,
    dir_okay=True,
    writable=True,
    resolve_path=True,
    help="Directory where XML and CSV outputs are written.",
)
FPS_OPTION = typer.Option(30, "--fps", min=1, help="Timeline frame rate.")
MIN_MESSAGES_OPTION = typer.Option(
    3,
    "--min-messages",
    min=1,
    help="Minimum chat count for A markers.",
)
MIN_LAUGHS_OPTION = typer.Option(
    2,
    "--min-laughs",
    min=1,
    help="Minimum laugh count for A markers.",
)
MIN_HEATMAP_SCORE_OPTION = typer.Option(
    0.75,
    "--min-heatmap-score",
    min=0,
    max=1,
    help="Minimum normalized heatmap score for B markers.",
)
OVERLAP_SECONDS_OPTION = typer.Option(
    5,
    "--overlap-seconds",
    min=0,
    help="Window for S marker overlap.",
)
MAX_MARKERS_OPTION = typer.Option(
    None,
    "--max-markers",
    min=1,
    help="Maximum marker count to export.",
)
MIN_MARKER_GAP_SECONDS_OPTION = typer.Option(
    0,
    "--min-marker-gap-seconds",
    min=0,
    help="Minimum seconds between exported markers.",
)
PRE_ROLL_SECONDS_OPTION = typer.Option(
    0,
    "--pre-roll-seconds",
    min=0,
    help="Seconds to start Premiere markers before the detected peak.",
)
MARKER_DURATION_SECONDS_OPTION = typer.Option(
    1,
    "--marker-duration-seconds",
    min=1,
    help="Duration of each exported Premiere marker.",
)


@app.callback()
def root() -> None:
    """Run EditFlow commands."""


@app.command()
def analyze(  # noqa: PLR0913
    chat: Path = CHAT_OPTION,
    heatmap: Path = HEATMAP_OPTION,
    out: Path = OUT_OPTION,
    fps: int = FPS_OPTION,
    min_messages: int = MIN_MESSAGES_OPTION,
    min_laughs: int = MIN_LAUGHS_OPTION,
    min_heatmap_score: float = MIN_HEATMAP_SCORE_OPTION,
    overlap_seconds: int = OVERLAP_SECONDS_OPTION,
    max_markers: Optional[int] = MAX_MARKERS_OPTION,  # noqa: UP045
    min_marker_gap_seconds: int = MIN_MARKER_GAP_SECONDS_OPTION,
    pre_roll_seconds: int = PRE_ROLL_SECONDS_OPTION,
    marker_duration_seconds: int = MARKER_DURATION_SECONDS_OPTION,
) -> None:
    """Analyze chat and replay heatmap files, then write Premiere XML and CSV."""
    try:
        result = run_pipeline(
            chat_path=chat,
            heatmap_path=heatmap,
            output_dir=out,
            settings=AnalysisSettings(
                fps=fps,
                min_messages=min_messages,
                min_laughs=min_laughs,
                min_heatmap_score=min_heatmap_score,
                overlap_seconds=overlap_seconds,
                max_markers=max_markers,
                min_marker_gap_seconds=min_marker_gap_seconds,
                pre_roll_seconds=pre_roll_seconds,
                marker_duration_seconds=marker_duration_seconds,
            ),
        )
    except ValueError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1) from error

    typer.echo(f"Generated {result.marker_count} markers")
    typer.echo(f"Premiere XML: {result.xml_path}")
    typer.echo(f"CSV report: {result.csv_path}")


def main() -> None:
    """Console script entry point."""
    app()


if __name__ == "__main__":
    main()
