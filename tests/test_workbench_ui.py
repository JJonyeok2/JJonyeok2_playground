"""Tests for the practical EditFlow workbench UI."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_workbench_has_editor_focused_layout():
    html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")

    required_ids = [
        'id="videoInput"',
        'id="chatInput"',
        'id="heatmapInput"',
        'id="minMessages"',
        'id="minLaughs"',
        'id="minHeatmapScore"',
        'id="overlapSeconds"',
        'id="analyzeButton"',
        'id="videoPreview"',
        'id="timeline"',
        'id="markerTable"',
        'id="exportXmlButton"',
        'id="exportCsvButton"',
    ]

    for element_id in required_ids:
        assert element_id in html

    assert "Premiere XML" in html
    assert "Final Cut" not in html


def test_workbench_script_supports_local_analysis_and_exports():
    script = (ROOT / "web" / "app.js").read_text(encoding="utf-8")

    required_functions = [
        "function parseDataFile",
        "function parseCsv",
        "function detectChatPeaks",
        "function detectHeatmapPeaks",
        "function buildMarkers",
        "function renderTimeline",
        "function exportMarkersAsCsv",
        "function exportMarkersAsXml",
    ]

    for function_name in required_functions:
        assert function_name in script

    assert "Premiere Pro" in script
    assert "<xmeml" in script


def test_workbench_script_calls_backend_analysis_api_with_fallback():
    script = (ROOT / "web" / "app.js").read_text(encoding="utf-8")

    required_backend_hooks = [
        "const API_BASE_URL",
        "async function requestBackendAnalysis",
        "function applyBackendResult",
        "function runLocalAnalysis",
        "fetch(`${API_BASE_URL}/analyze`",
    ]

    for hook in required_backend_hooks:
        assert hook in script

    assert 'const API_BASE_URL = "http://127.0.0.1:8000";' in script


def test_workbench_styles_use_dense_panels_not_landing_sections():
    styles = (ROOT / "web" / "styles.css").read_text(encoding="utf-8")

    assert ".workspace" in styles
    assert ".left-panel" in styles
    assert ".video-stage" in styles
    assert ".right-panel" in styles
    assert "border-radius: 8px" in styles or "border-radius: 6px" in styles
