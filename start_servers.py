import subprocess
import time
import requests
import os
import signal
import sys

# Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
BASE_URL = f"http://localhost:{API_PORT}/api/v1"
FRONTEND_PORT = 5173
FRONTEND_URL = f"http://localhost:{FRONTEND_PORT}"

def main():
    print("=== [Server Launcher] Starting... ===")
    
    # --- 1. Start Backend ---
    print(f"[*] Launching Backend (Uvicorn) on {API_PORT}...")
    env_backend = os.environ.copy()
    env_backend["PYTHONPATH"] = "./backend"
    env_backend["OLLAMA_TEXT_MODEL"] = "qwen2.5:latest" 
    
    backend_cmd = [
        sys.executable, "-m", "uvicorn", "app.main:app", 
        "--host", API_HOST, "--port", str(API_PORT)
    ]
    
    backend_proc = subprocess.Popen(
        backend_cmd, cwd="./backend", env=env_backend,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    
    # --- 2. Start Frontend ---
    print(f"[*] Launching Frontend (Vite) on {FRONTEND_PORT}...")
    frontend_cmd = ["npx", "vite", "--host", "--port", str(FRONTEND_PORT)]

    frontend_proc = subprocess.Popen(
        frontend_cmd, cwd="./frontend",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    print(f"[*] PIDs -> Backend: {backend_proc.pid}, Frontend: {frontend_proc.pid}")
    
    # --- 3. Wait for Services ---
    print("[*] Waiting for services (max 60s)...")
    backend_ready = False
    frontend_ready = False
    start_time = time.time()
    
    while time.time() - start_time < 60:
        if not backend_ready:
            try:
                if requests.get(f"{BASE_URL}/questions/", timeout=1).status_code == 200:
                    print("[+] Backend is UP!")
                    backend_ready = True
            except: pass
        
        if not frontend_ready:
            try:
                if requests.get(FRONTEND_URL, timeout=1).status_code == 200:
                    print("[+] Frontend is UP!")
                    frontend_ready = True
            except: pass
        
        if backend_ready and frontend_ready:
            print("=== SERVERS READY ===")
            break
        
        if backend_proc.poll() is not None:
            print("[-] Backend died.")
            print(backend_proc.stderr.read())
            return
        if frontend_proc.poll() is not None:
            print("[-] Frontend died.")
            print(frontend_proc.stderr.read())
            return
            
        time.sleep(1)

    if backend_ready and frontend_ready:
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            pass
    
    print("[*] Shutting down...")
    backend_proc.terminate()
    frontend_proc.terminate()

if __name__ == "__main__":
    main()
