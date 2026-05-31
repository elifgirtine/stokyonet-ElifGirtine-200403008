#!/bin/bash
echo ""
echo "===================================="
echo "   StokYönet - Başlatılıyor..."
echo "===================================="
echo ""

if [ ! -d "venv" ]; then
    echo "Sanal ortam oluşturuluyor..."
    python3 -m venv venv
fi

source venv/bin/activate

if [ ! -f "serviceAccountKey.json" ]; then
    echo "Firebase kurulumu gerekli!"
    python3 kurulum.py
else
    echo "Firebase kurulumu mevcut."
fi

echo ""
echo "Uygulama başlatılıyor..."
echo "Tarayıcıda açın: http://localhost:5001"
echo "Durdurmak için: CTRL+C"
echo ""
python3 app.py
