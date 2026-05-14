# Quick Start

This is the shortest path to run the current upload-based application locally.

## 1. Start the backend

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
venv\Scripts\python app.py
```

Important backend env vars:
- `GROQ_API_KEY` for AI insights
- `GROQ_MODEL` to override the default Groq model
- `UPLOAD_TTL_MINUTES` for in-memory session lifetime
- `MAX_UPLOAD_SESSIONS` for concurrent upload limits

Backend default URL:
- `http://localhost:5000`

## 2. Start the frontend

Open a new terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend default URL:
- `http://localhost:5173`

Optional frontend env var:
- `VITE_API_URL` defaults to `http://localhost:5000/api`

## 3. Upload a sample dataset

After both servers are running:

1. Open `http://localhost:5173`.
2. Choose a market such as `IN` or `US`.
3. Upload a repository sample file like `smart.csv`, `hypermart.csv`, or `supplico.csv`.
4. Run forecast and pattern analysis.
5. Generate AI insights if `GROQ_API_KEY` is configured.

## 4. Run the smoke test

```powershell
backend\venv\Scripts\python.exe backend\smoke_test.py
```

This verifies:
- upload flow
- aggregate forecast flow
- product forecast flow
- runtime metadata endpoints
- holiday coverage beyond 2026

## Notes

- No offline model training is required for the live upload workflow.
- Upload sessions are stored in memory only.
- Per-upload XGBoost model files are saved under `backend/models/`.
- Archived `.pkl` bundles remain in the repo for offline experimentation only.
- Please refer to `SETUP.md` for more detailed configuration options.
