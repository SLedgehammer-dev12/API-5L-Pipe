@echo off
chcp 65001 > nul
title Windows Standalone Exe Builder

echo ======================================================================
echo   📦 Building Windows One-File Executable (.exe) for API-5L-Pipe
echo ======================================================================
echo.

:: Check python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Python bulunamadi! Lutfen Python 3.10+ yukleyin.
    pause
    exit /b 1
)

echo 🔨 Bagimliliklar yukleniyor...
python -m pip install -r requirements.txt pyinstaller --quiet

echo 🔨 Temiz .exe derleniyor (Antivirus-Safe, No-UPX)...
pyinstaller --name "API-5L-Pipe" ^
    --onefile ^
    --noconfirm ^
    --clean ^
    --noupx ^
    --add-data "static;static" ^
    --add-data "templates;templates" ^
    --add-data "core;core" ^
    --hidden-import "uvicorn" ^
    --hidden-import "uvicorn.logging" ^
    --hidden-import "uvicorn.loops" ^
    --hidden-import "uvicorn.loops.auto" ^
    --hidden-import "uvicorn.protocols" ^
    --hidden-import "uvicorn.protocols.http" ^
    --hidden-import "uvicorn.protocols.http.auto" ^
    --hidden-import "uvicorn.lifespan" ^
    --hidden-import "uvicorn.lifespan.on" ^
    --hidden-import "fastapi" ^
    --hidden-import "openpyxl" ^
    --hidden-import "jinja2" ^
    --hidden-import "pydantic" ^
    run.py

echo.
echo ======================================================================
echo ✅ Windows .exe Dosyasi Basariyla Olusturuldu!
echo 📍 Konum: dist\API-5L-Pipe.exe
echo ======================================================================
pause
