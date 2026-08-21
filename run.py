#!/usr/bin/env python3
"""
Launcher script for API 5L PSL2 & BOTAŞ Pipe QA/QC & Design Suite.
Starts Uvicorn server and automatically opens the browser.
"""

import sys
import webbrowser
import threading
import time
import uvicorn

def open_browser(port=8000):
    time.sleep(1.2)
    url = f"http://127.0.0.1:{port}"
    print(f"\n=======================================================")
    print(f"🚀 API 5L & BOTAŞ Boru Kalite Güvence ve Kabul Yazılımı Başlatıldı!")
    print(f"🌐 Tarayıcı Adresi: {url}")
    print(f"=======================================================\n")
    webbrowser.open(url)

if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            port = 8000

    # Start browser opener in background thread
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    # Start Uvicorn FastAPI server
    uvicorn.run("app:app", host="127.0.0.1", port=port, reload=False, log_level="info")
