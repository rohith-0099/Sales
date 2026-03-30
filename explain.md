# Sales Prediction System - Source-Verified Project Explanation

This file is the best "what this repo really does" reference for the current codebase.

Use this as the source of truth when older docs conflict with implementation.

Audit status:
- Verified against source code on March 30, 2026.
- Verified against shipped datasets and model artifacts in this repo.
- Verified with backend route checks and a successful frontend production build.

Important corrections up front:
- The active product is the upload-based forecasting and analytics system.
- The legacy BigMart-style prediction flow has been removed from the live UI and backend API.
- AI insights currently use Groq, not Gemini.
- Upload sessions are stored in memory only. There is no database.
- Runtime forecasting uses Prophet plus per-upload XGBoost ensemble models.
- Older `.pkl` bundles in `backend/models/` remain in the repo as offline artifacts, not live runtime dependencies.

## 1. What The Project Does

This is a full-stack retail analytics application that lets a user:

1. Upload a CSV or XLSX retail dataset.
2. Auto-detect date, sales, and product columns.
3. Normalize the dataset into a standard internal structure.
4. Analyze historical sales patterns.
5. Forecast future sales with Prophet, optionally blended with a per-upload XGBoost model.
6. View product-level rankings and drill-down analysis.
7. See holiday and festival impact by market.
8. Ask an AI model to summarize the business situation in multiple languages.
9. Export forecast rows as CSV.

This means the project is not just "a single sales model". It is a retail intelligence dashboard that combines upload parsing, normalization, time-series forecasting, product analysis, holiday-aware context, and AI-generated summaries.

## 2. Main User Journeys

### Upload-driven analytics flow
- User selects a market in the frontend.
- User uploads a CSV or XLSX file.
- Backend normalizes the file, stores it in a temporary upload session, and tries to train a session-specific XGBoost model.
- User runs analysis for all products or one chosen product.
- Frontend requests forecast and pattern analysis in parallel.
- Frontend fetches holiday markers for the chart.
- User can ask for an AI brief and export forecast rows as CSV.

## 3. Architecture

```text
frontend (React + Vite + Tailwind + Recharts)
    -> calls
backend/app.py (Flask API)
    -> uses
analytics_engine.py   # upload parsing, normalization, analysis, Prophet forecast
ensemble_engine.py    # per-upload XGBoost and Prophet+XGB blending
market_holidays.py    # multi-country holiday logic
ai_engine.py          # Groq-powered AI brief generation
    -> reads/writes
backend/models/       # saved model artifacts and per-upload XGB json files
    -> reads
backend/data/         # training/reference datasets
```

There is no database, auth system, queue, or persistent upload storage layer.

## 4. Frontend Stack And Behavior

Main files:
- `frontend/src/App.jsx`
- `frontend/src/components/FileUpload.jsx`
- `frontend/src/components/ForecastChart.jsx`

Libraries:
- React 18
- Axios
- Recharts
- react-dropzone
- Tailwind CSS
- Vite

What the frontend does:
- manages upload state, analysis state, AI state, market selection, product search, and forecast export
- posts uploads to `/api/upload-csv`
- calls `/api/forecast` and `/api/analyze-patterns`
- calls `/api/products/search` with deferred search input
- calls `/api/holidays` to overlay holiday markers on the forecast chart
- calls `/api/ai-insights`

Market support in the UI:
- India (`IN`)
- United States (`US`)
- United Kingdom (`GB`)
- UAE (`AE`)
- Australia (`AU`)
- Canada (`CA`)

The selected market changes:
- currency formatting
- holiday calendar used in backend requests
- upload-time country code for per-session model training

Important frontend nuance:
- forecast horizon buttons are preset labels, but the backend will accept any positive integer period count
- the exported CSV contains forecast rows only, not historical rows

## 5. Backend Entry Point

`backend/app.py` is the main API gateway.

Key responsibilities:
- loads `.env`
- creates the upload session store
- exposes all REST endpoints
- coordinates analytics, ensemble, holiday, and AI logic
- exposes runtime metadata through `/api/health` and `/api/model-info`

Upload session storage:
- in memory only
- default TTL: 90 minutes
- default maximum active sessions: 25
- controlled by `UPLOAD_TTL_MINUTES` and `MAX_UPLOAD_SESSIONS`

