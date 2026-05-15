# EditFlow MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first working EditFlow MVP: ingest chat/heatmap data, detect highlight moments, classify markers, and export Premiere-importable XML plus a CSV report.

**Architecture:** Keep the first version as a Python package with pure core modules and thin adapters. Core modules parse input data, detect peaks, merge evidence, and create marker objects; adapters expose the same pipeline through a CLI and a FastAPI endpoint.

**Tech Stack:** Python 3.11+, pytest, FastAPI, Typer, Ruff, standard-library XML generation, CSV/JSON input files.

---

## MVP Scope

This plan implements the Notion project's first practical slice:

- Input: local chat logs and replay heatmap files in CSV or JSON.
- Analysis: detect chat velocity peaks, laugh spikes, and replay heatmap peaks.
- Classification:
  - Purple/S-grade: chat peak and heatmap peak overlap.
  - Red/A-grade: chat peak only.
  - Yellow/B-grade: heatmap peak only.
- Output: `dist/editflow_markers.xml` and `dist/editflow_markers.csv`.
- Interface: CLI first, then a small FastAPI endpoint that runs the same pipeline.

Out of scope for this MVP: live Chzzk/SOOP API collection, browser crawling, Whisper, OCR, scene detection, Adobe UXP panel, React dashboard, PostgreSQL, Redis.

## Target File Structure

- Create: `pyproject.toml` - package metadata, dependencies, lint/test commands.
- Modify: `README.md` - MVP usage and project direction.
- Create: `src/editflow/__init__.py` - package version.
- Create: `src/editflow/models.py` - shared dataclasses and marker enums.
- Create: `src/editflow/ingest/chat.py` - chat CSV/JSON parser.
- Create: `src/editflow/ingest/heatmap.py` - heatmap CSV/JSON parser.
- Create: `src/editflow/analysis/peaks.py` - threshold-based peak detection.
- Create: `src/editflow/analysis/markers.py` - evidence merging and marker classification.
- Create: `src/editflow/exporters/premiere_xml.py` - XML marker export.
- Create: `src/editflow/exporters/csv_report.py` - CSV sidecar report.
- Create: `src/editflow/pipeline.py` - orchestration used by CLI and API.
- Create: `src/editflow/cli.py` - command-line entrypoint.
- Create: `src/editflow/api.py` - FastAPI endpoint.
- Create: `examples/chat.csv` - deterministic sample chat data.
- Create: `examples/heatmap.csv` - deterministic sample heatmap data.
- Create: `tests/test_models.py` - model behavior tests.
- Create: `tests/test_chat_ingest.py` - chat parser tests.
- Create: `tests/test_heatmap_ingest.py` - heatmap parser tests.
- Create: `tests/test_peaks.py` - peak detection tests.
- Create: `tests/test_markers.py` - marker classification tests.
- Create: `tests/test_exporters.py` - XML and CSV exporter tests.
- Create: `tests/test_pipeline_cli_api.py` - end-to-end, CLI, and API tests.
- Create: `docs/premiere-import-checklist.md` - manual verification checklist.

## Data Contracts

Chat CSV:

```csv
second,message
8,ㅋㅋㅋ
9,미쳤다
10,ㅋㅋㅋㅋㅋㅋ
42,와 이건 살려야됨
43,ㅋㅋㅋㅋ
```

Heatmap CSV:

```csv
second,score
10,0.92
43,0.84
120,0.78
```

Generated marker:

```python
Marker(
    second=10,
    grade=MarkerGrade.S,
    color=MarkerColor.PURPLE,
    title="S급 하이라이트",
    memo="무조건 살려야 하는 핵심 구간! 숏폼 제작 1순위 후보입니다.",
    evidence=["chat_peak", "heatmap_peak"],
    confidence=1.0,
)
```

### Task 1: Project Bootstrap

**Files:**
- Create: `pyproject.toml`
- Create: `src/editflow/__init__.py`
- Create: `examples/chat.csv`
- Create: `examples/heatmap.csv`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write the first failing package test**

Create `tests/test_models.py`:

```python
from editflow import __version__


def test_package_version_exists():
    assert __version__ == "0.1.0"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_models.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'editflow'`.

- [ ] **Step 3: Create package config and version file**

Create `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=69", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "editflow"
version = "0.1.0"
description = "AI-assisted highlight marker generator for Korean stream editing workflows."
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.115.0",
  "typer>=0.12.0",
  "uvicorn>=0.30.0",
]

[project.optional-dependencies]
dev = [
  "httpx>=0.27.0",
  "pytest>=8.0.0",
  "ruff>=0.6.0",
]

[project.scripts]
editflow = "editflow.cli:app"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
```

Create `src/editflow/__init__.py`:

```python
__version__ = "0.1.0"
```

Create `examples/chat.csv`:

