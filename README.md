# EditFlow

EditFlow detects highlight moments from livestream chat and replay heatmap data,
then exports editor-friendly Premiere Pro marker XML and a CSV report.

## Current Features

- Load chat data from CSV or JSON.
- Load replay heatmap data from CSV or JSON.
- Detect chat reaction peaks and heatmap replay peaks.
- Classify markers as S, A, or B based on combined evidence.
- Limit noisy output with max marker count and minimum marker gap settings.
- Export Premiere Pro XML markers with configurable pre-roll and duration.
- Export CSV reports with human-readable timecode.
- Run through CLI, FastAPI, or the static workbench UI.

## Input Formats

Chat CSV:

```csv
second,message
10,ㅋㅋㅋ
10,미쳤다
11,좋다
```

Heatmap CSV:

```csv
second,score
10,0.7
11,0.9
```

JSON files use a list of objects with the same keys:

```json
[
  { "second": 10, "message": "ㅋㅋㅋ" }
]
```

## CLI

Run from this repository without installing:

```bash
PYTHONPATH=src JJonyeok2/bin/python -m editflow.cli analyze \
  --chat examples/chat.csv \
  --heatmap examples/heatmap.csv \
  --out outputs \
  --max-markers 20 \
  --peak-merge-seconds 2 \
  --min-marker-gap-seconds 8 \
  --pre-roll-seconds 2 \
  --marker-duration-seconds 5
```

Outputs:

- `outputs/editflow_markers.xml`
- `outputs/editflow_markers.csv`
- `outputs/editflow_manifest.json`

The package entry point is also configured as `editflow` after installation.

## API

Start the API:

```bash
JJonyeok2/bin/python -m uvicorn editflow.api:api --app-dir src --host 127.0.0.1 --port 8000
```

Analyze uploaded text:

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "chat_text": "second,message\n10,ㅋㅋ\n10,ㅋㅋㅋ\n10,미쳤다\n",
    "chat_filename": "chat.csv",
    "heatmap_text": "second,score\n11,0.9\n",
    "heatmap_filename": "heatmap.csv",
    "fps": 30,
    "max_markers": 20,
    "peak_merge_seconds": 2,
    "min_marker_gap_seconds": 8,
    "pre_roll_seconds": 2,
    "marker_duration_seconds": 5
  }'
```

## Static UI

The current UI is a practical workbench and can be refined later.

```bash
python3 -m http.server 8765 --directory web
```

Open `http://localhost:8765/index.html`.

## Verification

```bash
JJonyeok2/bin/python -m pytest -q
JJonyeok2/bin/python -m ruff check src tests
node --check web/app.js
```