Important storage caveat:
- upload sessions expire from memory
- session XGBoost files named like `<upload_id>_aggregate_xgb.json` and `<upload_id>_product_xgb.json` remain on disk unless deleted manually

## 6. API Endpoints

Implemented endpoints in `backend/app.py`:

- `GET /`
  - basic API info and endpoint map

- `GET /api/health`
  - runtime health, active upload sessions, and upload session limits

- `POST /api/upload-csv`
  - file upload, normalization, upload-session creation, session XGBoost training

- `GET /api/products/search`
  - search detected products inside one upload session

- `POST /api/forecast`
  - Prophet forecast, optionally blended with session XGBoost forecast

- `POST /api/analyze-patterns`
  - trend summary, period trends, product leaderboard, holiday impact

- `GET /api/festival-impact`
  - upcoming festivals and impact scores for the next 60 days

- `GET /api/holidays`
  - holiday list between two dates for a market

- `GET /api/model-info`
  - runtime stack description, upload-session limits, and session-model artifact patterns

- `POST /api/ai-insights`
  - short multilingual business brief using Groq

Important API note:
- the older `/api/predict` and `/api/batch-predict` legacy endpoints are no longer part of the active application runtime

## 7. Upload Parsing And Normalization

All upload parsing is handled in `backend/analytics_engine.py`.

Accepted file types:
- `.csv`
- `.xlsx`

The engine normalizes incoming data to at least:
- `date`
- `sales`

If product information exists, it also creates:
- `product_key`
- `product_search_text`

### Date detection
The parser looks for names like:
- `date`
- `order_date`
- `invoice_date`
- `sales_date`
- `transaction_date`
- `ship_date`
- `timestamp`
- `datetime`
- `ds`

If no direct date column exists, it can build dates from:
- `year`
- optional `month`
- optional `day`

### Sales detection
The parser looks for names like:
- `sales`
- `total_sales`
- `sales_value`
- `sales_amount`
- `revenue`
- `turnover`
- `gmv`
- `amount`

Important accuracy note:
- whichever numeric column looks most like sales becomes the internal `sales` series
- the system does not automatically distinguish revenue from units sold
- example: `Sales_Units` can be treated as the forecast target even if it is not currency

### Product detection
The parser searches for:
- product name columns such as `product_name`, `product`, `item_name`, `category`
- product ID columns such as `product_id`, `product_code`, `item_identifier`, `sku`
- product context columns such as `segment`, `product_type`, `product_category`

If both name and ID exist, `product_key` may become a combined label like `Fresh Milk (1L) (PROD-104)`.

### Granularity inference
Granularity is inferred by median date gap:
- `daily`
- `weekly`
- `monthly`
- `yearly`

Frequency profiles are hardcoded:

| Granularity | Prophet freq | Default periods | Forecast unit |
|---|---|---:|---|
| daily | `D` | 30 | days |
| weekly | `W` | 12 | weeks |
| monthly | `MS` | 12 | months |
| yearly | `YS` | 3 | years |

## 8. Historical Analysis Logic

Historical analysis also lives in `analytics_engine.py`.

What it computes:
- total sales
- average sales
- latest sales
- current run rate
- previous run rate
- growth percent
- trend direction
- volatility percent
- start and end date
- period trends
- trend highlights
- festival impact
- top festivals
- product leaderboard
- selected product stats

Important analysis nuances:
- raw rows are aggregated by date before analysis
- daily and weekly data are grouped into month-level rows in the trend table
- top products come from the upload-wide product summary even if a single product is selected
- non-daily uploads get an "approximate" festival impact note

## 9. Forecasting Logic

Base forecasting is implemented with Prophet in `generate_forecast()`.

What Prophet uses:
- frequency profile based on detected granularity
- seasonality toggles from that profile
- interval width `0.85`

Holiday handling:
- the selected market calendar adds holiday-derived features
- Prophet may receive a binary `festival_impact` regressor when the series has meaningful variation around festivals

Forecast response includes:
- `historical_series`
- `forecast`
- `summary`
- `granularity`
- `forecast_periods`
- `forecast_unit`
- `selected_product`

Forecast summary includes:
- average predicted sales
- cumulative predicted sales
- peak forecast sales and date
- projected growth percent
- projected direction
- comparison to current sales window

Negative future values are clipped to zero.

## 10. Prophet + XGBoost Ensemble Logic