```csv
second,message
8,ㅋㅋㅋ
9,미쳤다
10,ㅋㅋㅋㅋㅋㅋ
42,와 이건 살려야됨
43,ㅋㅋㅋㅋ
44,레전드
120,정보 좋다
```

Create `examples/heatmap.csv`:

```csv
second,score
10,0.92
43,0.84
120,0.78
```

- [ ] **Step 4: Run the package test**

Run: `pytest tests/test_models.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/editflow/__init__.py examples/chat.csv examples/heatmap.csv tests/test_models.py
git commit -m "chore: bootstrap editflow python package"
```

### Task 2: Domain Models

**Files:**
- Create: `src/editflow/models.py`
- Modify: `tests/test_models.py`

- [ ] **Step 1: Write failing model tests**

Replace `tests/test_models.py` with:

```python
from editflow import __version__
from editflow.models import ChatBucket, HeatmapPoint, Marker, MarkerColor, MarkerGrade


def test_package_version_exists():
    assert __version__ == "0.1.0"


def test_marker_grade_maps_to_expected_color_and_memo():
    marker = Marker.from_grade(
        second=10,
        grade=MarkerGrade.S,
        evidence=["chat_peak", "heatmap_peak"],
        confidence=1.0,
    )

    assert marker.color == MarkerColor.PURPLE
    assert marker.title == "S급 하이라이트"
    assert marker.memo == "무조건 살려야 하는 핵심 구간! 숏폼 제작 1순위 후보입니다."


def test_chat_bucket_counts_laugh_token():
    bucket = ChatBucket(second=3, messages=["ㅋㅋㅋ", "좋다", "ㅋㅋㅋㅋ"])

    assert bucket.message_count == 3
    assert bucket.laugh_count == 2


def test_heatmap_point_requires_normalized_score():
    point = HeatmapPoint(second=5, score=0.75)

    assert point.second == 5
    assert point.score == 0.75
```

- [ ] **Step 2: Run tests to verify missing models**

Run: `pytest tests/test_models.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'editflow.models'`.

- [ ] **Step 3: Implement domain models**

Create `src/editflow/models.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class MarkerGrade(StrEnum):
    S = "S"
    A = "A"
    B = "B"


class MarkerColor(StrEnum):
    PURPLE = "purple"
    RED = "red"
    YELLOW = "yellow"


GRADE_STYLE = {
    MarkerGrade.S: (
        MarkerColor.PURPLE,
        "S급 하이라이트",
        "무조건 살려야 하는 핵심 구간! 숏폼 제작 1순위 후보입니다.",
    ),
    MarkerGrade.A: (
        MarkerColor.RED,
        "A급 채팅 피크",
        "시청자 실시간 반응 폭발! 웃음 포인트나 소통 구간입니다.",
    ),
    MarkerGrade.B: (
        MarkerColor.YELLOW,
        "B급 열지도 피크",
        "방송 후 반복 시청 집중 구간! 정보 전달 혹은 몰입 토크입니다.",
    ),
}


@dataclass(frozen=True)
class ChatBucket:
    second: int
    messages: list[str]

    @property
    def message_count(self) -> int:
        return len(self.messages)

    @property
    def laugh_count(self) -> int:
        return sum(1 for message in self.messages if "ㅋ" in message)


@dataclass(frozen=True)
class HeatmapPoint:
    second: int
    score: float

    def __post_init__(self) -> None:
        if not 0 <= self.score <= 1:
            raise ValueError("heatmap score must be between 0 and 1")


@dataclass(frozen=True)
class Peak:
    second: int
    source: str
    strength: float


@dataclass(frozen=True)
class Marker:
    second: int
    grade: MarkerGrade
    color: MarkerColor
    title: str
    memo: str
    evidence: list[str]
    confidence: float

    @classmethod
    def from_grade(
        cls,
        *,
        second: int,
        grade: MarkerGrade,
        evidence: list[str],
        confidence: float,
    ) -> "Marker":
        color, title, memo = GRADE_STYLE[grade]
        return cls(
            second=second,
            grade=grade,
            color=color,
            title=title,
            memo=memo,
            evidence=evidence,
            confidence=confidence,
        )
```

- [ ] **Step 4: Run model tests**

Run: `pytest tests/test_models.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/editflow/models.py tests/test_models.py
git commit -m "feat: add editflow domain models"
```

### Task 3: Chat Log Ingestion

**Files:**
- Create: `src/editflow/ingest/__init__.py`
- Create: `src/editflow/ingest/chat.py`
- Create: `tests/test_chat_ingest.py`

- [ ] **Step 1: Write failing chat ingestion tests**

Create `tests/test_chat_ingest.py`:

