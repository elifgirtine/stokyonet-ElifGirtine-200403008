@echo off
chcp 65001 >nul
echo.
echo ====================================
echo    StokYonet - Baslatiliyor...
echo ====================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo Sanal ortam olusturuluyor...
    python -m venv venv
)

call venv\Scripts\activate.bat

if not exist "serviceAccountKey.json" (
    echo Firebase kurulumu gerekli!
    python kurulum.py
) else (
    echo Firebase kurulumu mevcut.
)

echo.
echo Uygulama baslatiliyor...
echo Tarayicida acin: http://localhost:5001
echo Durdurmak icin: CTRL+C
echo.
python app.py
pause
