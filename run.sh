#!/usr/bin/env bash
# ======================================================================
# API 5L PSL2 & BOTAŞ Pipe QA/QC Suite Launcher (macOS / Linux)
# Compatible with Apple Silicon (M1/M2/M3/M4), Intel Mac, and Linux
# ======================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "======================================================================"
echo "  🚀 API 5L PSL2 & BOTAŞ Boru Kalite Güvence Yazılımı v2.1.0"
echo "  💻 Sistem: $(uname -s) ($(uname -m))"
echo "======================================================================"
echo ""

# Check python3
if ! command -v python3 &> /dev/null; then
    echo "❌ [HATA] python3 bulunamadı! Lütfen Python 3.10+ yükleyin."
    exit 1
fi

echo "🔍 Bağımlılıklar kontrol ediliyor..."
python3 -m pip install -r requirements.txt --quiet

echo "🌐 Sunucu başlatılıyor..."
python3 run.py
