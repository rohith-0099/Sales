# 🚀 Quick Start Guide

## ✅ Setup Complete!

All dependencies are installed and ready to go!

## 📋 What You Need to Do Now

### Step 1: Add the Dataset (REQUIRED)

Download the **Big Mart Sales Dataset** and place `Train.csv` in:
```
backend/data/Train.csv
```

**Where to get it:**
- Kaggle: Search "Big Mart Sales Dataset"
- Analytics Vidhya: Big Mart Sales III

### Step 2: Train the Model

Open a terminal in the `backend` folder and run:

```bash
# Windows
venv\Scripts\python model.py

# Mac/Linux
source venv/bin/activate
python model.py
```

This will:
- Load and preprocess the data
- Train the XGBoost model
- Save the model to `models/sales_model.pkl`
- Generate visualizations

**Expected time:** 1-2 minutes

### Step 3: Start the Backend Server

**Option A - Using the batch file (Windows):**
```bash
start_server.bat
```

**Option B - Manual:**
```bash
# Windows
venv\Scripts\python app.py

# Mac/Linux
source venv/bin/activate
python app.py
```

Server will run on: `http://localhost:5000`

### Step 4: Start the Frontend

Open a **NEW terminal** in the `frontend` folder:

```bash
npm run dev
```

App will run on: `http://localhost:5173`

### Step 5: Test the Application

1. Open your browser to `http://localhost:5173`
2. Fill in the form with sample data:
   ```
   Item Identifier: FDA15
   Item Weight: 9.30
   Item Fat Content: Low Fat
   Item Visibility: 0.016
   Item Type: Dairy
   Item MRP: 249.81
   Outlet Identifier: OUT049
   Outlet Establishment Year: 1999
   Outlet Size: Medium
   Outlet Location Type: Tier 1
   Outlet Type: Supermarket Type1
   ```
3. Click "Predict Sales"
4. See the prediction! 🎉

## 🛠️ Helpful Scripts

### Verify Setup
Check if all dependencies are installed:
```bash
cd backend
venv\Scripts\python verify_setup.py
```

### Complete Setup (Windows)
Run the automated setup from project root:
```bash
setup.bat
```

## 📁 Project Structure

```
sales-prediction-system/
├── backend/
│   ├── venv/                    ✅ Created & configured
│   ├── models/                  ⏳ Will be created when you train
│   ├── data/
│   │   └── Train.csv           ❌ YOU NEED TO ADD THIS
│   ├── visualizations/          ⏳ Will be created when you train
│   ├── app.py                   ✅ Flask API
│   ├── model.py                 ✅ Training script
│   ├── verify_setup.py          ✅ Verification script
│   └── start_server.bat         ✅ Quick start script
│
└── frontend/
    ├── node_modules/            ✅ Dependencies installed
    ├── src/
    │   ├── App.jsx             ✅ Main component
    │   └── App.css             ✅ Styling
    └── package.json            ✅ Config
```

## ⚠️ Common Issues

### "Model not found"
- **Solution:** Run `python model.py` first to train the model

### "No such file: Train.csv"
- **Solution:** Add the dataset to `backend/data/Train.csv`

### "Failed to connect to server"
- **Solution:** Make sure Flask is running on port 5000
- Check if you see: `Running on http://0.0.0.0:5000`

### Port already in use
- **Backend (5000):** Stop other Flask apps or change port in `app.py`
- **Frontend (5173):** Stop other Vite apps or it will auto-assign a new port

## 🎯 Next Steps

1. ✅ Dependencies installed
2. ❌ Add Train.csv to `backend/data/`
3. ❌ Train model: `python model.py`
4. ❌ Start backend: `python app.py`
5. ❌ Start frontend: `npm run dev`
6. ❌ Test in browser

## 📚 Additional Resources

- **Full Documentation:** See `README.md`
- **Setup Details:** See `SETUP.md`
- **Project Walkthrough:** See the walkthrough artifact

## 💡 Tips

- Keep both terminals (backend & frontend) running
- Backend must be started before frontend for API calls to work
- Check `backend/visualizations/` for model performance charts after training
- Modify `App.css` to customize the UI appearance

---

**Ready to start? Add Train.csv and run `python model.py`!** 🚀
