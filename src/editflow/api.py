"""FastAPI adapter for the EditFlow analysis pipeline."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from editflow.pipeline import AnalysisSettings, run_analysis_from_text

api = FastAPI(title="EditFlow API", version="0.1.0")
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    """Request body for browser-uploaded chat and heatmap text."""

    chat_text: str
    chat_filename: str = "chat.csv"
    heatmap_text: str
    heatmap_filename: str = "heatmap.csv"
    fps: int = Field(default=30, ge=1)
    min_messages: int = Field(default=3, ge=1)
    min_laughs: int = Field(default=2, ge=1)
    min_heatmap_score: float = Field(default=0.75, ge=0, le=1)
    overlap_seconds: int = Field(default=5, ge=0)


class MarkerResponse(BaseModel):
    """Serializable marker response."""

    second: int
    grade: str
    color: str
    title: str
    memo: str
    evidence: list[str]
    confidence: float


class AnalyzeResponse(BaseModel):
    """Response returned to the workbench UI."""

    marker_count: int
    markers: list[MarkerResponse]
    xml_text: str
    csv_text: str


@api.get("/health")
def health() -> dict[str, str]:
    """Report API health."""
    return {"status": "ok"}


@api.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """Run marker analysis and return markers plus export texts."""
    result = run_analysis_from_text(
        chat_text=request.chat_text,
        chat_filename=request.chat_filename,
        heatmap_text=request.heatmap_text,
        heatmap_filename=request.heatmap_filename,
        settings=AnalysisSettings(
            fps=request.fps,
            min_messages=request.min_messages,
            min_laughs=request.min_laughs,
            min_heatmap_score=request.min_heatmap_score,
            overlap_seconds=request.overlap_seconds,
        ),
    )
    return AnalyzeResponse(
        marker_count=result.marker_count,
        markers=[
            MarkerResponse(
                second=marker.second,
                grade=marker.grade.value,
                color=marker.color.value,
                title=marker.title,
                memo=marker.memo,
                evidence=marker.evidence,
                confidence=marker.confidence,
            )
            for marker in result.markers
        ],
        xml_text=result.xml_text,
        csv_text=result.csv_text,
    )
