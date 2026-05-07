# Frontend Notes

This frontend is a React + Vite dashboard for the upload-based sales forecasting workflow.

## Main responsibilities

- market selection
- file upload
- forecast requests
- pattern analysis requests
- product search
- holiday overlay rendering
- AI insight requests
- forecast CSV export

## Key files

- `src/App.jsx`
- `src/components/FileUpload.jsx`
- `src/components/ForecastChart.jsx`

## Local commands

```powershell
npm install
npm run dev
npm run build
npm run lint
```

## Environment

- `VITE_API_URL` defaults to `http://localhost:5000/api`

## Notes

- The frontend talks to the Flask backend over REST.
- The current UI supports India, United States, United Kingdom, UAE, Australia, and Canada.
- Product search and AI insight flows depend on a successful upload session from the backend.