Per-upload ensemble logic is implemented in `backend/ensemble_engine.py`.

During upload:
- backend trains scope-aware XGBoost models on aggregated series rather than raw row-level sales
- one aggregate model is trained on total sales summed by date
- one product-scope model is trained on sales summed by product and date when product identifiers exist
- models are saved to:
  - `backend/models/<upload_id>_aggregate_xgb.json`
  - `backend/models/<upload_id>_product_xgb.json`

This fixes the earlier scale mismatch between Prophet and XGBoost.

Engineered session-model features:
- `lag_1`
- `lag_7`
- `lag_30`
- `rolling_mean_7`
- `rolling_mean_30`
- `day_of_week`
- `month`
- `quarter`
- `is_weekend`
- `is_festival`

Weighting logic:

| Row count | Prophet | XGBoost |
|---:|---:|---:|
| < 100 | 0.8 | 0.2 |
| 100-300 | 0.5 | 0.5 |
| > 300 | 0.2 | 0.8 |

Important caveats:
- session-model RMSE and MAE are still fit-time metrics, not dedicated backtesting metrics
- the displayed `High` or `Medium` confidence label is a heuristic based on weight dominance, not a true confidence estimate
- Prophet lower and upper bounds are kept even when point forecasts are blended with XGBoost
- if session training or ensemble prediction fails, the backend falls back to Prophet output

## 11. Holiday And Market Logic

Runtime market logic is in `backend/market_holidays.py`.

The code uses the `holidays` library and maps holiday names into categories such as:
- Diwali
- Holi
- Eid
- Christmas
- New Year
- Durga Puja
- Thanksgiving
- Black Friday
- Independence Day
- Republic Day
- Easter
- Halloween
- Labor Day

Holiday-derived fields can include:
- `is_holiday`
- `holiday_name`
- `festival_category`
- `days_to_festival`
- `nearest_festival`
- `is_pre_festival`
- `is_post_festival`

Current behavior:
- calendars automatically expand to cover requested or forecasted years
- non-holiday rows no longer get forced into the `Other` festival category
- top-festival analysis now uses real holiday labels when a holiday is not mapped to a major category

## 12. AI Insight Logic

AI generation is implemented in `backend/ai_engine.py`.

Provider:
- Groq

Default model:
- `llama-3.3-70b-versatile`

Environment variables:
- `GROQ_API_KEY`
- `GROQ_MODEL`

Supported languages:
- English
- Hindi
- Marathi
- Bengali
- Telugu
- Tamil
- Malayalam

Prompt structure asks for exactly these sections:
- `## Core Problem`
- `## Focus Area`
- `## Future Strategy`
- `## Forecast Signal`

Important AI behavior note:
- if the Groq API key is missing or invalid, the backend returns an unavailable or fallback response in the `insights` field
- there is no full local LLM replacement in the repo

## 13. Offline Training And Archived Model Assets

The active runtime app does not depend on pre-trained `.pkl` bundles for live forecasting. Forecasting is driven by uploaded data plus per-session modeling.

However, the repository still contains older training and experimentation assets:

### `backend/models/integrated_sales_model.pkl`
Purpose:
- archived integrated model bundle produced by the offline training pipeline

Training sources:
- BigMart
- Diwali Sales
- Indian Retail

Important note:
- this artifact is retained in the repo for experimentation and reference
- it is not the live forecast engine behind the current UI workflow

### `backend/models/sales_model.pkl`
Purpose:
- archived model bundle from the older BigMart-style project phase

Important note:
- this artifact is no longer exposed through the live UI or active API endpoints

Important realism note:
- `unified_data_processor.py` assigns synthetic hourly dates to BigMart and Diwali rows so they can be merged with real-dated retail data
- this makes the integrated dataset useful for experimentation, but it is not a naturally aligned real-world time-series source

## 14. Offline Training Pipelines

Important backend scripts:

- `backend/model.py`
  - archived training pipeline from the earlier BigMart-style phase
  - creates feature importance and evaluation plots

- `backend/unified_data_processor.py`
  - merges BigMart, Diwali Sales, and Indian Retail data
  - adds festival and encoded categorical features
  - saves `backend/data/unified_training_data.csv`
  - saves `backend/models/unified_encoders.pkl`

