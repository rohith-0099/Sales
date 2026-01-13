# Sales Prediction System - Setup Instructions

## ⚠️ IMPORTANT: You need the Train.csv dataset!

Before running the model training, you **MUST** place your `Train.csv` file in the `backend/data/` folder.

If you don't have the dataset, you can download it from:
- Kaggle: Big Mart Sales Dataset
- Or use your own retail sales dataset with similar structure

## 📁 Expected Dataset Structure

The `Train.csv` should have these columns:
- Item_Identifier
- Item_Weight
- Item_Fat_Content
- Item_Visibility
- Item_Type
- Item_MRP
- Outlet_Identifier
- Outlet_Establishment_Year
- Outlet_Size
- Outlet_Location_Type
- Outlet_Type
- Item_Outlet_Sales (target variable)

## 🚀 Quick Start Guide

### Step 1: Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Create virtual environment (Mac/Linux)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# IMPORTANT: Add Train.csv to backend/data/ folder!

# Train the model (this will create sales_model.pkl)
python model.py

# Start Flask server
python app.py
```

Expected output:
```
✅ Model loaded successfully!
🚀 Starting Flask server...
 * Running on http://0.0.0.0:5000
```

### Step 2: Frontend Setup (New Terminal)

```bash
# Navigate to frontend
cd frontend

# Dependencies are already installed, just run:
npm run dev
```

Expected output:
```
VITE v7.3.1  ready in 500 ms
➜  Local:   http://localhost:5173/
```

### Step 3: Test the Application

1. Open browser: `http://localhost:5173`
2. Fill in the form with sample data
3. Click "Predict Sales"
4. See the prediction result!

## 🧪 Sample Test Data

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

## 🔧 Troubleshooting

### Backend Issues

**"No such file or directory: 'data/Train.csv'"**
- Solution: Place Train.csv in backend/data/ folder

**"Model not found"**
- Solution: Run `python model.py` first

**"Module not found"**
- Solution: Activate venv and run `pip install -r requirements.txt`

### Frontend Issues

**"Failed to connect to server"**
- Solution: Make sure Flask is running on port 5000

**CORS errors**
- Solution: flask-cors should be installed (check requirements.txt)

## 📊 What Happens During Training

When you run `python model.py`:
1. Loads Train.csv (8,523 rows)
2. Cleans missing values
3. Encodes categorical variables
4. Trains XGBoost model
5. Evaluates performance (R² ~0.56)
6. Saves model to `models/sales_model.pkl`
7. Creates visualizations in `visualizations/`

## 🎯 Next Steps

After setup:
- Try different product combinations
- Check prediction history
- View model visualizations in `backend/visualizations/`
- Customize the UI in `frontend/src/App.css`
- Improve model by tuning hyperparameters in `model.py`

## 📚 File Structure

```
sales-prediction-system/
├── backend/
│   ├── app.py                    ✅ Created
│   ├── model.py                  ✅ Created
│   ├── requirements.txt          ✅ Created
│   ├── models/                   ✅ Created (empty)
│   ├── data/                     ✅ Created (empty)
│   │   └── Train.csv            ❌ YOU NEED TO ADD THIS!
│   └── visualizations/           ✅ Created (empty)
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx              ✅ Created
│   │   ├── App.css              ✅ Created
│   │   └── main.jsx             ✅ Updated
│   ├── package.json             ✅ Created
│   └── node_modules/            ✅ Installed
│
├── README.md                     ✅ Created
├── .gitignore                    ✅ Created
└── SETUP.md                      ✅ This file
```

## ✅ Checklist

- [ ] Add Train.csv to backend/data/
- [ ] Create Python virtual environment
- [ ] Install Python dependencies
- [ ] Train the model
- [ ] Start Flask server
- [ ] Start React dev server
- [ ] Test prediction in browser

---

**Need help? Check the main README.md for detailed documentation!**
