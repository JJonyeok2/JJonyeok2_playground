export function renderAnalysisResult(elements, state) {
  renderTimeline(elements, state);
  renderMarkerTable(elements, state);
  elements.exportXmlButton.disabled = state.markers.length === 0;
  elements.exportCsvButton.disabled = state.markers.length === 0;
}

export function renderTimeline(elements, state) {
  elements.timeline.innerHTML = "";
  const duration = Math.max(state.duration, ...state.markers.map((marker) => marker.second), 1);

  for (const marker of state.markers) {
    const button = document.createElement("button");
    button.className = `timeline-marker ${marker.className}`;
    button.style.left = `${Math.min(100, (marker.second / duration) * 100)}%`;
    button.title = `${formatTime(marker.second)} ${marker.title}`;
    button.type = "button";
    button.addEventListener("click", () => selectMarker(elements, marker));
    elements.timeline.appendChild(button);
  }
}

export function renderMarkerTable(elements, state) {
  elements.markerCount.textContent = String(state.markers.length);
  elements.markerRows.innerHTML = "";

  if (state.markers.length === 0) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 4;
    cell.className = "empty-state";
    cell.textContent = "No markers yet";
    row.appendChild(cell);
    elements.markerRows.appendChild(row);
    return;
  }

  for (const marker of state.markers) {
    const row = document.createElement("tr");
    appendCell(row, formatTime(marker.second));
    appendCell(row, marker.grade);
    appendCell(row, marker.evidence.join(" + "));
    appendCell(row, `${Math.round(marker.confidence * 100)}%`);
    row.addEventListener("click", () => selectMarker(elements, marker));
    elements.markerRows.appendChild(row);
  }
}

export function selectMarker(elements, marker) {
  if (Number.isFinite(marker.second)) {
    elements.videoPreview.currentTime = marker.second;
  }

  elements.markerDetail.textContent = "";
  const title = document.createElement("h3");
  title.textContent = `${formatTime(marker.second)} · ${marker.title}`;
  const memo = document.createElement("p");
  memo.textContent = marker.memo;
  const evidence = document.createElement("p");
  evidence.textContent = `Evidence: ${marker.evidence.join(" + ")} · Confidence ${Math.round(marker.confidence * 100)}%`;
  elements.markerDetail.append(title, memo, evidence);
}

export function updateSummary(elements, state) {
  const videoName = elements.videoInput.files[0]?.name ?? "no video";
  elements.projectSummary.textContent = `${videoName} · chat ${state.chatRows.length} rows · heatmap ${state.heatmapRows.length} rows`;
}

export function formatTime(totalSeconds) {
  const seconds = Math.max(0, Math.floor(totalSeconds));
  const minutes = Math.floor(seconds / 60);
  const remainder = String(seconds % 60).padStart(2, "0");
  return `${minutes}:${remainder}`;
}

function appendCell(row, text) {
  const cell = document.createElement("td");
  cell.textContent = text;
  row.appendChild(cell);
}
