import { applyBackendResult, requestBackendAnalysis } from "./api.js";
import { runLocalAnalysis } from "./analysis.js";
import { DEFAULT_FPS } from "./config.js";
import { readDataFile } from "./data.js";
import { exportMarkersAsCsv, exportMarkersAsXml } from "./exporters.js";
import { renderAnalysisResult, renderTimeline, updateSummary } from "./render.js";
import { state } from "./state.js";

const elements = {
  videoInput: document.getElementById("videoInput"),
  chatInput: document.getElementById("chatInput"),
  heatmapInput: document.getElementById("heatmapInput"),
  minMessages: document.getElementById("minMessages"),
  minLaughs: document.getElementById("minLaughs"),
  minHeatmapScore: document.getElementById("minHeatmapScore"),
  overlapSeconds: document.getElementById("overlapSeconds"),
  peakMergeSeconds: document.getElementById("peakMergeSeconds"),
  maxMarkers: document.getElementById("maxMarkers"),
  minMarkerGapSeconds: document.getElementById("minMarkerGapSeconds"),
  preRollSeconds: document.getElementById("preRollSeconds"),
  markerDurationSeconds: document.getElementById("markerDurationSeconds"),
  analyzeButton: document.getElementById("analyzeButton"),
  exportXmlButton: document.getElementById("exportXmlButton"),
  exportCsvButton: document.getElementById("exportCsvButton"),
  videoPreview: document.getElementById("videoPreview"),
  timeline: document.getElementById("timeline"),
  markerRows: document.getElementById("markerRows"),
  markerCount: document.getElementById("markerCount"),
  markerDetail: document.getElementById("markerDetail"),
  projectSummary: document.getElementById("projectSummary"),
  statusPill: document.getElementById("statusPill"),
};

elements.videoInput.addEventListener("change", handleVideoUpload);
elements.chatInput.addEventListener("change", async (event) => {
  const data = await readDataFile(event.target.files[0]);
  state.chatRows = data.rows;
  state.chatText = data.text;
  state.chatFileName = data.filename;
  updateSummary(elements, state);
});
elements.heatmapInput.addEventListener("change", async (event) => {
  const data = await readDataFile(event.target.files[0]);
  state.heatmapRows = data.rows;
  state.heatmapText = data.text;
  state.heatmapFileName = data.filename;
  updateSummary(elements, state);
});
elements.analyzeButton.addEventListener("click", runAnalysis);
elements.exportCsvButton.addEventListener("click", () => exportMarkersAsCsv(state));
elements.exportXmlButton.addEventListener("click", () => exportMarkersAsXml(state));
elements.videoPreview.addEventListener("loadedmetadata", () => {
  state.duration = Math.floor(elements.videoPreview.duration || 0);
  updateSummary(elements, state);
  renderTimeline(elements, state);
});

async function runAnalysis() {
  elements.analyzeButton.disabled = true;
  elements.statusPill.textContent = "Analyzing";
  const settings = collectAnalysisSettings();

  try {
    const result = await requestBackendAnalysis(state, settings);
    applyBackendResult(state, result, settings);
    elements.statusPill.textContent = "API analyzed";
  } catch (error) {
    console.warn("EditFlow API unavailable. Falling back to browser analysis.", error);
    runLocalAnalysis(state, settings);
    elements.statusPill.textContent = "Local analyzed";
  } finally {
    renderAnalysisResult(elements, state);
    elements.analyzeButton.disabled = false;
  }
}

function collectAnalysisSettings() {
  const maxMarkers = readNumber(elements.maxMarkers, null);
  return {
    fps: DEFAULT_FPS,
    minMessages: readNumber(elements.minMessages, 3),
    minLaughs: readNumber(elements.minLaughs, 2),
    minHeatmapScore: readNumber(elements.minHeatmapScore, 0.75),
    overlapSeconds: readNumber(elements.overlapSeconds, 5),
    peakMergeSeconds: readNumber(elements.peakMergeSeconds, 2),
    maxMarkers: Number.isFinite(maxMarkers) && maxMarkers > 0 ? maxMarkers : null,
    minMarkerGapSeconds: readNumber(elements.minMarkerGapSeconds, 0),
    preRollSeconds: readNumber(elements.preRollSeconds, 0),
    markerDurationSeconds: readNumber(elements.markerDurationSeconds, 1),
  };
}

function readNumber(input, fallback) {
  const value = Number(input.value);
  return Number.isFinite(value) ? value : fallback;
}

function handleVideoUpload(event) {
  const file = event.target.files[0];
  if (!file) {
    return;
  }

  if (state.videoUrl) {
    URL.revokeObjectURL(state.videoUrl);
  }
  state.videoUrl = URL.createObjectURL(file);
  elements.videoPreview.src = state.videoUrl;
  updateSummary(elements, state);
}
