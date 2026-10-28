import os
import sys
import time
import subprocess
import webbrowser

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    print("=" * 60)
    print("      AGRISENTINEL 1-CLICK DEMO LAUNCHER")
    print("=" * 60)
    print("\n[1/2] Starting Backend Server (FastAPI)...")
    backend_proc = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "main:app",
        "--host", "127.0.0.1", "--port", "8000"
    ])

    time.sleep(2)

    print("[2/2] Starting Dashboard (Streamlit)...")
    dashboard_proc = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "dashboard.py",
        "--server.port", "8501", "--server.headless", "false"
    ])

    time.sleep(2)
    webbrowser.open("http://localhost:8501")

    print("\n" + "=" * 60)
    print("  All services active!")
    print("  Dashboard: http://localhost:8501")
    print("  API Docs:  http://127.0.0.1:8000/docs")
    print("  Press Ctrl+C to stop all services.")
    print("=" * 60 + "\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down services...")
        backend_proc.terminate()
        dashboard_proc.terminate()
        print("Done.")

if __name__ == "__main__":
    main()
