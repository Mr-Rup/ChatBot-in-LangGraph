@echo off
set VENV_DIR=.myenv

echo Checking for virtual environment...
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Virtual environment not found. Creating a new one...
    py -3.11 -m venv %VENV_DIR%
    
    echo Activating virtual environment...
    call "%VENV_DIR%\Scripts\activate.bat"

    echo Checking/updating pip version
    python.exe -m pip install --upgrade pip
    
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
) else (
    echo Virtual environment found. Activating...
    call "%VENV_DIR%\Scripts\activate.bat"
    
    echo Checking/updating dependencies from requirements.txt...
    pip install -r requirements.txt
)

echo.
echo Starting the ChatBot Application...
python -m streamlit run app.py

pause