- `backend/train_integrated_model.py`
  - trains the archived integrated XGBoost model on the unified data
  - saves `backend/models/integrated_sales_model.pkl`
  - saves integrated model plots

- `backend/explore_datasets.py`
  - dataset inspection utility

- `backend/verify_setup.py`
  - dependency checker

## 15. Data Assets In The Repo

Training/reference data under `backend/data/`:
- `Train.csv` -> 8,523 rows
- `Test.csv` -> 5,681 rows
- `unified_training_data.csv` -> 22,308 rows on disk
- `diwali_sales/Diwali Sales Data.csv` -> 11,251 rows
- `indian_retail/INDIA_RETAIL_DATA.xlsx` -> 2,534 rows

Sample upload datasets in the repo root:
- `smart.csv` -> 5,110 rows
- `hypermart.csv` -> 5,475 rows
- `supplico.csv` -> 216 rows
- `reliance_yearly.csv` -> 128 rows
- `reliance_smart.csv` -> 43,800 rows

Testing datasets:
- `test_data/synthetic_shop_sales_1_year.csv` -> 1,825 rows
- `test_data/indian_household_1000_products_1yr.csv` -> 218,797 rows

## 16. Known Limitations

- No database or persistent upload session storage.
- Server restart clears upload sessions.
- Per-upload XGBoost files accumulate in `backend/models/`.
- The chosen sales column may represent units, revenue, or another metric depending on naming.
- Weekly data is summarized into monthly period rows for trend reporting.
- Festival impact on non-daily data is approximate.
- AI requires a valid Groq API key.
- Product filtering is exact after normalization, so free text can fail if it does not match a real `product_key`.
- Confidence labels in the ensemble output are heuristic labels, not formal uncertainty guarantees.

## 17. Most Important Files To Read

If someone wants to understand the repo quickly, the highest-value files are:

1. `backend/app.py`
2. `backend/analytics_engine.py`
3. `backend/ensemble_engine.py`
4. `backend/market_holidays.py`
5. `backend/ai_engine.py`
6. `frontend/src/App.jsx`
7. `backend/unified_data_processor.py`
8. `backend/train_integrated_model.py`

## 18. Verification Performed For This Document

During this audit, the following were verified:
- route definitions in `backend/app.py`
- upload parsing, analysis, and forecasting code
- AI provider and prompt logic
- dataset shapes in the repo
- daily upload flow
- monthly upload flow
- `/api/health`
- `/api/model-info`
- `/api/upload-csv`
- `/api/forecast`
- `/api/analyze-patterns`
- `/api/holidays`
- `/api/festival-impact`
- `/api/ai-insights`
- frontend build with `npm run build`

Concrete verified runtime facts:
- daily sample upload returned `granularity = daily`
- monthly sample upload returned `granularity = monthly`
- monthly sample defaulted to `12` forecast periods and `months` as forecast unit
- backend health reports the upload-based forecasting stack
- smoke tests cover aggregate forecast flow, product forecast flow, runtime metadata endpoints, and holiday coverage beyond 2026

## 19. Bottom Line

This repo is a retail intelligence platform centered on an upload-based analytics dashboard that normalizes retail data, analyzes trends, forecasts future sales, adds holiday context, supports product drill-down, and generates multilingual AI briefs.

The core modern stack is:
- React frontend
- Flask backend
- pandas for normalization
- Prophet for time-series forecasting
- per-upload XGBoost for ensemble enhancement
- holidays-based market calendars
- Groq for short business insights

If another AI system needs to answer questions about this repository accurately, this file is the right document to provide.

## 20. Detailed Repository Inventory

This section explains what is present in the project folder beyond just the main application code.

### Top-level files and folders

- `.gitignore`
  - standard ignore rules for Python, Node, build output, local env files, and image outputs

- `README.md`
  - high-level project overview
  - partly outdated relative to the current code

- `QUICKSTART.md`
  - older quickstart material
  - not the best source of truth for the current implementation

- `SETUP.md`
  - older setup instructions
  - useful, but partially outdated

- `explain.md`
  - this source-verified explanation document

- `setup.bat`
  - Windows helper for creating backend venv and installing a base dependency set

- `generate_massive_data.py`
  - synthetic dataset generator for large retail upload testing

- `smart.csv`
  - sample retail file for upload testing
  - parser typically treats `Sales_Units` as the target metric

