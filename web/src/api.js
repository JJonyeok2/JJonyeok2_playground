import { gradeMeta } from "./config.js";
import { buildCsvText, buildPremiereXmlText } from "./exporters.js";

export const API_BASE_URL = "http://127.0.0.1:8000";

export async function requestBackendAnalysis(state, settings) {
  if (!state.chatText || !state.heatmapText) {
    throw new Error("Chat and heatmap data are required.");
  }

  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      chat_text: state.chatText,
      chat_filename: state.chatFileName || "chat.csv",
      heatmap_text: state.heatmapText,
      heatmap_filename: state.heatmapFileName || "heatmap.csv",
      fps: settings.fps,
      min_messages: settings.minMessages,
      min_laughs: settings.minLaughs,
      min_heatmap_score: settings.minHeatmapScore,
      overlap_seconds: settings.overlapSeconds,
      peak_merge_seconds: settings.peakMergeSeconds,
      max_markers: settings.maxMarkers,
      min_marker_gap_seconds: settings.minMarkerGapSeconds,
      pre_roll_seconds: settings.preRollSeconds,
      marker_duration_seconds: settings.markerDurationSeconds,
    }),
  });

  if (!response.ok) {
    throw new Error(`EditFlow API returned ${response.status}`);
  }

  return response.json();
}

export function applyBackendResult(state, result, settings) {
  state.markers = result.markers.map((marker) => normalizeBackendMarker(marker, settings));
  state.xmlText = result.xml_text || buildPremiereXmlText(state.markers, settings.fps);
  state.csvText = result.csv_text || buildCsvText(state.markers);
}

function normalizeBackendMarker(marker, settings) {
  const grade = String(marker.grade || "B").toUpperCase();
  const meta = gradeMeta[grade] || gradeMeta.B;
  return {
    second: Number(marker.second),
    peakSecond: Number(marker.second),
    grade,
    color: marker.color || meta.color,
    className: meta.className,
    title: marker.title || meta.title,
    memo: marker.memo || meta.memo,
    evidence: Array.isArray(marker.evidence) ? marker.evidence : [],
    confidence: Number(marker.confidence || 0),
    durationSeconds: settings.markerDurationSeconds,
  };
}
