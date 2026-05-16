"""Shared dataclasses and marker enums for EditFlow."""

from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class ChatBucket:
    """Chat messages grouped by playback second."""
    second: int
    messages: list[str]

    @property
    def message_count(self) -> int:
        """Return the number of messages in the bucket."""
        return len(self.messages)

    @property
    def laugh_count(self) -> int:
        """Return the number of messages containing Korean laugh tokens."""
        return sum(1 for message in self.messages if "ㅋ" in message)


@dataclass(frozen=True)
class HeatmapPoint:
    """Replay heatmap score at a playback second."""
    second: int
    score: float

    def __post_init__(self) -> None:
        """Validate that heatmap scores are normalized."""
        if not 0 <= self.score <= 1:
            message = "heatmap score must be between 0 and 1"
            raise ValueError(message)


@dataclass(frozen=True)
class Peak:
    """Detected evidence peak from chat or replay heatmap data."""
    second: int
    source: str
    strength: float


class MarkerGrade(Enum):
    """Marker grade enumeration."""
    S = "S"
    A = "A"
    B = "B"


class MarkerColor(Enum):
    """Marker color enumeration."""
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


@dataclass
class Marker:
    """Represents a detected highlight marker."""
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
        """Create a marker with the standard style for its grade."""
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
