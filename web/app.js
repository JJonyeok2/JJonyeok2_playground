const state = {
  videoUrl: "",
  chatRows: [],
  heatmapRows: [],
  markers: [],
  duration: 0,
};

const gradeMeta = {
  S: {
    color: "purple",
    className: "grade-s",
    title: "S급 하이라이트",
    memo: "Premiere Pro 타임라인에서 우선 검수할 핵심 구간입니다.",
  },
  A: {
    color: "red",
    className: "grade-a",
    title: "A급 채팅 피크",
    memo: "채팅 반응이 강한 구간입니다.",
  },
  B: {
    color: "yellow",
    className: "grade-b",
    title: "B급 히트맵 피크",
    memo: "반복 시청이 집중된 구간입니다.",
  },
};

const elements = {
  videoInput: document.getElementById("videoInput"),
  chatInput: document.getElementById("chatInput"),
  heatmapInput: document.getElementById("heatmapInput"),
  minMessages: document.getElementById("minMessages"),
  minLaughs: document.getElementById("minLaughs"),
  minHeatmapScore: document.getElementById("minHeatmapScore"),
  overlapSeconds: document.getElementById("overlapSeconds"),
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
  state.chatRows = await parseDataFile(event.target.files[0]);
  updateSummary();
});
elements.heatmapInput.addEventListener("change", async (event) => {
  state.heatmapRows = await parseDataFile(event.target.files[0]);
  updateSummary();
});
elements.analyzeButton.addEventListener("click", runAnalysis);
elements.exportCsvButton.addEventListener("click", exportMarkersAsCsv);
elements.exportXmlButton.addEventListener("click", exportMarkersAsXml);
elements.videoPreview.addEventListener("loadedmetadata", () => {
  state.duration = Math.floor(elements.videoPreview.duration || 0);
  updateSummary();
  renderTimeline();
});

async function parseDataFile(file) {
  if (!file) {
    return [];
  }
  const text = await file.text();
  if (file.name.toLowerCase().endsWith(".json")) {
    return JSON.parse(text);
  }
  return parseCsv(text);
}

function parseCsv(text) {
  const [headerLine, ...lines] = text.trim().split(/\r?\n/);
  const headers = headerLine.split(",").map((header) => header.trim());
  return lines
    .filter(Boolean)
    .map((line) => {
      const values = line.split(",");
      return headers.reduce((row, header, index) => {
        row[header] = values[index]?.trim() ?? "";
        return row;
      }, {});
    });
}

function detectChatPeaks(rows, minMessages, minLaughs) {
  const grouped = new Map();
  for (const row of rows) {
    const second = Number(row.second);
    const message = String(row.message ?? "").trim();
    if (!Number.isFinite(second) || !message) {
      continue;
    }
    if (!grouped.has(second)) {
      grouped.set(second, []);
    }
    grouped.get(second).push(message);
  }

  const maxCount = Math.max(1, ...Array.from(grouped.values()).map((messages) => messages.length));
  return Array.from(grouped.entries())
    .filter(([, messages]) => {
      const laughCount = messages.filter((message) => message.includes("ㅋ")).length;
      return messages.length >= minMessages || laughCount >= minLaughs;
    })
    .map(([second, messages]) => ({
      second,
      source: "chat_peak",
      strength: Number((messages.length / maxCount).toFixed(4)),
    }));
}

function detectHeatmapPeaks(rows, minScore) {
  return rows
    .map((row) => ({
      second: Number(row.second),
      score: Number(row.score),
    }))
    .filter((row) => Number.isFinite(row.second) && row.score >= minScore)
    .map((row) => ({
      second: row.second,
      source: "heatmap_peak",
      strength: row.score,
    }));
}

function buildMarkers(chatPeaks, heatmapPeaks, overlapSeconds) {
  const usedHeatmap = new Set();
  const markers = [];

  for (const chatPeak of chatPeaks) {
    const match = findNearestPeak(chatPeak, heatmapPeaks, overlapSeconds);
    if (match) {
      usedHeatmap.add(match.second);
      markers.push(createMarker(chatPeak.second, "S", ["chat_peak", "heatmap_peak"], (chatPeak.strength + match.strength) / 2));
    } else {
      markers.push(createMarker(chatPeak.second, "A", ["chat_peak"], chatPeak.strength));
    }
  }

  for (const heatmapPeak of heatmapPeaks) {
    if (!usedHeatmap.has(heatmapPeak.second)) {
      markers.push(createMarker(heatmapPeak.second, "B", ["heatmap_peak"], heatmapPeak.strength));
    }
  }

  return markers.sort((left, right) => left.second - right.second);
}

