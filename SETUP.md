# Sales Prediction System Setup

This setup guide reflects the current upload-based forecasting application.

## Backend setup

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Backend dependencies include:
- Flask
- Prophet
- XGBoost
- pandas
- holidays
- Groq SDK

Recommended `backend/.env` values:

```env
FLASK_DEBUG=false
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
UPLOAD_TTL_MINUTES=90
MAX_UPLOAD_SESSIONS=25
REQUEST_TIMEOUT=30
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
AI_TIMEOUT=30
```

Start the backend:

```powershell
cd backend
venv\Scripts\python app.py
```

Or on Windows:

```powershell
cd backend
start_server.bat
```

## Frontend setup

```powershell
cd frontend
npm install
npm run dev
```

Optional frontend env var:
- `VITE_API_URL`

Default API base:
- `http://localhost:5000/api`

## Validation steps

Backend smoke test:

```powershell
backend\venv\Scripts\python.exe backend\smoke_test.py
```

Frontend production build:

```powershell
cd frontend
npm run build
```

## Practical notes

- The live app does not require running `backend/model.py`.
- Upload sessions are stored in memory and are cleared on server restart.
- Per-upload XGBoost JSON files can accumulate under `backend/models/`.
- Archived `.pkl` model bundles are retained for offline experimentation, not the live runtime path.
- Always verify your Python version before installation.