```python
from pathlib import Path

from editflow.ingest.chat import load_chat_buckets


def test_load_chat_csv_groups_messages_by_second(tmp_path: Path):
    path = tmp_path / "chat.csv"
    path.write_text(
        "second,message\n"
        "10,ㅋㅋㅋ\n"
        "10,미쳤다\n"
        "11,좋다\n",
        encoding="utf-8",
    )

    buckets = load_chat_buckets(path)

    assert buckets[0].second == 10
    assert buckets[0].message_count == 2
    assert buckets[0].laugh_count == 1
    assert buckets[1].second == 11


def test_load_chat_json_groups_messages_by_second(tmp_path: Path):
    path = tmp_path / "chat.json"
    path.write_text(
        '[{"second": 5, "message": "ㅋㅋ"}, {"second": 5, "message": "나이스"}]',
        encoding="utf-8",
    )

    buckets = load_chat_buckets(path)

    assert len(buckets) == 1
    assert buckets[0].messages == ["ㅋㅋ", "나이스"]
```

- [ ] **Step 2: Run tests to verify missing parser**

Run: `pytest tests/test_chat_ingest.py -v`

Expected: FAIL with `ModuleNotFoundError` or `ImportError`.

- [ ] **Step 3: Implement chat parser**

Create `src/editflow/ingest/__init__.py`:

```python
"""Input parsers for EditFlow."""
```

Create `src/editflow/ingest/chat.py`:

```python
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

from editflow.models import ChatBucket


def load_chat_buckets(path: Path) -> list[ChatBucket]:
    rows = _read_rows(path)
    grouped: dict[int, list[str]] = defaultdict(list)

    for row in rows:
        second = int(row["second"])
        message = str(row["message"]).strip()
        if message:
            grouped[second].append(message)

    return [ChatBucket(second=second, messages=grouped[second]) for second in sorted(grouped)]


def _read_rows(path: Path) -> list[dict[str, object]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8", newline="") as file:
            return list(csv.DictReader(file))
    if suffix == ".json":
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError("chat JSON must be a list of objects")
        return data
    raise ValueError(f"unsupported chat file extension: {suffix}")
```

- [ ] **Step 4: Run chat ingestion tests**

Run: `pytest tests/test_chat_ingest.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/editflow/ingest/__init__.py src/editflow/ingest/chat.py tests/test_chat_ingest.py
git commit -m "feat: parse chat logs into time buckets"
```

### Task 4: Heatmap Ingestion

**Files:**
- Create: `src/editflow/ingest/heatmap.py`
- Create: `tests/test_heatmap_ingest.py`

- [ ] **Step 1: Write failing heatmap ingestion tests**

Create `tests/test_heatmap_ingest.py`:

```python
from pathlib import Path

import pytest

from editflow.ingest.heatmap import load_heatmap_points


def test_load_heatmap_csv_sorts_points(tmp_path: Path):
    path = tmp_path / "heatmap.csv"
    path.write_text("second,score\n12,0.5\n3,0.9\n", encoding="utf-8")

    points = load_heatmap_points(path)

    assert [point.second for point in points] == [3, 12]
    assert points[0].score == 0.9


def test_load_heatmap_rejects_score_outside_normalized_range(tmp_path: Path):
    path = tmp_path / "heatmap.csv"
    path.write_text("second,score\n12,1.5\n", encoding="utf-8")

    with pytest.raises(ValueError, match="between 0 and 1"):
        load_heatmap_points(path)
```

- [ ] **Step 2: Run tests to verify missing parser**

Run: `pytest tests/test_heatmap_ingest.py -v`

Expected: FAIL with `ModuleNotFoundError` or `ImportError`.

- [ ] **Step 3: Implement heatmap parser**

Create `src/editflow/ingest/heatmap.py`:

```python
from __future__ import annotations

import csv
import json
from pathlib import Path

from editflow.models import HeatmapPoint


def load_heatmap_points(path: Path) -> list[HeatmapPoint]:
    rows = _read_rows(path)
    points = [
        HeatmapPoint(second=int(row["second"]), score=float(row["score"]))
        for row in rows
    ]
    return sorted(points, key=lambda point: point.second)


def _read_rows(path: Path) -> list[dict[str, object]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8", newline="") as file:
            return list(csv.DictReader(file))
    if suffix == ".json":
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError("heatmap JSON must be a list of objects")
        return data
    raise ValueError(f"unsupported heatmap file extension: {suffix}")
```

- [ ] **Step 4: Run heatmap ingestion tests**

Run: `pytest tests/test_heatmap_ingest.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/editflow/ingest/heatmap.py tests/test_heatmap_ingest.py
git commit -m "feat: parse replay heatmap points"
```

### Task 5: Peak Detection

**Files:**
- Create: `src/editflow/analysis/__init__.py`
- Create: `src/editflow/analysis/peaks.py`
- Create: `tests/test_peaks.py`

- [ ] **Step 1: Write failing peak detection tests**

Create `tests/test_peaks.py`:

