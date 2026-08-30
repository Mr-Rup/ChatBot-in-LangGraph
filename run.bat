@echo off
set VENV_DIR=.myenv

echo Checking for virtual environment...
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Virtual environment not found. Creating a new one...
    python -m venv %VENV_DIR%
    
    echo Activating virtual environment...
    call "%VENV_DIR%\Scripts\activate.bat"
    
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
) else (
    echo Virtual environment found. Activating...
    call "%VENV_DIR%\Scripts\activate.bat"
)

echo.
echo Starting the ChatBot Application...
streamlit run frontend_streaming.py

pause
