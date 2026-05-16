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
