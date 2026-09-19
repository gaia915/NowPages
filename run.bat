@echo off
setlocal
cd /d "%~dp0"

echo ======================================================
echo   Planetarium Event Page Generator
echo ======================================================
echo.

echo [1/2] Checking Python dependencies...
python -m pip install -r requirements.txt -q

echo.
echo [2/2] Fetching events and generating pages...
python -X utf8 main.py

echo.
echo ======================================================
echo   Done! Opening dist\index.html in your browser...
echo ======================================================
start "" "%~dp0dist\index.html"
echo.
pause
