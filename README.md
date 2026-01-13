# 🛒 Indian Retail Sales Forecasting System

AI-powered sales prediction platform with CSV upload, festival analysis, and demographic insights for Indian retail markets.

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.8+** installed
- **Node.js 16+** and npm installed
- Virtual environment already set up in `backend/venv/`

---

## ▶️ Starting the Application

You need **TWO terminal windows** - one for backend, one for frontend.

### 1️⃣ Start Backend (Flask API)

**Open Terminal 1:**

```powershell
# Navigate to backend folder
cd c:\Users\rohit\Desktop\sales-prediction-system\backend

# Activate virtual environment and start server
venv\Scripts\python.exe app.py
```

**✅ Expected Output:**
```
✅ Integrated model loaded successfully!
   Features: 25
   Test R²: 0.9359
   Datasets: BigMart, Diwali Sales, Indian Retail
🚀 Starting Enhanced Flask server...
📊 Festival calendar loaded
🔮 Forecasting capabilities enabled
 * Running on http://127.0.0.1:5000
```

**Backend is ready when you see:** `Running on http://127.0.0.1:5000`

---

### 2️⃣ Start Frontend (React + Vite)

**Open Terminal 2:**

```powershell
# Navigate to frontend folder
cd c:\Users\rohit\Desktop\sales-prediction-system\frontend

# Start development server
npm run dev
```

**✅ Expected Output:**
```
VITE v5.4.21  ready in 651 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

**Frontend is ready when you see:** `Local: http://localhost:5173/`

---

### 3️⃣ Access the Application

Open your browser and navigate to:
```
http://localhost:5173
```

You should see the **Indian Retail Sales Forecasting System** dashboard with:
- **Bulk Forecast (CSV Upload)** tab - Upload historical data for predictions
- **Single Item Prediction** tab - Individual product forecasting

---

## 🛠️ Alternative: Using Batch Files (Windows Only)

### Backend:
```powershell
cd backend
.\start_server.bat
```

### Frontend:
```powershell
cd frontend
npm run dev
```

---

## ⚙️ Features Overview

### 📊 Bulk CSV Forecasting
1. Click **"Bulk Forecast (CSV Upload)"** tab
2. Drag & drop a CSV file with columns: `date`, `sales`
3. Get instant:
   - 30-day forecast
   - Festival impact analysis
   - Pattern recognition

### 🔮 Single Item Prediction
1. Click **"Single Item Prediction"** tab
2. Enter product details (weight, MRP, category, etc.)
3. Get immediate sales prediction

---

## 📁 Project Structure

```
sales-prediction-system/
├── backend/                    # Flask API server
│   ├── venv/                   # Python virtual environment
│   ├── models/                 # Trained ML models
│   │   └── integrated_sales_model.pkl (22K+ records, R²=0.9359)
│   ├── data/                   # Datasets
│   │   ├── diwali_sales/       # 11K Diwali transactions
│   │   ├── indian_retail/      # 2.5K retail orders
│   │   └── unified_training_data.csv (Combined dataset)
│   ├── app.py                  # Main Flask application
│   ├── indian_holidays.py      # Festival calendar
│   └── requirements.txt        # Python dependencies
│
└── frontend/                   # React + Vite interface
    ├── src/
    │   ├── App.jsx             # Main dashboard
    │   ├── components/
    │   │   ├── FileUpload.jsx  # CSV upload component
    │   │   └── ForecastChart.jsx # Interactive charts
    │   └── App.css             # Tailwind styles
    ├── package.json            # Node dependencies
    └── tailwind.config.js      # Tailwind configuration
```

---

## 🔧 Troubleshooting

### ❌ Port Already in Use

**Backend (Port 5000):**
```powershell
# Check what's using port 5000
netstat -ano | findstr :5000

# Kill the process (replace <PID> with actual number)
taskkill /PID <PID> /F
```

**Frontend (Port 5173):**
```powershell
# Check what's using port 5173
netstat -ano | findstr :5173

# Vite will auto-assign a different port if 5173 is busy
```

### ❌ Backend Error: "Model not found"

The integrated model should be at `backend/models/integrated_sales_model.pkl`.

**Solution:**
```powershell
cd backend
venv\Scripts\python.exe train_integrated_model.py
```

This will retrain the model using all three datasets.

### ❌ Frontend Error: "Failed to connect to server"

**Check:**
1. Backend is running on port 5000
2. Look for: `Running on http://127.0.0.1:5000` in backend terminal
3. If not running, restart backend server

### ❌ Dependencies Missing

**Backend:**
```powershell
cd backend
venv\Scripts\pip install -r requirements.txt
```

**Frontend:**
```powershell
cd frontend
npm install
```

---

## 📊 Model Information

### Current Model: **Integrated Sales Model**
- **Training Data:** 22,285 records
- **Data Sources:** BigMart + Diwali Sales + Indian Retail
- **Accuracy:** R² = 0.9359 (93.59%)
- **Features:** 25+ (demographics, festivals, regions, temporal)

### Top Predictive Features:
1. **Gender** - Customer demographics
2. **Year** - Temporal trends
3. **Festival Season** - Diwali, Eid, Holi impact
4. **Month** - Seasonal patterns
5. **Region/State** - Geographic variations

---

## 🎯 Use Cases

### Scenario 1: CSV Bulk Upload
"Upload 1 year of store sales data to get next 30-day forecast with festival overlays"

### Scenario 2: Diwali Planning
"Predict sales surge during Diwali week for inventory optimization"

### Scenario 3: Regional Analysis
"Compare sales patterns across North vs South India"

---

## 📝 API Endpoints

The backend provides these REST APIs:

| Endpoint | Method | Purpose |
|:---------|:-------|:--------|
| `/api/predict` | POST | Single item prediction |
| `/api/upload-csv` | POST | Upload historical sales CSV |
| `/api/forecast` | POST | Generate time-series forecast |
| `/api/analyze-patterns` | POST | Pattern analysis |
| `/api/festival-impact` | GET | Upcoming festivals |
| `/api/health` | GET | Server health check |

---

## 🛑 Stopping the Application

**Backend:**
- Press `Ctrl + C` in the backend terminal

**Frontend:**
- Press `Ctrl + C` in the frontend terminal

---

## 📚 Additional Documentation

- [SETUP.md](SETUP.md) - Initial setup and installation
- [QUICKSTART.md](QUICKSTART.md) - First-time configuration
- [backend/data/README.md](backend/data/README.md) - Dataset documentation
- Walkthrough artifact - Complete feature guide

---

## 🎉 You're All Set!

The system is now ready to forecast Indian retail sales with 93.59% accuracy! 

**Need help?** Check the troubleshooting section above or review the documentation files.