- `hypermart.csv`
  - sample upload file using a revenue-oriented schema

- `supplico.csv`
  - sample monthly upload file

- `reliance_yearly.csv`
  - sample yearly upload file

- `reliance_smart.csv`
  - larger daily sample upload file

- `India Retail Shop Sales Data 2025-2026.xlsx`
  - raw reference dataset in the repo root
  - not part of the runtime upload flow by default

- `test_data/`
  - contains cleaner sample upload datasets for controlled testing

- `models/`
  - top-level folder exists but is currently empty
  - runtime model files are stored in `backend/models`, not here

- `visualizations/`
  - top-level folder exists but is currently empty
  - generated backend training plots are stored in `backend/visualizations`

### Backend folder inventory

- `backend/app.py`
  - Flask API entrypoint and integration layer

- `backend/analytics_engine.py`
  - normalization, column detection, product handling, analysis, Prophet forecast logic

- `backend/ensemble_engine.py`
  - per-upload XGBoost training and blending logic

- `backend/market_holidays.py`
  - runtime multi-country holiday calendar

- `backend/indian_holidays.py`
  - India-specific holiday utility mainly used by offline scripts

- `backend/ai_engine.py`
  - Groq prompt construction and AI brief request execution

- `backend/model.py`
  - archived training pipeline from the earlier BigMart-style phase

- `backend/unified_data_processor.py`
  - integrated data preparation script

- `backend/train_integrated_model.py`
  - archived integrated XGBoost model training script

- `backend/explore_datasets.py`
  - dataset inspection utility

- `backend/verify_setup.py`
  - dependency/import verification script

- `backend/smoke_test.py`
  - lightweight automated smoke test for upload, forecast, runtime metadata, and holiday coverage

- `backend/start_server.bat`
  - Windows helper to start Flask after activating the backend venv

- `backend/.env`
  - backend runtime configuration

- `backend/requirements.txt`
  - main backend dependency list

- `backend/venv/`
  - local Python virtual environment already present in this repository workspace

- `backend/__pycache__/`
  - generated Python cache files, not source

### Backend data inventory

- `backend/data/Train.csv`
  - archived BigMart training dataset

- `backend/data/Test.csv`
  - archived BigMart test dataset without target

- `backend/data/unified_training_data.csv`
  - merged training dataset used by the archived integrated model workflow

- `backend/data/dataset_summary.txt`
  - summary generated by `explore_datasets.py`

- `backend/data/README.md`
  - notes about the Kaggle datasets and intended integration approach

- `backend/data/diwali_sales/Diwali Sales Data.csv`
  - Diwali shopping dataset used by unified processing

- `backend/data/indian_retail/INDIA_RETAIL_DATA.xlsx`
  - Indian retail dataset with temporal and regional fields

- `backend/data/holidays/INDIA_RETAIL_DATA.xlsx`
  - duplicate or reused file under the holidays folder
  - not a distinct runtime holiday engine source

- `backend/data/archive.zip`
- `backend/data/Diwali Sales.zip`
- `backend/data/Holidays dataset.zip`
- `backend/data/indian retail.zip`
  - raw archive/source files kept in the repo for provenance and manual reuse
  - not directly used by the live API during normal runtime

### Backend model inventory

- `backend/models/integrated_sales_model.pkl`
  - archived integrated model bundle

- `backend/models/sales_model.pkl`
  - archived model bundle from the earlier project phase

- `backend/models/unified_encoders.pkl`
  - label encoders created during unified data processing

- `backend/models/*_aggregate_xgb.json`
  - per-upload aggregate-scope XGBoost model files

- `backend/models/*_product_xgb.json`
  - per-upload product-scope XGBoost model files
  - created dynamically when uploads are processed

### Backend visualization inventory

Generated PNG plots under `backend/visualizations/` include:
- `actual_vs_predicted.png`
- `feature_importance.png`
- `item_weight_dist.png`
- `item_mrp_dist.png`
- `sales_dist.png`
- `establishment_year.png`
- `fat_content_before.png`
- `fat_content_after.png`
- `integrated_feature_importance.png`
- `integrated_actual_vs_predicted.png`

These are offline training outputs, not files rendered live by the frontend.

### Frontend folder inventory

- `frontend/package.json`
  - frontend dependencies and scripts

- `frontend/package-lock.json`
  - exact npm dependency lockfile

