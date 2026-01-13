@echo off
REM Quick Start Script for Sales Prediction System - Backend
REM This script activates the virtual environment and starts the Flask server

echo ========================================
echo Sales Prediction System - Backend
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup first:
    echo   python -m venv venv
    echo   venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check if model exists
if not exist "models\sales_model.pkl" (
    echo WARNING: Model not found!
    echo.
    echo You need to:
    echo 1. Add Train.csv to the data\ folder
    echo 2. Run: venv\Scripts\python model.py
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment and start server
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting Flask server...
echo Server will run on http://localhost:5000
echo Press Ctrl+C to stop
echo.

python app.py
