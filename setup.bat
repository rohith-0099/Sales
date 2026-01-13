@echo off
REM Complete Setup Script for Sales Prediction System

echo ========================================
echo Sales Prediction System - Complete Setup
echo ========================================
echo.

cd backend

REM Step 1: Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)
echo ✓ Python found

REM Step 2: Create virtual environment
echo.
echo [2/5] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

REM Step 3: Install dependencies
echo.
echo [3/5] Installing Python dependencies...
echo This may take a few minutes...
call venv\Scripts\activate.bat
pip install --quiet --upgrade pip
pip install --quiet flask flask-cors pandas numpy scikit-learn xgboost matplotlib seaborn
echo ✓ Dependencies installed

REM Step 4: Verify setup
echo.
echo [4/5] Verifying installation...
python verify_setup.py
if errorlevel 1 (
    echo ERROR: Setup verification failed!
    pause
    exit /b 1
)

REM Step 5: Check for dataset
echo.
echo [5/5] Checking for dataset...
if not exist "data\Train.csv" (
    echo.
    echo ⚠️  WARNING: Train.csv not found in data\ folder
    echo.
    echo You need to add the dataset before training the model.
    echo Download it from Kaggle: Big Mart Sales Dataset
    echo.
) else (
    echo ✓ Dataset found
)

cd ..

echo.
echo ========================================
echo ✅ SETUP COMPLETE!
echo ========================================
echo.
echo NEXT STEPS:
echo 1. Add Train.csv to backend\data\ folder (if not done)
echo 2. Train model: cd backend ^&^& venv\Scripts\python model.py
echo 3. Start backend: cd backend ^&^& start_server.bat
echo 4. Start frontend: cd frontend ^&^& npm run dev
echo 5. Open http://localhost:5173
echo.
pause
