export async function parseDataFile(file) {
  const data = await readDataFile(file);
  return data.rows;
}

export async function readDataFile(file) {
  if (!file) {
    return { rows: [], text: "", filename: "" };
  }

  const text = await file.text();
  return {
    rows: parseDataText(text, file.name),
    text,
    filename: file.name,
  };
}

export function parseDataText(text, filename) {
  if (filename.toLowerCase().endsWith(".json")) {
    return normalizeJsonRows(JSON.parse(text));
  }
  return parseCsv(text);
}

export function parseCsv(text) {
  const normalizedText = text.trim();
  if (!normalizedText) {
    return [];
  }

  const [headerLine, ...lines] = normalizedText.split(/\r?\n/);
  const headers = parseCsvLine(headerLine).map((header) => header.trim());

  return lines
    .filter(Boolean)
    .map((line) => {
      const values = parseCsvLine(line);
      return headers.reduce((row, header, index) => {
        row[header] = values[index]?.trim() ?? "";
        return row;
      }, {});
    });
}

function parseCsvLine(line) {
  const values = [];
  let current = "";
  let insideQuote = false;

  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    const nextChar = line[index + 1];

    if (char === '"' && insideQuote && nextChar === '"') {
      current += '"';
      index += 1;
      continue;
    }

    if (char === '"') {
      insideQuote = !insideQuote;
      continue;
    }

    if (char === "," && !insideQuote) {
      values.push(current);
      current = "";
      continue;
    }

    current += char;
  }

  values.push(current);
  return values;
}

function normalizeJsonRows(parsed) {
  if (Array.isArray(parsed)) {
    return parsed;
  }

  if (Array.isArray(parsed.rows)) {
    return parsed.rows;
  }

  if (Array.isArray(parsed.items)) {
    return parsed.items;
  }

  if (Array.isArray(parsed.data)) {
    return parsed.data;
  }

  return [];
}
