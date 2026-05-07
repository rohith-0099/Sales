# Sales Prediction & Retail Intelligence System

This repository contains the current upload-driven retail analytics application. Users upload a CSV or XLSX dataset, the backend normalizes it into a shared structure, analyzes historical patterns, forecasts future sales with Prophet plus optional per-upload XGBoost blending, overlays market holidays, and generates short Groq-powered business summaries.

`explain.md` is the best source of truth when older markdown files disagree with the implementation.

## Core Features

### 1. Upload-based normalization
- Supports `.csv` and `.xlsx` retail datasets.
- Auto-detects date, sales, and product columns.
- Infers upload granularity as daily, weekly, monthly, or yearly.

### 2. Forecasting and analysis
- Uses Prophet for the main time-series forecast.
- Can blend in per-upload XGBoost models trained during the upload flow.
- Returns summary metrics, trend highlights, and forecast intervals.

### 3. Product drill-down
- Supports search within an upload session.
- Builds normalized product keys when item identifiers are available.
- Shows leaderboard and selected-product analysis from the same uploaded dataset.

### 4. Market-aware context
- Supports India, United States, United Kingdom, UAE, Australia, and Canada.
- Adds market-specific holiday markers and festival summaries.
- Adjusts frontend currency display based on the selected market.

### 5. AI summaries
- Uses Groq, not Gemini, for AI-generated business briefs.
- Supports English, Hindi, Marathi, Bengali, Telugu, Tamil, and Malayalam.
- Returns a fallback message when `GROQ_API_KEY` is missing or invalid.

## Architecture

```text
frontend (React + Vite + Tailwind + Recharts)
    -> calls
backend/app.py (Flask API)
    -> uses
analytics_engine.py   # upload parsing, normalization, analysis, Prophet forecast
ensemble_engine.py    # per-upload XGBoost and Prophet+XGBoost blending
market_holidays.py    # multi-country holiday logic
ai_engine.py          # Groq-powered AI brief generation
```

There is no database, queue, auth layer, or persistent upload session store in the current app.

## Quick Start

### Backend

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
venv\Scripts\python app.py
```

Set these values in `backend/.env` as needed:
- `GROQ_API_KEY`
- `GROQ_MODEL`
- `UPLOAD_TTL_MINUTES`
- `MAX_UPLOAD_SESSIONS`

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Optional frontend env var:
- `VITE_API_URL` defaults to `http://localhost:5000/api`

## Usage Workflow

1. Select a market in the frontend.
2. Upload a CSV or XLSX retail dataset.
3. Run forecast and pattern analysis for all products or one selected item.
4. Inspect product search results, trend summaries, and holiday overlays.
5. Generate an AI brief and export forecast rows if needed.

## Runtime Notes

- Upload sessions are stored in memory only and expire automatically.
- Per-upload XGBoost JSON artifacts are written under `backend/models/`.
- Older `.pkl` bundles in `backend/models/` are archived offline artifacts, not live runtime dependencies.
- Sample upload files such as `smart.csv`, `hypermart.csv`, and `supplico.csv` are included in the repository root.

## Validation

```powershell
backend\venv\Scripts\python.exe backend\smoke_test.py
cd frontend
npm run build
```

## Related Docs

- `explain.md` for the audited repository explanation
- `QUICKSTART.md` for the shortest local run path
- `SETUP.md` for more detailed environment notes
- `backend/README.md` for backend module documentation
