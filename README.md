# 🚀 Sales Prediction & Retail Intelligence System

A professional-grade retail analytics platform that transforms raw sales data into actionable business strategies. The system combines time-series forecasting, product-level drill-downs, and multilingual AI insights to help retailers understand their past and predict their future.

---

## 🌟 Core Features

### 1. 📊 Smart Data Upload & Normalization
*   **Flexible Formats:** Supports `.xlsx` and `.csv` files.
*   **Automatic Detection:** Dynamically identifies date and sales columns, and infers data granularity (Daily, Weekly, Monthly, or Yearly).
*   **Product Extraction:** Automatically detects product identifiers (Names or IDs) to enable granular filtering.

### 2. 🔮 Advanced Sales Forecasting
*   **Prophet-Powered:** Uses the Meta Prophet model for robust time-series forecasting.
*   **Granular Predictions:** Matches the forecast length to your data (e.g., 30 days for daily data, 12 months for monthly data).
*   **Uncertainty Intervals:** Provides lower and upper confidence bounds for every prediction.

### 3. 🌍 Multi-Market Intelligence (New!)
*   **Market Selection:** Toggle between **India, USA, UK, UAE, Australia, and Canada**.
*   **Dynamic Currency:** Automatically switches symbols (₹, $, £, AED) and formatting based on the selected market.
*   **Holiday Awareness:** Injects country-specific holiday regressors (e.g., Diwali for India, Thanksgiving for USA) into the AI model for higher seasonal accuracy.

### 4. 🤖 Gemini AI Strategic Analyst
*   **Explainable Trends:** Generates natural language explanations of sales health.
*   **Actionable Advice:** Provides exactly 3 concrete steps to improve sales based on current data.
*   **Multilingual:** Supports **English, Hindi, Marathi, Bengali, Telugu, and Tamil**.

### 5. 🔬 Product Deep-Dive
*   **Searchable Inventory:** Quickly find any product from your uploaded dataset.
*   **Isolated Analysis:** View specific trends and local forecasts for a single item.
*   **Leaderboard:** Automatically ranks top-performing products by total sales and volume.

---

## 📁 Project Architecture

```text
sales-prediction-system/
├── backend/                # Flask Server
│   ├── app.py              # Main API Hub & Route Handlers
│   ├── analytics_engine.py # Core Forecasting & Data Logic (Prophet)
│   ├── market_holidays.py  # Global Holiday Database & Logic
│   ├── model.py            # XGBoost Single-Item Model (Attributes)
│   ├── requirements.txt    # Backend Dependencies
│   └── data/               # Historical Datasets
├── frontend/               # React (Vite) Application
│   ├── src/
│   │   ├── App.jsx         # Main Dashboard Interface
│   │   └── components/     # UI Components (Charts, Uploaders)
│   └── package.json        # Frontend Dependencies
└── models/                 # Saved ML Models (.pkl)
```

---

## 🛠️ Quick Start Guide

### 1. Prerequisites
*   Python 3.9+
*   Node.js & npm
*   Google Gemini API Key ([Get it here](https://aistudio.google.com/app/apikey))

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```
**Configure Environment:** Create a `.env` file in the `backend/` folder:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 4. Run the App
1.  Start the backend: `python app.py`
2.  Start the frontend: `npm run dev`
3.  Open `http://localhost:5173` in your browser.

---

## 📈 Usage Workflow
1.  **Select Market:** Choose your country from the top-right dropdown.
2.  **Upload:** Drag and drop your sales spreadsheet.
3.  **Analyze:** Click "Generate forecast and insights".
4.  **Explore:** Use the search bar to zoom into specific products.
5.  **Strategize:** Click "Generate AI insight" to get your business plan.

---

## ⚖️ Accuracy & Performance
The system uses a hybrid approach:
*   **Seasonality:** Captured via the Prophet model's Fourier series components.
*   **Holidays:** Modeled as point-in-time regressors with a +/- 7-day window.
*   **Granularity:** Optimized comparison windows for stable growth metrics.

*This project is designed for both Indian and International retail markets.*
