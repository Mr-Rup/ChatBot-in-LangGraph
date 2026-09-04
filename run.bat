@echo off
setlocal
title ChatBot - LangGraph Application
chcp 65001 >nul

set VENV_DIR=.myenv

echo ============================================================
echo Starting ChatBot Application...
echo ============================================================

:: Check if python launcher or python is available
py --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    python --version >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Python is not installed or not added to your PATH!
        echo Please install Python 3.11+ to run this application.
        pause
        exit /b 1
    )
)

:: Check for .env file
if not exist ".env" (
    echo [WARNING] No .env file found in the root directory.
    echo If you are using API models, you will need to add your API keys here!
    echo.
)

echo Checking for virtual environment...
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [INFO] Virtual environment not found. Creating a new one...
    py -3.11 -m venv %VENV_DIR% || python -m venv %VENV_DIR%
    
    echo [INFO] Activating virtual environment...
    call "%VENV_DIR%\Scripts\activate.bat"

    echo [INFO] Upgrading pip...
    python -m pip install --upgrade pip -q
    
    echo [INFO] Installing dependencies from requirements.txt (this may take a while)...
    pip install -r requirements.txt
) else (
    echo [INFO] Virtual environment found. Activating...
    call "%VENV_DIR%\Scripts\activate.bat"
    
    echo [INFO] Verifying dependencies...
    :: Using -q to keep the terminal clean if everything is already installed
    pip install -r requirements.txt -q
)

:: Interactive model selection from config.json & backend/models.json
python -c "from backend.config import prompt_model_selection; prompt_model_selection()"

echo.
echo ============================================================
echo Launching Streamlit Interface...
echo ============================================================
python -m streamlit run app.py

pause
