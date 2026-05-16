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
        'id="peakMergeSeconds"',
        'id="maxMarkers"',
        'id="minMarkerGapSeconds"',
        'id="preRollSeconds"',
        'id="markerDurationSeconds"',
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
    assert '<script type="module" src="./src/main.js"></script>' in html


def test_workbench_hides_tuning_controls_in_collapsed_advanced_panel():
    html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")

    details_start = html.index('<details class="advanced-settings">')
    details_end = html.index("</details>", details_start)
    advanced_markup = html[details_start:details_end]
    button_position = html.index('id="analyzeButton"')

    assert button_position < details_start
    assert '<details class="advanced-settings" open>' not in html
    assert "<summary>Advanced</summary>" in advanced_markup

    advanced_ids = [
        'id="minMessages"',
        'id="minLaughs"',
        'id="minHeatmapScore"',
        'id="overlapSeconds"',
        'id="peakMergeSeconds"',
        'id="maxMarkers"',
        'id="minMarkerGapSeconds"',
        'id="preRollSeconds"',
        'id="markerDurationSeconds"',
    ]

    for element_id in advanced_ids:
        assert element_id in advanced_markup


def test_workbench_uses_modular_frontend_scripts():
    module_exports = {
        "web/src/api.js": [
            "export async function requestBackendAnalysis",
            "export function applyBackendResult",
        ],
        "web/src/analysis.js": [
            "export function detectChatPeaks",
            "export function detectHeatmapPeaks",
            "export function buildMarkers",
            "export function runLocalAnalysis",
        ],
        "web/src/data.js": [
            "export async function parseDataFile",
            "export function parseCsv",
        ],
        "web/src/render.js": [
            "export function renderTimeline",
            "export function renderMarkerTable",
        ],
        "web/src/exporters.js": [
            "export function exportMarkersAsCsv",
            "export function exportMarkersAsXml",
            "export function buildPremiereXmlText",
            "export function buildCsvText",
        ],
    }

    for module_path, required_exports in module_exports.items():
        script = (ROOT / module_path).read_text(encoding="utf-8")
        for exported_symbol in required_exports:
            assert exported_symbol in script

    main_script = (ROOT / "web" / "src" / "main.js").read_text(encoding="utf-8")
    assert 'from "./api.js"' in main_script
    assert 'from "./analysis.js"' in main_script
    assert 'from "./data.js"' in main_script
    assert 'from "./render.js"' in main_script


def test_workbench_api_payload_includes_marker_postprocessing_options():
    script = (ROOT / "web" / "src" / "api.js").read_text(encoding="utf-8")

    required_payload_fields = [
        'API_BASE_URL = "http://127.0.0.1:8000"',
        "fetch(`${API_BASE_URL}/analyze`",
        "peak_merge_seconds",
        "max_markers",
        "min_marker_gap_seconds",
        "pre_roll_seconds",
        "marker_duration_seconds",
    ]

    for payload_field in required_payload_fields:
        assert payload_field in script


def test_workbench_scripts_keep_backend_fallback_and_premiere_exports():
    main_script = (ROOT / "web" / "src" / "main.js").read_text(encoding="utf-8")
    analysis_script = (ROOT / "web" / "src" / "analysis.js").read_text(encoding="utf-8")
    exporter_script = (ROOT / "web" / "src" / "exporters.js").read_text(
        encoding="utf-8",
    )

    required_fallback_hooks = [
        "async function runAnalysis",
        "requestBackendAnalysis",
        "function runLocalAnalysis",
        "EditFlow API unavailable. Falling back to browser analysis.",
    ]

    for hook in required_fallback_hooks:
        assert hook in main_script or hook in analysis_script

    assert "Premiere Pro" in exporter_script
    assert "<xmeml" in exporter_script


def test_workbench_styles_use_dense_panels_not_landing_sections():
    styles = (ROOT / "web" / "styles.css").read_text(encoding="utf-8")

    assert ".workspace" in styles
    assert ".left-panel" in styles
    assert ".video-stage" in styles
    assert ".right-panel" in styles
    assert "border-radius: 8px" in styles or "border-radius: 6px" in styles
