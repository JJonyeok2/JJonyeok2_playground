"""Shared dataclasses and marker enums for EditFlow."""

from dataclasses import dataclass
from enum import Enum


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