```python
from editflow.analysis.peaks import detect_chat_peaks, detect_heatmap_peaks
from editflow.models import ChatBucket, HeatmapPoint


def test_detect_chat_peaks_uses_message_and_laugh_velocity():
    buckets = [
        ChatBucket(second=1, messages=["좋다"]),
        ChatBucket(second=2, messages=["ㅋㅋ", "ㅋㅋㅋ", "미쳤다", "와"]),
        ChatBucket(second=3, messages=["음"]),
    ]

    peaks = detect_chat_peaks(buckets, min_messages=3, min_laughs=2)

    assert len(peaks) == 1
    assert peaks[0].second == 2
    assert peaks[0].source == "chat_peak"
    assert peaks[0].strength == 1.0


def test_detect_heatmap_peaks_uses_minimum_score():
    points = [
        HeatmapPoint(second=10, score=0.4),
        HeatmapPoint(second=20, score=0.82),
    ]

    peaks = detect_heatmap_peaks(points, min_score=0.8)

    assert len(peaks) == 1
    assert peaks[0].second == 20
    assert peaks[0].source == "heatmap_peak"
    assert peaks[0].strength == 0.82
```

- [ ] **Step 2: Run tests to verify missing analysis module**

Run: `pytest tests/test_peaks.py -v`

Expected: FAIL with `ModuleNotFoundError` or `ImportError`.

- [ ] **Step 3: Implement peak detection**

Create `src/editflow/analysis/__init__.py`:

```python
"""Analysis modules for EditFlow."""
```

Create `src/editflow/analysis/peaks.py`:

```python
from __future__ import annotations

from editflow.models import ChatBucket, HeatmapPoint, Peak


def detect_chat_peaks(
    buckets: list[ChatBucket],
    *,
    min_messages: int = 3,
    min_laughs: int = 2,
) -> list[Peak]:
    peaks: list[Peak] = []
    max_count = max((bucket.message_count for bucket in buckets), default=1)

    for bucket in buckets:
        if bucket.message_count >= min_messages or bucket.laugh_count >= min_laughs:
            strength = round(bucket.message_count / max_count, 4)
            peaks.append(Peak(second=bucket.second, source="chat_peak", strength=strength))

    return peaks


def detect_heatmap_peaks(
    points: list[HeatmapPoint],
    *,
    min_score: float = 0.75,
) -> list[Peak]:
    return [
        Peak(second=point.second, source="heatmap_peak", strength=point.score)
        for point in points
        if point.score >= min_score
    ]
```

- [ ] **Step 4: Run peak tests**

Run: `pytest tests/test_peaks.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/editflow/analysis/__init__.py src/editflow/analysis/peaks.py tests/test_peaks.py
git commit -m "feat: detect chat and heatmap peaks"
```

### Task 6: Marker Classification

**Files:**
- Create: `src/editflow/analysis/markers.py`
- Create: `tests/test_markers.py`

- [ ] **Step 1: Write failing marker classification tests**

Create `tests/test_markers.py`:

```python
from editflow.analysis.markers import build_markers
from editflow.models import MarkerColor, MarkerGrade, Peak


def test_build_markers_creates_s_grade_when_sources_overlap():
    markers = build_markers(
        chat_peaks=[Peak(second=10, source="chat_peak", strength=1.0)],
        heatmap_peaks=[Peak(second=12, source="heatmap_peak", strength=0.9)],
        overlap_seconds=3,
    )

    assert len(markers) == 1
    assert markers[0].second == 10
    assert markers[0].grade == MarkerGrade.S
    assert markers[0].color == MarkerColor.PURPLE
    assert markers[0].evidence == ["chat_peak", "heatmap_peak"]


def test_build_markers_keeps_single_source_markers():
    markers = build_markers(
        chat_peaks=[Peak(second=30, source="chat_peak", strength=0.8)],
        heatmap_peaks=[Peak(second=90, source="heatmap_peak", strength=0.76)],
        overlap_seconds=3,
    )

    assert [marker.grade for marker in markers] == [MarkerGrade.A, MarkerGrade.B]
    assert [marker.second for marker in markers] == [30, 90]
```

- [ ] **Step 2: Run tests to verify missing marker builder**

Run: `pytest tests/test_markers.py -v`

Expected: FAIL with `ModuleNotFoundError` or `ImportError`.

- [ ] **Step 3: Implement marker classification**

Create `src/editflow/analysis/markers.py`:

