import { DEFAULT_FPS } from "./config.js";
import { formatTime } from "./render.js";

export function exportMarkersAsCsv(state) {
  downloadText("editflow_markers.csv", state.csvText || buildCsvText(state.markers));
}

export function buildCsvText(markers) {
  const rows = [
    ["second", "timecode", "grade", "title", "evidence", "confidence"],
    ...markers.map((marker) => [
      marker.second,
      formatTime(marker.second),
      marker.grade,
      marker.title,
      marker.evidence.join("+"),
      marker.confidence,
    ]),
  ];
  return rows.map((row) => row.map(escapeCsvValue).join(",")).join("\n");
}

export function exportMarkersAsXml(state) {
  downloadText("editflow_premiere_markers.xml", state.xmlText || buildPremiereXmlText(state.markers));
}

export function buildPremiereXmlText(markerRows, fps = DEFAULT_FPS) {
  const markers = markerRows
    .map((marker) => {
      const inFrame = Math.round(marker.second * fps);
      const durationFrames = Math.max(1, Math.round((marker.durationSeconds ?? 1) * fps));
      return `
      <marker>
        <name>[${escapeXml(marker.color.toUpperCase())}] ${escapeXml(marker.title)}</name>
        <comment>${escapeXml(marker.memo)}</comment>
        <in>${inFrame}</in>
        <out>${inFrame + durationFrames}</out>
      </marker>`;
    })
    .join("");

  return `<?xml version="1.0" encoding="UTF-8"?>
<xmeml version="5">
  <sequence id="editflow-premiere-sequence">
    <name>EditFlow Premiere Pro Markers</name>${markers}
  </sequence>
</xmeml>`;
}

function escapeXml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function escapeCsvValue(value) {
  const text = String(value);
  if (!/[",\n]/.test(text)) {
    return text;
  }
  return `"${text.replaceAll('"', '""')}"`;
}

function downloadText(filename, text) {
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  URL.revokeObjectURL(link.href);
}
