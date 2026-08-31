#!/usr/bin/env python3
"""
Blue Orbit Master System Launcher
ISRO SIH 2026 - Problem Statement 26176
Launches both FastAPI Multi-Agent Backend (port 8000) and React Vite Frontend (port 5173).
"""

import subprocess
import sys
import time
import os
import signal

def main():
    print("=" * 70)
    print("🌊 Blue Orbit — Marine Ecosystem Reasoning with Collaborative Agents")
    print("🚀 Indian Space Research Organisation (ISRO) · SIH 2026")
    print("=" * 70)

    # 1. Start Backend
    print("\n[1/2] 🛰️ Starting FastAPI Multi-Agent Backend on port 8000...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    # Wait 2 seconds for backend to start listening
    time.sleep(2)

    # 2. Start Frontend
    print("[2/2] 🖥️ Starting React Vite GIS Command Center on port 5173...")
    client_dir = os.path.join(os.path.dirname(__file__), "client")
    frontend_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=client_dir,
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    print("\n" + "=" * 70)
    print("✨ Blue Orbit Marine Intelligence Network is LIVE:")
    print("   • Web Command Center:   http://localhost:5173")
    print("   • FastAPI Backend Docs: http://localhost:8000/docs")
    print("   • Live Agent WebSocket: ws://localhost:8000/ws/agent-stream")
    print("   Press CTRL+C to gracefully stop all services.")
    print("=" * 70 + "\n")

    def handle_shutdown(sig, frame):
        print("\n🛑 Shutting down Blue Orbit services...")
        backend_proc.terminate()
        frontend_proc.terminate()
        backend_proc.wait()
        frontend_proc.wait()
        print("✓ All processes safely terminated. Goodbye!")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        handle_shutdown(None, None)

if __name__ == "__main__":
    main()