```python
from __future__ import annotations

from editflow.models import Marker, MarkerGrade, Peak


def build_markers(
    *,
    chat_peaks: list[Peak],
    heatmap_peaks: list[Peak],
    overlap_seconds: int = 5,
) -> list[Marker]:
    markers: list[Marker] = []
    used_heatmap_seconds: set[int] = set()

    for chat_peak in chat_peaks:
        matching_heatmap = _nearest_peak(chat_peak, heatmap_peaks, overlap_seconds)
        if matching_heatmap is not None:
            used_heatmap_seconds.add(matching_heatmap.second)
            confidence = round((chat_peak.strength + matching_heatmap.strength) / 2, 4)
            markers.append(
                Marker.from_grade(
                    second=chat_peak.second,
                    grade=MarkerGrade.S,
                    evidence=["chat_peak", "heatmap_peak"],
                    confidence=confidence,
                )
            )
        else:
            markers.append(
                Marker.from_grade(
                    second=chat_peak.second,
                    grade=MarkerGrade.A,
                    evidence=["chat_peak"],
                    confidence=chat_peak.strength,
                )
            )

    for heatmap_peak in heatmap_peaks:
        if heatmap_peak.second in used_heatmap_seconds:
            continue
        markers.append(
            Marker.from_grade(
                second=heatmap_peak.second,
                grade=MarkerGrade.B,
                evidence=["heatmap_peak"],
                confidence=heatmap_peak.strength,
            )
        )

    return sorted(markers, key=lambda marker: marker.second)


def _nearest_peak(reference: Peak, candidates: list[Peak], overlap_seconds: int) -> Peak | None:
    overlapping = [
        candidate
        for candidate in candidates
        if abs(candidate.second - reference.second) <= overlap_seconds
    ]
    if not overlapping:
        return None
    return min(overlapping, key=lambda candidate: abs(candidate.second - reference.second))
```

- [ ] **Step 4: Run marker tests**

Run: `pytest tests/test_markers.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/editflow/analysis/markers.py tests/test_markers.py
git commit -m "feat: classify highlight markers by evidence"
```

### Task 7: XML and CSV Exporters

**Files:**
- Create: `src/editflow/exporters/__init__.py`
- Create: `src/editflow/exporters/premiere_xml.py`
- Create: `src/editflow/exporters/csv_report.py`
- Create: `tests/test_exporters.py`

- [ ] **Step 1: Write failing exporter tests**

Create `tests/test_exporters.py`:

```python
from pathlib import Path
from xml.etree import ElementTree

from editflow.exporters.csv_report import write_marker_csv
from editflow.exporters.premiere_xml import build_premiere_xml
from editflow.models import Marker, MarkerGrade


def test_build_premiere_xml_contains_sequence_markers():
    marker = Marker.from_grade(
        second=10,
        grade=MarkerGrade.S,
        evidence=["chat_peak", "heatmap_peak"],
        confidence=0.95,
    )

    xml_text = build_premiere_xml([marker], sequence_name="EditFlow Test", fps=30)
    root = ElementTree.fromstring(xml_text)
    marker_node = root.find(".//marker")

    assert root.tag == "xmeml"
    assert marker_node is not None
    assert marker_node.findtext("name") == "[PURPLE] S급 하이라이트"
    assert marker_node.findtext("in") == "300"


def test_write_marker_csv_outputs_sidecar_report(tmp_path: Path):
    marker = Marker.from_grade(
        second=10,
        grade=MarkerGrade.A,
        evidence=["chat_peak"],
        confidence=0.8,
    )
    path = tmp_path / "markers.csv"

    write_marker_csv([marker], path)

    assert "second,grade,color,title,memo,evidence,confidence" in path.read_text(encoding="utf-8")
    assert "10,A,red,A급 채팅 피크" in path.read_text(encoding="utf-8")
```

- [ ] **Step 2: Run tests to verify missing exporters**

Run: `pytest tests/test_exporters.py -v`

Expected: FAIL with `ModuleNotFoundError` or `ImportError`.

- [ ] **Step 3: Implement XML and CSV exporters**

Create `src/editflow/exporters/__init__.py`:

```python
"""Output exporters for EditFlow."""
```

Create `src/editflow/exporters/premiere_xml.py`:

```python
from __future__ import annotations

from xml.dom import minidom
from xml.etree import ElementTree

from editflow.models import Marker


def build_premiere_xml(
    markers: list[Marker],
    *,
    sequence_name: str = "EditFlow Markers",
    fps: int = 30,
) -> str:
    root = ElementTree.Element("xmeml", {"version": "4"})
    sequence = ElementTree.SubElement(root, "sequence", {"id": "editflow-sequence"})
    ElementTree.SubElement(sequence, "name").text = sequence_name
    ElementTree.SubElement(sequence, "duration").text = str(_duration_frames(markers, fps))

    rate = ElementTree.SubElement(sequence, "rate")
    ElementTree.SubElement(rate, "timebase").text = str(fps)
    ElementTree.SubElement(rate, "ntsc").text = "FALSE"

    for marker in markers:
        marker_node = ElementTree.SubElement(sequence, "marker")
        frame = marker.second * fps
        ElementTree.SubElement(marker_node, "name").text = f"[{marker.color.upper()}] {marker.title}"
        ElementTree.SubElement(marker_node, "comment").text = (
            f"{marker.memo} | evidence={','.join(marker.evidence)} | confidence={marker.confidence:.2f}"
        )
        ElementTree.SubElement(marker_node, "in").text = str(frame)
        ElementTree.SubElement(marker_node, "out").text = str(frame + fps)

    rough_xml = ElementTree.tostring(root, encoding="utf-8")
    return minidom.parseString(rough_xml).toprettyxml(indent="  ")


def _duration_frames(markers: list[Marker], fps: int) -> int:
    if not markers:
        return fps
    return (max(marker.second for marker in markers) + 60) * fps
```

