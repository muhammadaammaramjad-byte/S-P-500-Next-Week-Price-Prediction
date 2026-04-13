@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   S&P 500 Predictor - Env Setup
echo ========================================

echo.
echo [1/6] Checking Python version...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo [2/6] Removing old environment if exists...
if exist venv (
    rmdir /s /q venv
    echo Old venv removed
)

echo.
echo [3/6] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create venv
    pause
    exit /b 1
)

echo.
echo [4/6] Activating environment...
call venv\Scripts\activate

echo.
echo [5/6] Upgrading pip, setuptools, wheel...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo ERROR: pip upgrade failed
    pause
    exit /b 1
)

echo.
echo [6/6] Installing dependencies...
pip install --no-cache-dir -r requirements.txt
if errorlevel 1 (
    echo ERROR: Dependency installation failed
    pause
    exit /b 1
)

echo.
echo Verifying critical packages...
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import pandas; print('Pandas:', pandas.__version__)"
python -c "import catboost; print('CatBoost:', catboost.__version__)"
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"

if errorlevel 1 (
    echo ERROR: Package verification failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo   SETUP SUCCESSFUL ✅
echo ========================================
echo.
echo To activate environment:
echo   venv\Scripts\activate
echo.
echo To run API:
echo   python api.py
echo.
pause
endlocal