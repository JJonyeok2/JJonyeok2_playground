import { gradeMeta } from "./config.js";
import { buildCsvText, buildPremiereXmlText } from "./exporters.js";

export function detectChatPeaks(rows, minMessages, minLaughs) {
  const grouped = new Map();

  for (const row of rows) {
    const second = Number(row.second);
    const message = String(row.message ?? "").trim();
    if (!Number.isFinite(second) || !message) {
      continue;
    }

    const bucket = Math.floor(second);
    if (!grouped.has(bucket)) {
      grouped.set(bucket, []);
    }
    grouped.get(bucket).push(message);
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

export function detectHeatmapPeaks(rows, minScore) {
  return rows
    .map((row) => ({
      second: Number(row.second),
      score: Number(row.score),
    }))
    .filter((row) => Number.isFinite(row.second) && row.score >= minScore)
    .map((row) => ({
      second: Math.floor(row.second),
      source: "heatmap_peak",
      strength: row.score,
    }));
}

export function buildMarkers(chatPeaks, heatmapPeaks, settings) {
  const usedHeatmap = new Set();
  const markers = [];

  for (const chatPeak of chatPeaks) {
    const match = findNearestPeak(chatPeak, heatmapPeaks, settings.overlapSeconds);
    if (match) {
      usedHeatmap.add(match.second);
      markers.push(
        createMarker(chatPeak.second, "S", ["chat_peak", "heatmap_peak"], (chatPeak.strength + match.strength) / 2, settings),
      );
    } else {
      markers.push(createMarker(chatPeak.second, "A", ["chat_peak"], chatPeak.strength, settings));
    }
  }

  for (const heatmapPeak of heatmapPeaks) {
    if (!usedHeatmap.has(heatmapPeak.second)) {
      markers.push(createMarker(heatmapPeak.second, "B", ["heatmap_peak"], heatmapPeak.strength, settings));
    }
  }

  const merged = mergeNearbyMarkers(markers, settings.peakMergeSeconds);
  const shifted = merged.map((marker) => ({
    ...marker,
    second: Math.max(0, marker.second - settings.preRollSeconds),
  }));

  return enforceMarkerLimits(shifted, settings)
    .sort((left, right) => left.second - right.second)
    .map((marker) => ({
      ...marker,
      confidence: Number(marker.confidence.toFixed(4)),
    }));
}

export function runLocalAnalysis(state, settings) {
  const chatPeaks = detectChatPeaks(state.chatRows, settings.minMessages, settings.minLaughs);
  const heatmapPeaks = detectHeatmapPeaks(state.heatmapRows, settings.minHeatmapScore);

  state.markers = buildMarkers(chatPeaks, heatmapPeaks, settings);
  state.xmlText = buildPremiereXmlText(state.markers, settings.fps);
  state.csvText = buildCsvText(state.markers);
}

function createMarker(second, grade, evidence, confidence, settings) {
  return {
    second,
    peakSecond: second,
    grade,
    evidence,
    confidence,
    durationSeconds: settings.markerDurationSeconds,
    ...gradeMeta[grade],
  };
}

function findNearestPeak(reference, candidates, overlapSeconds) {
  return candidates
    .filter((candidate) => Math.abs(candidate.second - reference.second) <= overlapSeconds)
    .sort((left, right) => Math.abs(left.second - reference.second) - Math.abs(right.second - reference.second))[0];
}

function mergeNearbyMarkers(markers, mergeSeconds) {
  if (mergeSeconds <= 0) {
    return markers.sort(sortBySecondThenGrade);
  }

  const merged = [];
  const sortedMarkers = [...markers].sort(sortBySecondThenGrade);

  for (const marker of sortedMarkers) {
    const previous = merged.at(-1);
    if (!previous || marker.second - previous.second > mergeSeconds) {
      merged.push(marker);
      continue;
    }

    const winner = compareGrade(marker.grade, previous.grade) < 0 ? marker : previous;
    const evidence = Array.from(new Set([...previous.evidence, ...marker.evidence]));
    merged[merged.length - 1] = {
      ...winner,
      second: Math.min(previous.second, marker.second),
      peakSecond: Math.round((previous.peakSecond + marker.peakSecond) / 2),
      evidence,
      confidence: Math.max(previous.confidence, marker.confidence),
    };
  }

  return merged;
}

function enforceMarkerLimits(markers, settings) {
  const byRank = [...markers].sort((left, right) => {
    const gradeDiff = compareGrade(left.grade, right.grade);
    if (gradeDiff !== 0) {
      return gradeDiff;
    }
    return right.confidence - left.confidence;
  });

  const selected = [];
  for (const marker of byRank) {
    const tooClose = selected.some((selectedMarker) => Math.abs(selectedMarker.second - marker.second) < settings.minMarkerGapSeconds);
    if (tooClose) {
      continue;
    }

    selected.push(marker);
    if (settings.maxMarkers && selected.length >= settings.maxMarkers) {
      break;
    }
  }

  return selected;
}

function sortBySecondThenGrade(left, right) {
  return left.second - right.second || compareGrade(left.grade, right.grade);
}

function compareGrade(leftGrade, rightGrade) {
  const rank = { S: 0, A: 1, B: 2 };
  return rank[leftGrade] - rank[rightGrade];
}
