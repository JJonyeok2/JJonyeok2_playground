"""Tests for EditFlow command line workflows."""

from typer.testing import CliRunner

from editflow.cli import app

CHAT_TEXT = "second,message\n10,ㅋㅋ\n10,ㅋㅋㅋ\n10,미쳤다\n"
HEATMAP_TEXT = "second,score\n11,0.9\n"


def test_analyze_command_writes_premiere_xml_and_csv(tmp_path):
    chat_path = tmp_path / "chat.csv"
    heatmap_path = tmp_path / "heatmap.csv"
    output_dir = tmp_path / "out"
    chat_path.write_text(CHAT_TEXT, encoding="utf-8")
    heatmap_path.write_text(HEATMAP_TEXT, encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "analyze",
            "--chat",
            str(chat_path),
            "--heatmap",
            str(heatmap_path),
            "--out",
            str(output_dir),
            "--fps",
            "30",
        ],
    )

    xml_path = output_dir / "editflow_markers.xml"
    csv_path = output_dir / "editflow_markers.csv"

    assert result.exit_code == 0, result.output
    assert "Generated 1 markers" in result.output
    assert str(xml_path) in result.output
    assert str(csv_path) in result.output
    assert "<xmeml" in xml_path.read_text(encoding="utf-8")
    assert "S급 하이라이트" in csv_path.read_text(encoding="utf-8")


def test_analyze_command_accepts_marker_limit_options(tmp_path):
    chat_path = tmp_path / "chat.csv"
    heatmap_path = tmp_path / "heatmap.csv"
    output_dir = tmp_path / "out"
    chat_path.write_text(
        (
            "second,message\n"
            "10,ㅋㅋ\n10,ㅋㅋㅋ\n10,미쳤다\n"
            "12,ㅋㅋ\n12,ㅋㅋㅋ\n12,레전드\n"
            "40,ㅋㅋ\n40,ㅋㅋㅋ\n40,좋다\n"
        ),
        encoding="utf-8",
    )
    heatmap_path.write_text("second,score\n11,0.9\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "analyze",
            "--chat",
            str(chat_path),
            "--heatmap",
            str(heatmap_path),
            "--out",
            str(output_dir),
            "--max-markers",
            "1",
            "--min-marker-gap-seconds",
            "5",
        ],
    )

    csv_text = (output_dir / "editflow_markers.csv").read_text(encoding="utf-8")

    assert result.exit_code == 0, result.output
    assert "Generated 1 markers" in result.output
    assert "10,S,purple" in csv_text
    assert "40,A,red" not in csv_text


def test_analyze_command_reports_invalid_input_without_traceback(tmp_path):
    chat_path = tmp_path / "chat.csv"
    heatmap_path = tmp_path / "heatmap.csv"
    output_dir = tmp_path / "out"
    chat_path.write_text("time,text\n10,ㅋㅋ\n", encoding="utf-8")
    heatmap_path.write_text(HEATMAP_TEXT, encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "analyze",
            "--chat",
            str(chat_path),
            "--heatmap",
            str(heatmap_path),
            "--out",
            str(output_dir),
        ],
    )

    assert result.exit_code == 1
    assert "chat rows must include columns" in result.output
    assert "Traceback" not in result.output