- `frontend/vite.config.js`
  - Vite config with manual chunk splitting for build optimization

- `frontend/tailwind.config.js`
  - Tailwind scan paths and extended theme values

- `frontend/postcss.config.js`
  - PostCSS config for Tailwind and Autoprefixer

- `frontend/eslint.config.js`
  - ESLint config for React code

- `frontend/eslint.txt`
  - saved lint output artifact
  - not runtime logic

- `frontend/index.html`
  - root HTML shell
  - imports Inter from Google Fonts

- `frontend/README.md`
  - default Vite/React template README, not project-specific documentation

- `frontend/update_frontend.py`
  - one-off maintenance/refactor script used previously to alter frontend files
  - not part of runtime

- `frontend/public/vite.svg`
  - static Vite asset

- `frontend/src/main.jsx`
  - React app bootstrapping

- `frontend/src/App.jsx`
  - main dashboard component

- `frontend/src/App.css`
  - Tailwind directives plus some global styling utilities

- `frontend/src/index.css`
  - minimal root styling file

- `frontend/src/components/FileUpload.jsx`
  - drag-and-drop upload UI

- `frontend/src/components/ForecastChart.jsx`
  - Recharts-based forecast visualization component

- `frontend/src/assets/react.svg`
  - static asset from template scaffolding

- `frontend/dist/`
  - generated production build output

- `frontend/node_modules/`
  - installed frontend dependencies

## 21. Technologies And Tools Used

This section groups the tools by role so the project can be described clearly in a detailed report.

### Programming languages
- Python
- JavaScript
- HTML
- CSS
- Batch scripting (`.bat`)

### Backend frameworks and libraries
- Flask
- flask-cors
- pandas
- numpy
- Prophet
- XGBoost
- scikit-learn
- holidays
- python-dotenv
- openpyxl
- Groq SDK

### Frontend frameworks and libraries
- React
- Vite
- Axios
- Recharts
- react-dropzone
- Tailwind CSS
- PostCSS
- Autoprefixer

### Model training and visualization tools
- matplotlib
- seaborn

### Development and quality tools
- ESLint
- npm
- Python virtual environment

### Data and file formats used
- CSV
- XLSX
- PKL
- JSON
- PNG
- ZIP

## 22. API Payload And Output Reference

These are the important request shapes used by the app.

### Upload request

Endpoint:
- `POST /api/upload-csv`

Form fields:
- `file`
- optional `country_code`

Typical output:
- `success`
- `upload_id`
- `file_name`
- `stats`
- `preview`
- `columns`
- `granularity`
- `product_column`
- `product_primary_column`
- `product_lookup_columns`
- `sample_products`

### Forecast request

Endpoint:
- `POST /api/forecast`

Typical payload:

```json
{
  "upload_id": "session_id_here",
  "selected_product": "optional product key",
  "country_code": "IN",
  "forecast_periods": 30
}
```

Alternative mode:
- instead of `upload_id`, the backend also supports direct `historical_data` in JSON
- the current frontend does not use that path

Typical output:
- `historical_series`
- `forecast`
- `summary`
- `granularity`
- `forecast_periods`
- `forecast_unit`
- optional `confidence`
- optional `ensemble_weights`
- optional `metrics`

### Pattern analysis request

Endpoint:
- `POST /api/analyze-patterns`

Typical payload:

```json
{
  "upload_id": "session_id_here",
  "selected_product": "optional product key",
  "country_code": "IN"
}
```

Typical output:
- `summary`
- `period_trends`
- `trend_highlights`
- `festival_impact`
- `top_festivals`
- `top_products`
- `selected_product_stats`
- `selected_product`

### Product search request

Endpoint:
- `GET /api/products/search`

Query params:
- `upload_id`
- `q`
- `limit`

Typical output:
- list of product matches with `value`, `total_sales`, `records`, and `rank`

### AI insight request

Endpoint:
- `POST /api/ai-insights`

Typical payload includes:
- `upload_id`
- `language`
- `product_name`
- `summary`
- `total_sales`
- `trend`
- `growth_rate`
- `festival`
- `granularity`
- `market`
- `country_code`
- `context`

Typical output:
- `success`
- `insights`
- `model`

### Runtime metadata request

Endpoint:
- `GET /api/model-info`

