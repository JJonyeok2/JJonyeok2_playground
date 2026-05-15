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
