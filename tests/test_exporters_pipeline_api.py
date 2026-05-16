"""Tests for marker export, pipeline orchestration, and API integration."""

import pytest
from fastapi import HTTPException

from editflow.api import AnalyzeRequest, analyze, api
from editflow.exporters.csv_report import build_marker_csv
from editflow.exporters.premiere_xml import build_premiere_xml
from editflow.models import Marker, MarkerGrade
from editflow.pipeline import AnalysisSettings, run_analysis_from_text

CHAT_TEXT = "second,message\n10,ㅋㅋ\n10,ㅋㅋㅋ\n10,미쳤다\n"
HEATMAP_TEXT = "second,score\n11,0.9\n"


def test_build_premiere_xml_contains_sequence_markers():
    marker = Marker.from_grade(
        second=10,
        grade=MarkerGrade.S,
        evidence=["chat_peak", "heatmap_peak"],
        confidence=0.95,
    )

    xml_text = build_premiere_xml([marker], sequence_name="EditFlow Test", fps=30)

    assert '<xmeml version="5">' in xml_text
    assert "<marker>" in xml_text
    assert "<name>[PURPLE] S급 하이라이트</name>" in xml_text
    assert "<in>300</in>" in xml_text


def test_build_premiere_xml_supports_preroll_and_duration():
    marker = Marker.from_grade(
        second=10,
        grade=MarkerGrade.S,
        evidence=["chat_peak", "heatmap_peak"],
        confidence=0.95,
    )

    xml_text = build_premiere_xml(
        [marker],
        fps=30,
        pre_roll_seconds=2,
        marker_duration_seconds=5,
    )

    assert "<in>240</in>" in xml_text
    assert "<out>390</out>" in xml_text


def test_build_marker_csv_outputs_sidecar_report():
    marker = Marker.from_grade(
        second=65,
        grade=MarkerGrade.A,
        evidence=["chat_peak"],
        confidence=0.8,
    )

    csv_text = build_marker_csv([marker])

    assert "second,timecode,grade,color,title,memo,evidence,confidence" in csv_text
    assert "65,00:01:05:00,A,red,A급 채팅 피크" in csv_text


def test_run_analysis_from_text_returns_markers_and_export_text():
    result = run_analysis_from_text(
        chat_text=CHAT_TEXT,
        chat_filename="chat.csv",
        heatmap_text=HEATMAP_TEXT,
        heatmap_filename="heatmap.csv",
        settings=AnalysisSettings(fps=30),
    )

    assert result.marker_count == 1
    assert result.markers[0].grade == MarkerGrade.S
    assert "<xmeml" in result.xml_text
    assert "S급 하이라이트" in result.csv_text


def test_run_analysis_from_text_applies_marker_limits():
    result = run_analysis_from_text(
        chat_text=(
            "second,message\n"
            "10,ㅋㅋ\n10,ㅋㅋㅋ\n10,미쳤다\n"
            "12,ㅋㅋ\n12,ㅋㅋㅋ\n12,레전드\n"
            "40,ㅋㅋ\n40,ㅋㅋㅋ\n40,좋다\n"
        ),
        chat_filename="chat.csv",
        heatmap_text="second,score\n11,0.9\n",
        heatmap_filename="heatmap.csv",
        settings=AnalysisSettings(
            max_markers=1,
            min_marker_gap_seconds=5,
        ),
    )

    assert result.marker_count == 1
    assert result.markers[0].second == 10
    assert result.markers[0].grade == MarkerGrade.S


def test_run_analysis_from_text_applies_xml_window_settings():
    result = run_analysis_from_text(
        chat_text=CHAT_TEXT,
        chat_filename="chat.csv",
        heatmap_text=HEATMAP_TEXT,
        heatmap_filename="heatmap.csv",
        settings=AnalysisSettings(
            fps=30,
            pre_roll_seconds=2,
            marker_duration_seconds=5,
        ),
    )

    assert "<in>240</in>" in result.xml_text
    assert "<out>390</out>" in result.xml_text


def test_api_analyze_endpoint_accepts_uploaded_file_texts():
    route_paths = {route.path for route in api.routes}
    result = analyze(
        AnalyzeRequest(
            chat_text=CHAT_TEXT,
            chat_filename="chat.csv",
            heatmap_text=HEATMAP_TEXT,
            heatmap_filename="heatmap.csv",
            fps=30,
            min_messages=3,
            min_laughs=2,
            min_heatmap_score=0.75,
            overlap_seconds=5,
        )
    )

    assert "/analyze" in route_paths
    assert result.marker_count == 1
    assert result.markers[0].grade == "S"
    assert result.xml_text.startswith("<?xml")
    assert "S급 하이라이트" in result.csv_text


def test_api_analyze_endpoint_accepts_marker_limit_settings():
    result = analyze(
        AnalyzeRequest(
            chat_text=(
                "second,message\n"
                "10,ㅋㅋ\n10,ㅋㅋㅋ\n10,미쳤다\n"
                "12,ㅋㅋ\n12,ㅋㅋㅋ\n12,레전드\n"
                "40,ㅋㅋ\n40,ㅋㅋㅋ\n40,좋다\n"
            ),
            chat_filename="chat.csv",
            heatmap_text="second,score\n11,0.9\n",
            heatmap_filename="heatmap.csv",
            max_markers=1,
            min_marker_gap_seconds=5,
        )
    )

    assert result.marker_count == 1
    assert result.markers[0].second == 10


def test_api_analyze_endpoint_accepts_xml_window_settings():
    result = analyze(
        AnalyzeRequest(
            chat_text=CHAT_TEXT,
            chat_filename="chat.csv",
            heatmap_text=HEATMAP_TEXT,
            heatmap_filename="heatmap.csv",
            pre_roll_seconds=2,
            marker_duration_seconds=5,
        )
    )

    assert "<in>240</in>" in result.xml_text
    assert "<out>390</out>" in result.xml_text


def test_api_analyze_endpoint_returns_bad_request_for_invalid_input():
    with pytest.raises(HTTPException) as error:
        analyze(
            AnalyzeRequest(
                chat_text="time,text\n10,ㅋㅋ\n",
                chat_filename="chat.csv",
                heatmap_text=HEATMAP_TEXT,
                heatmap_filename="heatmap.csv",
            )
        )

    assert error.value.status_code == 400
    assert "chat rows must include columns" in error.value.detail
