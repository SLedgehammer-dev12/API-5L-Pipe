@echo off
chcp 65001 > nul
title API 5L PSL2 & BOTAS Boru Kalite Guvence Yazilimi

echo ======================================================================
echo   API 5L PSL2 & BOTAS Boru Kalite Guvence ve Tasarim Yazilimi v1.0.0
echo ======================================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Python bulunamadi! Lutfen Python 3.10 veya uzeri bir surumu yukleyin.
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Install / verify requirements
echo [BILGI] Bagimliliklar kontrol ediliyor...
python -m pip install -r requirements.txt --quiet

:: Launch application
echo.
echo [BASLATILIYOR] Tarayiciniz otomatik olarak acilacaktir...
echo Adres: http://127.0.0.1:8000
echo.
python run.py

pause
