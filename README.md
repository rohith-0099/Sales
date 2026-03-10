# Indian Retail Sales Forecaster and AI Analyst

This project is a retail analytics system for store owners and analysts who want to upload historical sales data and turn it into actionable business insights. The application analyzes past sales, estimates near-term future sales, highlights trends and patterns, and lets users drill down into individual products by name or unique ID. It also includes multilingual AI explanations powered by Google Gemini to explain what is happening in the data, which products deserve more focus, and how sales can be improved.

## Core Capabilities

- Upload historical retail sales data in CSV format.
- Analyze current sales health from uploaded data.
- Generate future sales forecasts for the next 30 days.
- Show patterns such as monthly trends and festival impact.
- Detect product identifiers in the uploaded file and filter analysis by product.
- Use Gemini AI to generate multilingual business recommendations.
- Run a separate manual single-item sales prediction flow with the trained model.

## What the System Analyzes

After you upload a file with `date` and `sales` columns, the system can:

- summarize the uploaded data
- forecast upcoming sales
- show trend and pattern information
- compare normal days with festival periods
- identify top-performing festivals
- let you search for a product and view its specific forecast
- generate AI-based explanations and strategy suggestions

Supported product lookup columns include:

- `product_code`
- `product_id`
- `item_identifier`
- `product`
- `item`
- `product_name`

## Example Use Case

A retail store uploads daily, monthly, or yearly sales data. The system reads the historical records, shows the current performance pattern, predicts future sales, and allows the user to search for a specific product to inspect its sales behavior separately. Gemini AI then explains the trend in the selected language and suggests which products need more attention and what actions may help improve revenue.

## Tech Stack

- Frontend: React, Vite, Tailwind CSS, Recharts
- Backend: Flask, Pandas, Prophet, scikit-learn
- ML model: XGBoost-based sales prediction pipeline
- AI assistant: Google Gemini
- Domain logic: Indian festival calendar and holiday-aware analysis

## Quick Start

You need two terminals: one for the backend and one for the frontend.

### 1. Start the backend

```powershell
cd c:\Users\rohit\Desktop\sales-prediction-system\backend
venv\Scripts\python.exe app.py
```

The backend is ready when it shows:

```text
Running on http://127.0.0.1:5000
```

### 2. Start the frontend

```powershell
cd c:\Users\rohit\Desktop\sales-prediction-system\frontend
npm run dev
```

The frontend is ready when it shows a local URL such as:

```text
http://localhost:5173/
```

### 3. Open the app

Visit:

```text
http://localhost:5173
```

## Expected Input Format

Minimum required columns:

```csv
date,sales
2025-01-01,2500
2025-01-02,2700
```

Optional product-level analysis:

```csv
date,sales,product_id,product_name
2025-01-01,2500,P101,Milk
2025-01-02,1800,P102,Bread
```

Notes:

- `date` must be a valid date column.
- `sales` must be numeric.
- Product filtering is enabled only if one supported product column is present.
- The current forecast flow produces a 30-day future forecast.

## Workflow

1. Upload a sales CSV file.
2. Optionally choose a product before analysis.
3. Run analysis to generate forecasts and pattern insights.
4. Review the forecast chart and festival-based sales impact.
5. Search for a specific product to inspect its individual behavior.
6. Request Gemini AI insights in English, Hindi, Marathi, Bengali, Telugu, or Tamil.

## AI Insights

The AI insights feature uses Google Gemini to generate:

- current sales health commentary
- future outlook based on forecasted data
- product focus suggestions
- practical sales improvement strategies

To enable it, create `backend/.env` with:

```env
GOOGLE_API_KEY=your_api_key_here
```

## API Endpoints

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/api/predict` | POST | Manual single-item sales prediction |
| `/api/upload-csv` | POST | Upload and inspect historical CSV data |
| `/api/forecast` | POST | Generate forecast from historical sales |
| `/api/analyze-patterns` | POST | Analyze monthly trends and festival effects |
| `/api/festival-impact` | GET | View upcoming festivals and expected impact |
| `/api/model-info` | GET | Show loaded model information |
| `/api/health` | GET | Check backend health |
| `/api/ai-insights` | POST | Generate multilingual Gemini analysis |

## Project Structure

```text
sales-prediction-system/
|-- backend/
|   |-- app.py
|   |-- requirements.txt
|   |-- train_integrated_model.py
|   |-- unified_data_processor.py
|   |-- indian_holidays.py
|   |-- data/
|   `-- visualizations/
|-- frontend/
|   |-- src/
|   |   |-- App.jsx
|   |   `-- components/
|   `-- package.json
|-- models/
|-- test_data/
|-- visualizations/
`-- README.md
```

## Troubleshooting

### Model not found

If the backend cannot find the trained model, retrain it:

```powershell
cd c:\Users\rohit\Desktop\sales-prediction-system\backend
venv\Scripts\python.exe train_integrated_model.py
```

### Frontend cannot connect

Make sure the backend is running on port `5000`.

### Gemini insights fail

Make sure `GOOGLE_API_KEY` exists in `backend/.env`.

## Summary

This project is designed to help retail businesses move from raw sales files to clear decisions. It combines forecasting, product-level exploration, festival-aware trend analysis, and multilingual AI explanations in one workflow.