Create `src/editflow/exporters/csv_report.py`:

```python
from __future__ import annotations

import csv
from pathlib import Path

from editflow.models import Marker


def write_marker_csv(markers: list[Marker], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["second", "grade", "color", "title", "memo", "evidence", "confidence"],
        )
        writer.writeheader()
        for marker in markers:
            writer.writerow(
                {
                    "second": marker.second,
                    "grade": marker.grade.value,
                    "color": marker.color.value,
                    "title": marker.title,
                    "memo": marker.memo,
                    "evidence": ",".join(marker.evidence),
                    "confidence": f"{marker.confidence:.4f}",
                }
            )
```

- [ ] **Step 4: Run exporter tests**

Run: `pytest tests/test_exporters.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/editflow/exporters tests/test_exporters.py
git commit -m "feat: export markers as xml and csv"
```

### Task 8: Pipeline and CLI

**Files:**
- Create: `src/editflow/pipeline.py`
- Create: `src/editflow/cli.py`
- Create: `tests/test_pipeline_cli_api.py`

- [ ] **Step 1: Write failing pipeline and CLI tests**

Create `tests/test_pipeline_cli_api.py`:

```python
from pathlib import Path

from typer.testing import CliRunner

from editflow.cli import app
from editflow.pipeline import run_pipeline


def test_run_pipeline_creates_xml_and_csv(tmp_path: Path):
    chat_path = tmp_path / "chat.csv"
    heatmap_path = tmp_path / "heatmap.csv"
    output_dir = tmp_path / "dist"
    chat_path.write_text("second,message\n10,ㅋㅋ\n10,ㅋㅋㅋ\n10,미쳤다\n", encoding="utf-8")
    heatmap_path.write_text("second,score\n11,0.9\n", encoding="utf-8")

    result = run_pipeline(chat_path=chat_path, heatmap_path=heatmap_path, output_dir=output_dir)

    assert result.marker_count == 1
    assert result.xml_path.exists()
    assert result.csv_path.exists()


def test_cli_analyze_command_runs_pipeline(tmp_path: Path):
    chat_path = tmp_path / "chat.csv"
    heatmap_path = tmp_path / "heatmap.csv"
    output_dir = tmp_path / "dist"
    chat_path.write_text("second,message\n10,ㅋㅋ\n10,ㅋㅋㅋ\n10,미쳤다\n", encoding="utf-8")
    heatmap_path.write_text("second,score\n11,0.9\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "analyze",
            "--chat",
            str(chat_path),
            "--heatmap",
            str(heatmap_path),
            "--output-dir",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Generated 1 marker" in result.stdout
```

- [ ] **Step 2: Run tests to verify missing pipeline**

Run: `pytest tests/test_pipeline_cli_api.py -v`

Expected: FAIL with `ModuleNotFoundError` or `ImportError`.

- [ ] **Step 3: Implement pipeline and CLI**

Create `src/editflow/pipeline.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from editflow.analysis.markers import build_markers
from editflow.analysis.peaks import detect_chat_peaks, detect_heatmap_peaks
from editflow.exporters.csv_report import write_marker_csv
from editflow.exporters.premiere_xml import build_premiere_xml
from editflow.ingest.chat import load_chat_buckets
from editflow.ingest.heatmap import load_heatmap_points
from editflow.models import Marker


@dataclass(frozen=True)
class PipelineResult:
    markers: list[Marker]
    xml_path: Path
    csv_path: Path

    @property
    def marker_count(self) -> int:
        return len(self.markers)


def run_pipeline(
    *,
    chat_path: Path,
    heatmap_path: Path,
    output_dir: Path,
    fps: int = 30,
) -> PipelineResult:
    chat_buckets = load_chat_buckets(chat_path)
    heatmap_points = load_heatmap_points(heatmap_path)
    chat_peaks = detect_chat_peaks(chat_buckets)
    heatmap_peaks = detect_heatmap_peaks(heatmap_points)
    markers = build_markers(chat_peaks=chat_peaks, heatmap_peaks=heatmap_peaks)

    output_dir.mkdir(parents=True, exist_ok=True)
    xml_path = output_dir / "editflow_markers.xml"
    csv_path = output_dir / "editflow_markers.csv"
    xml_path.write_text(build_premiere_xml(markers, fps=fps), encoding="utf-8")
    write_marker_csv(markers, csv_path)

    return PipelineResult(markers=markers, xml_path=xml_path, csv_path=csv_path)
```