function createMarker(second, grade, evidence, confidence) {
  return {
    second,
    grade,
    evidence,
    confidence: Number(confidence.toFixed(4)),
    ...gradeMeta[grade],
  };
}

function findNearestPeak(reference, candidates, overlapSeconds) {
  return candidates
    .filter((candidate) => Math.abs(candidate.second - reference.second) <= overlapSeconds)
    .sort((left, right) => Math.abs(left.second - reference.second) - Math.abs(right.second - reference.second))[0];
}

function runAnalysis() {
  const chatPeaks = detectChatPeaks(
    state.chatRows,
    Number(elements.minMessages.value),
    Number(elements.minLaughs.value),
  );
  const heatmapPeaks = detectHeatmapPeaks(
    state.heatmapRows,
    Number(elements.minHeatmapScore.value),
  );

  state.markers = buildMarkers(chatPeaks, heatmapPeaks, Number(elements.overlapSeconds.value));
  renderTimeline();
  renderMarkerTable();
  elements.exportXmlButton.disabled = state.markers.length === 0;
  elements.exportCsvButton.disabled = state.markers.length === 0;
  elements.statusPill.textContent = "Analyzed";
}

function renderTimeline() {
  elements.timeline.innerHTML = "";
  const duration = Math.max(state.duration, ...state.markers.map((marker) => marker.second), 1);

  for (const marker of state.markers) {
    const button = document.createElement("button");
    button.className = `timeline-marker ${marker.className}`;
    button.style.left = `${Math.min(100, (marker.second / duration) * 100)}%`;
    button.title = `${formatTime(marker.second)} ${marker.title}`;
    button.addEventListener("click", () => selectMarker(marker));
    elements.timeline.appendChild(button);
  }
}

function renderMarkerTable() {
  elements.markerCount.textContent = String(state.markers.length);
  elements.markerRows.innerHTML = "";

  if (state.markers.length === 0) {
    elements.markerRows.innerHTML = '<tr><td colspan="4" class="empty-state">No markers yet</td></tr>';
    return;
  }

  for (const marker of state.markers) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${formatTime(marker.second)}</td>
      <td>${marker.grade}</td>
      <td>${marker.evidence.join(" + ")}</td>
      <td>${Math.round(marker.confidence * 100)}%</td>
    `;
    row.addEventListener("click", () => selectMarker(marker));
    elements.markerRows.appendChild(row);
  }
}

function selectMarker(marker) {
  if (Number.isFinite(marker.second)) {
    elements.videoPreview.currentTime = marker.second;
  }
  elements.markerDetail.innerHTML = `
    <h3>${formatTime(marker.second)} · ${marker.title}</h3>
    <p>${marker.memo}</p>
    <p>Evidence: ${marker.evidence.join(" + ")} · Confidence ${Math.round(marker.confidence * 100)}%</p>
  `;
}

function exportMarkersAsCsv() {
  const rows = [
    ["second", "timecode", "grade", "title", "evidence", "confidence"],
    ...state.markers.map((marker) => [
      marker.second,
      formatTime(marker.second),
      marker.grade,
      marker.title,
      marker.evidence.join("+"),
      marker.confidence,
    ]),
  ];
  downloadText("editflow_markers.csv", rows.map((row) => row.join(",")).join("\n"));
}

function exportMarkersAsXml() {
  const markers = state.markers
    .map((marker) => `
      <marker>
        <name>${escapeXml(marker.title)}</name>
        <comment>${escapeXml(marker.memo)}</comment>
        <in>${Math.round(marker.second * 30)}</in>
        <out>${Math.round(marker.second * 30) + 1}</out>
      </marker>`)
    .join("");

  downloadText(
    "editflow_premiere_markers.xml",
    `<?xml version="1.0" encoding="UTF-8"?>
<xmeml version="5">
  <sequence id="editflow-premiere-sequence">
    <name>EditFlow Premiere Pro Markers</name>${markers}
  </sequence>
</xmeml>`,
  );
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
  updateSummary();
}

function updateSummary() {
  const videoName = elements.videoInput.files[0]?.name ?? "no video";
  elements.projectSummary.textContent = `${videoName} · chat ${state.chatRows.length} rows · heatmap ${state.heatmapRows.length} rows`;
}

function formatTime(totalSeconds) {
  const seconds = Math.max(0, Math.floor(totalSeconds));
  const minutes = Math.floor(seconds / 60);
  const remainder = String(seconds % 60).padStart(2, "0");
  return `${minutes}:${remainder}`;
}

function escapeXml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function downloadText(filename, text) {
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  URL.revokeObjectURL(link.href);
}