Typical output:
- `success`
- `runtime_mode`
- `forecast_engine`
- `upload_sessions`
- `session_model_artifacts`
- `festival_support`

## 23. Setup, Run, And Rebuild Guide

This section explains how the project is actually run from the repo.

### Backend setup

From the project root:

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Required backend env file:
- `backend/.env`

Observed variables:
- `UPLOAD_TTL_MINUTES`
- `MAX_UPLOAD_SESSIONS`
- `GROQ_API_KEY`
- `GROQ_MODEL`

### Start backend

```powershell
cd backend
venv\Scripts\python app.py
```

Or on Windows:

```powershell
cd backend
start_server.bat
```

### Frontend setup

```powershell
cd frontend
npm install
npm run dev
```

Optional frontend env variable:
- `VITE_API_URL`

Default API base in code:
- `http://localhost:5000/api`

### Production frontend build

```powershell
cd frontend
npm run build
```

This creates:
- `frontend/dist/`

### Smoke test run

```powershell
backend\venv\Scripts\python.exe backend\smoke_test.py
```

This verifies:
- upload flow
- aggregate forecast flow
- product forecast flow
- runtime metadata endpoints
- holiday coverage beyond 2026

### Offline retraining workflow

If someone wants to rebuild the integrated pipeline from source datasets:

```powershell
cd backend
venv\Scripts\python unified_data_processor.py
venv\Scripts\python train_integrated_model.py
```

If someone wants to rebuild the older archived BigMart model:

```powershell
cd backend
venv\Scripts\python model.py
```

### Practical runtime note

The live app can run without those archived `.pkl` bundles because the active forecast system is based on uploaded history plus per-session modeling.

## 24. Use Cases And Report-Ready Scenarios

The following scenarios explain how the project would be described in a detailed report.

### Use case 1: General retail trend analysis
A store owner uploads historical sales data and wants to know whether sales are rising, falling, or stable over time.

System value:
- automatic parsing
- KPI summary
- trend classification
- period-by-period breakdown

### Use case 2: Product-level focus
A retailer wants to know which product contributes the most to sales and whether one selected product should be stocked more aggressively.

System value:
- product detection
- searchable product list
- top product leaderboard
- selected product rank, share, and forecast

### Use case 3: Festival-aware planning
A retailer operating in India, the US, or another supported market wants to know how holidays may affect upcoming performance.

System value:
- market-specific holiday detection
- holiday markers on forecast charts
- festival uplift metrics
- holiday category summaries

### Use case 4: Management briefing
A business user wants a short summary to present to non-technical stakeholders.

System value:
- AI-generated brief
- simple language
- multilingual support
- action-oriented output

## 25. Repo Drift, Archived Pieces, And Notes For Report Writing

These are important if this file will be passed into another AI to generate formal reports.

- `README.md`, `QUICKSTART.md`, and `SETUP.md` contain useful information but do not fully reflect the latest implementation.
- `frontend/README.md` is the default Vite template README and should not be treated as project documentation.
- `frontend/eslint.txt` is a saved lint output artifact, not an active configuration source.
- `frontend/update_frontend.py` is a helper maintenance script, not part of normal runtime behavior.
- `top-level models/` and `top-level visualizations/` are empty and are not the runtime storage locations.
- the real runtime model directory is `backend/models/`
- the real generated training plot directory is `backend/visualizations/`
- the current codebase mixes production-style runtime code with experimentation/training scripts and retained raw data archives
- the integrated dataset includes synthetic dates for some source datasets, so it should be described honestly as an engineered training dataset rather than a purely natural operational history
- older BigMart-related files remain in the repository as archived assets, but they are not part of the live upload-based application flow

## 26. Final Guidance For Using This File As Report Input

If this file is used as the knowledge base for generating a project report, the most accurate framing is:

- this is a retail sales forecasting and analytics platform
- it combines historical analysis, time-series forecasting, per-upload machine learning, holiday-aware context, and AI-generated business summaries
- it is a full-stack project with a React frontend and Flask backend
- it uses a mixture of production-style runtime services and offline model/data preparation scripts
- the active application is the upload-driven forecasting dashboard
- older serialized model bundles in the repo should be described as archived or offline artifacts, not as the live runtime engine

For report writing, the safest assumption is:
- treat the upload-driven forecasting dashboard as the main product
- treat `explain.md` as the primary source of truth over older markdown docs
