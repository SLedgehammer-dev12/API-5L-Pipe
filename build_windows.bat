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

:: Read version from version.py
for /f "delims=" %%i in ('python -c "from version import __version__; print(__version__)"') do set VERSION=%%i
if "%VERSION%"=="" set VERSION=0.0.0

echo 🔨 Bagimliliklar yukleniyor...
python -m pip install -r requirements.txt pyinstaller --quiet

echo 🔨 Temiz .exe derleniyor (Antivirus-Safe, No-UPX)...
pyinstaller --name "API-5L-Pipe-Windows-x64-v%VERSION%" ^
    --onefile ^
    --noconfirm ^
    --clean ^
    --noupx ^
    --icon "static\icon\app_icon.ico" ^
    --add-data "static;static" ^
    --add-data "templates;templates" ^
    --add-data "core;core" ^
    --hidden-import "app" ^
    --hidden-import "core" ^
    --hidden-import "core.database" ^
    --hidden-import "core.pipe_qaqc_engine" ^
    --hidden-import "core.verification_engine" ^
    --hidden-import "core.wall_thickness_engine" ^
    --hidden-import "core.project_manager" ^
    --hidden-import "core.updater" ^
    --hidden-import "core.excel_exporter" ^
    --hidden-import "core.i18n" ^
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
    --hidden-import "core.pdf_exporter" ^
    --hidden-import "core.unlimited_ocr_engine" ^
    --hidden-import "core.itp_audit_engine" ^
    --hidden-import "core.sawh_engine" ^
    --collect-all reportlab ^
    --collect-all fitz ^
    --collect-all httpx ^
    --collect-all anyio ^
    --collect-all httpcore ^
    --collect-all certifi ^
    --hidden-import "truststore" ^
    --hidden-import "version" ^
    run.py

echo.
echo ======================================================================
echo ✅ Windows .exe Dosyasi Basariyla Olusturuldu!
echo 📍 Konum: dist\API-5L-Pipe-Windows-x64-v%VERSION%.exe
echo ======================================================================
pause