Create `src/editflow/cli.py`:

```python
from __future__ import annotations

from pathlib import Path

import typer

from editflow.pipeline import run_pipeline

app = typer.Typer(help="EditFlow highlight marker generator.")


@app.command()
def analyze(
    chat: Path = typer.Option(..., exists=True, readable=True, help="Chat CSV or JSON file."),
    heatmap: Path = typer.Option(..., exists=True, readable=True, help="Heatmap CSV or JSON file."),
    output_dir: Path = typer.Option(Path("dist"), help="Directory for XML and CSV outputs."),
    fps: int = typer.Option(30, min=1, help="Timeline frames per second."),
) -> None:
    result = run_pipeline(chat_path=chat, heatmap_path=heatmap, output_dir=output_dir, fps=fps)
    marker_word = "marker" if result.marker_count == 1 else "markers"
    typer.echo(f"Generated {result.marker_count} {marker_word}")
    typer.echo(f"XML: {result.xml_path}")
    typer.echo(f"CSV: {result.csv_path}")
```

- [ ] **Step 4: Run pipeline and CLI tests**

Run: `pytest tests/test_pipeline_cli_api.py -v`

Expected: PASS.

- [ ] **Step 5: Run the sample command**

Run: `editflow analyze --chat examples/chat.csv --heatmap examples/heatmap.csv --output-dir dist`

Expected:

```text
Generated 3 markers
XML: dist/editflow_markers.xml
CSV: dist/editflow_markers.csv
```

- [ ] **Step 6: Commit**

```bash
git add src/editflow/pipeline.py src/editflow/cli.py tests/test_pipeline_cli_api.py
git commit -m "feat: add marker generation pipeline and cli"
```

### Task 9: FastAPI Endpoint

**Files:**
- Create: `src/editflow/api.py`
- Modify: `tests/test_pipeline_cli_api.py`

- [ ] **Step 1: Add failing API test**

Append to `tests/test_pipeline_cli_api.py`:

```python
from fastapi.testclient import TestClient

from editflow.api import api


def test_api_analyze_endpoint_runs_pipeline(tmp_path: Path):
    chat_path = tmp_path / "chat.csv"
    heatmap_path = tmp_path / "heatmap.csv"
    output_dir = tmp_path / "dist"
    chat_path.write_text("second,message\n10,ㅋㅋ\n10,ㅋㅋㅋ\n10,미쳤다\n", encoding="utf-8")
    heatmap_path.write_text("second,score\n11,0.9\n", encoding="utf-8")

    response = TestClient(api).post(
        "/analyze",
        json={
            "chat_path": str(chat_path),
            "heatmap_path": str(heatmap_path),
            "output_dir": str(output_dir),
            "fps": 30,
        },
    )

    assert response.status_code == 200
    assert response.json()["marker_count"] == 1
    assert response.json()["xml_path"].endswith("editflow_markers.xml")
```

- [ ] **Step 2: Run the API test to verify missing endpoint**

Run: `pytest tests/test_pipeline_cli_api.py::test_api_analyze_endpoint_runs_pipeline -v`

Expected: FAIL with `ModuleNotFoundError` or `ImportError`.

- [ ] **Step 3: Implement API endpoint**

Create `src/editflow/api.py`:

```python
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, Field

from editflow.pipeline import run_pipeline

api = FastAPI(title="EditFlow API", version="0.1.0")


class AnalyzeRequest(BaseModel):
    chat_path: str
    heatmap_path: str
    output_dir: str = "dist"
    fps: int = Field(default=30, ge=1)


class AnalyzeResponse(BaseModel):
    marker_count: int
    xml_path: str
    csv_path: str


@api.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@api.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    result = run_pipeline(
        chat_path=Path(request.chat_path),
        heatmap_path=Path(request.heatmap_path),
        output_dir=Path(request.output_dir),
        fps=request.fps,
    )
    return AnalyzeResponse(
        marker_count=result.marker_count,
        xml_path=str(result.xml_path),
        csv_path=str(result.csv_path),
    )
```

- [ ] **Step 4: Run API tests**

Run: `pytest tests/test_pipeline_cli_api.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/editflow/api.py tests/test_pipeline_cli_api.py
git commit -m "feat: expose editflow pipeline through fastapi"
```

### Task 10: README and Premiere Verification Checklist

**Files:**
- Modify: `README.md`
- Create: `docs/premiere-import-checklist.md`

- [ ] **Step 1: Update README**

Replace `README.md` with:

```markdown
# EditFlow

EditFlow is an AI-assisted editing workflow tool for Korean stream highlights.

The first MVP analyzes chat reaction spikes and replay heatmap peaks, then generates marker files that help editors find high-value moments faster.

## MVP Features

- Parse chat logs from CSV or JSON.
- Parse replay heatmap data from CSV or JSON.
- Detect chat velocity and laugh spikes.
- Detect replay heatmap peaks.
- Classify markers:
  - Purple / S-grade: chat peak + heatmap peak overlap.
  - Red / A-grade: chat peak only.
  - Yellow / B-grade: heatmap peak only.
- Export:
  - `editflow_markers.xml`
  - `editflow_markers.csv`

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run Tests

```bash
pytest -v
ruff check .
```

## Run MVP

```bash
editflow analyze --chat examples/chat.csv --heatmap examples/heatmap.csv --output-dir dist
```

Expected output:

```text
Generated 3 markers
XML: dist/editflow_markers.xml
CSV: dist/editflow_markers.csv
```

## API

```bash
uvicorn editflow.api:api --reload
```

Then POST:

```json
{
  "chat_path": "examples/chat.csv",
  "heatmap_path": "examples/heatmap.csv",
  "output_dir": "dist",
  "fps": 30
}
```

to:

```text
POST /analyze
```

## Project Direction

This MVP intentionally avoids live collection, Whisper, OCR, and Adobe panel work. After marker generation is reliable, the next phases are:

1. Chzzk/SOOP data collection adapters.
2. YouTube `yt-dlp` replay ingestion.
3. Whisper-based keyword and context extraction.
4. OpenCV/OCR-based visual signals.
5. React/Next.js dashboard.
6. Adobe UXP Premiere panel.
```

- [ ] **Step 2: Add Premiere manual verification checklist**

Create `docs/premiere-import-checklist.md`:

```markdown
# Premiere Import Verification Checklist

Use this checklist after `dist/editflow_markers.xml` is generated.

## Test Asset

- Use a local test sequence with FPS set to 30.
- Generate markers with:

```bash
editflow analyze --chat examples/chat.csv --heatmap examples/heatmap.csv --output-dir dist --fps 30
```

## Import Steps

1. Open Adobe Premiere Pro.
2. Create or open a test project.
3. Use `File > Import`.
4. Select `dist/editflow_markers.xml`.
5. Confirm the imported sequence or marker data appears in the project panel.
6. Open the imported sequence.

## Expected Marker Checks

- Marker near `00:00:10:00` exists.
- Marker near `00:00:43:00` exists.
- Marker near `00:02:00:00` exists.
- S-grade marker name includes `[PURPLE] S급 하이라이트`.
- A-grade marker name includes `[RED] A급 채팅 피크`.
- B-grade marker name includes `[YELLOW] B급 열지도 피크`.
- Marker comment contains `evidence=`.
- Marker comment contains `confidence=`.

## Result Log

Record the verification result in the pull request or commit notes:

```text
Premiere import verification:
- Premiere version:
- XML imported:
- Marker timing correct:
- Marker names visible:
- Marker comments visible:
- Notes:
```
```

- [ ] **Step 3: Run full verification**

Run: `pytest -v`

Expected: PASS.

Run: `ruff check .`

Expected: PASS.

Run: `editflow analyze --chat examples/chat.csv --heatmap examples/heatmap.csv --output-dir dist`

Expected:

```text
Generated 3 markers
XML: dist/editflow_markers.xml
CSV: dist/editflow_markers.csv
```

- [ ] **Step 4: Commit**

```bash
git add README.md docs/premiere-import-checklist.md
git commit -m "docs: document editflow mvp workflow"
```

## Final Verification

Run these commands from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -v
ruff check .
editflow analyze --chat examples/chat.csv --heatmap examples/heatmap.csv --output-dir dist
uvicorn editflow.api:api --reload
```

Expected test result:

```text
tests passed
```

Expected CLI result:

```text
Generated 3 markers
XML: dist/editflow_markers.xml
CSV: dist/editflow_markers.csv
```

Expected API health result:

```text
GET /health -> {"status":"ok"}
```

## Self-Review

Spec coverage:

- Notion goal, "시간 부족" and "편집점 찾기 피로도" reduction: covered by marker generation MVP.
- Data collection foundation: covered by local CSV/JSON ingestion for chat and heatmap data.
- AI analysis engine direction: narrowed to deterministic signal analysis for MVP; Whisper/OCR/scene detection are documented as next phases.
- XML workflow integration: covered by `premiere_xml.py`, CLI output, and manual Premiere checklist.
- Low-cost stack: covered by Python, FastAPI, Typer, pytest, and standard-library XML generation.
- Core marker logic and weights: covered by S/A/B grade classification and overlap window scoring.

No placeholder terms are used as implementation requirements. Function names are consistent across tests, modules, CLI, and API.
