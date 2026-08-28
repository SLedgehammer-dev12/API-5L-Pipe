#!/usr/bin/env python3
"""
Rock-solid launcher for API 5L PSL2 & BOTAŞ Pipe QA/QC & Design Suite.
Fully compatible with PyInstaller (--onefile, --windowed, .app, and standalone scripts)
on Windows, macOS (Apple Silicon & Intel), and Linux.
"""

import sys
import multiprocessing
import socket
import threading
import time
import webbrowser
import logging

# 1. Critical: Freeze support for PyInstaller multiprocessing on Windows & macOS
multiprocessing.freeze_support()

# Use the operating system trust store (Windows cert store / macOS keychain) in addition
# to certifi roots. Resolves "self-signed certificate in certificate chain" failures
# caused by corporate TLS-inspecting proxies / antivirus web protection on Windows.
# Guarded: a missing truststore must never break the app.
try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

# 2. Critical: Ensure stdout and stderr exist even in --windowed / --noconsole GUI mode
class DummyWriter:
    def write(self, s):
        pass
    def flush(self):
        pass

if sys.stdout is None:
    sys.stdout = DummyWriter()
if sys.stderr is None:
    sys.stderr = DummyWriter()

# Configure basic logging to avoid NoneType write errors in GUI mode
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 3. Dynamic Free Port Finder
def find_available_port(default_port=8000, max_attempts=50):
    for p in range(default_port, default_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    return default_port

def open_browser_delayed(url, delay=1.2):
    time.sleep(delay)
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Browser launch note: {e}")

def main():
    # 4. Import the ASGI application directly as a Python object
    # DO NOT use string "app:app" because PyInstaller bundle cannot locate module by string
    from app import app
    import uvicorn

    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            port = find_available_port(8000)
    else:
        port = find_available_port(8000)

    url = f"http://127.0.0.1:{port}"
    print("\n=======================================================")
    print("🚀 API 5L & BOTAŞ Boru Kalite Güvence Yazılımı Başlatıldı")
    print(f"🌐 Adres: {url}")
    print("=======================================================\n")

    # Start browser opener in background thread
    threading.Thread(target=open_browser_delayed, args=(url, 1.2), daemon=True).start()

    # Configure Uvicorn directly with ASGI app object
    config = uvicorn.Config(
        app=app,
        host="127.0.0.1",
        port=port,
        log_level="info",
        access_log=False,
        loop="asyncio"
    )
    server = uvicorn.Server(config)
    server.run()

if __name__ == "__main__":
    main()
