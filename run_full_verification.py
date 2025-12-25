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
    print("=== [Full Stack Verification] Starting... ===")
    
    # --- 1. Start Backend ---
    print(f"[*] Launching Backend (Uvicorn) on {API_PORT}...")
    env_backend = os.environ.copy()
    env_backend["PYTHONPATH"] = "./backend"
    env_backend["OLLAMA_TEXT_MODEL"] = "qwen2.5:latest" 
    
    backend_cmd = [
        sys.executable, "-m", "uvicorn", "app.main:app", 
        "--host", API_HOST, "--port", str(API_PORT)
    ]
    
    # Run in backend dir
    backend_proc = subprocess.Popen(
        backend_cmd, cwd="./backend", env=env_backend,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    
    # --- 2. Start Frontend ---
    print(f"[*] Launching Frontend (Vite) on {FRONTEND_PORT}...")
    # Using npx vite to avoid npm script issues
    frontend_cmd = ["npx", "vite", "--host", "--port", str(FRONTEND_PORT)]

    frontend_proc = subprocess.Popen(
        frontend_cmd, cwd="./frontend",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    print(f"[*] PIDs -> Backend: {backend_proc.pid}, Frontend: {frontend_proc.pid}")
    
    try:
        # --- 3. Wait for Services ---
        print("[*] Waiting for services to come online (30s)...")
        backend_ready = False
        frontend_ready = False
        start_time = time.time()
        
        while time.time() - start_time < 30:
            if not backend_ready:
                try:
                    requests.get(f"{BASE_URL}/questions/", timeout=1)
                    print("[+] Backend is UP!")
                    backend_ready = True
                except: pass
            
            if not frontend_ready:
                try:
                    res = requests.get(FRONTEND_URL, timeout=1)
                    if res.status_code == 200:
                        print(f"[+] Frontend is UP! ({len(res.text)} bytes)")
                        frontend_ready = True
                except: pass
            
            if backend_ready and frontend_ready:
                break
            
            # Check premature death
            if backend_proc.poll() is not None:
                print("[-] Backend died.")
                _, err = backend_proc.communicate()
                print(err)
                return
            if frontend_proc.poll() is not None:
                print("[-] Frontend died.")
                _, err = frontend_proc.communicate()
                print(err)
                return
                
            time.sleep(1)

        if not (backend_ready and frontend_ready):
            print(f"[-] Timeout. Backend:{backend_ready}, Frontend:{frontend_ready}")
            # If frontend failed, maybe it's building? Wait a bit more or check output
            if backend_ready and not frontend_ready:
                 print("Backend is ready but Frontend is not. Checking Frontend output...")
                 # We can't read stdout/stderr here easily without blocking or using threads, 
                 # but let's assume it failed if 30s passed.

        # --- 4. Verify Logic (If Backend is up at least) ---
        print("\n--- Running Tests ---")
        
        if frontend_ready:
            print("[SUCCESS] Frontend is serving content via HTTP.")
        else:
             print("[FAILURE] Frontend HTTP check failed.")

        if backend_ready:
            # Check API (Analyze & Twin)
            print("[Test] /analyze Endpoint")
            try:
                analyze_res = requests.post(f"{BASE_URL}/questions/analyze", params={"content_stem": "Test"})
                if analyze_res.status_code == 200:
                    print(f"[SUCCESS] Analyze OK: {analyze_res.json()}")
                else:
                    print(f"[FAILURE] Analyze: {analyze_res.text}")
            except Exception as e: print(f"Analyze Ex: {e}")

            print("[Test] /twin Endpoint")
            try:
                payload = {
                    "question_type": "short_answer",
                    "content_stem": "Test Q",
                    "content_metadata": {
                        "source": {"name": "Test", "year": 2024},
                        "domain": {"major_domain": "Number"},
                        "difficulty": {"estimated_level": 1}
                    },
                    "answer_key": {"answer": "A"},
                    "create_by": "00000000-0000-0000-0000-000000000000"
                }
                c_res = requests.post(f"{BASE_URL}/questions/", json=payload)
                if c_res.status_code == 200:
                    q_id = c_res.json()['question_id']
                    t_res = requests.post(f"{BASE_URL}/questions/{q_id}/twin")
                    if t_res.status_code == 200:
                        print(f"[SUCCESS] Twin OK: {t_res.json()['content_stem']}")
                    else:
                        print(f"[FAILURE] Twin: {t_res.status_code} {t_res.text}")
                else:
                    print(f"[FAILURE] Create: {c_res.status_code}")
            except Exception as e: print(f"Twin Ex: {e}")

    except Exception as e:
        print(f"[!] Critical Error: {e}")
        
    finally:
        print("\n[*] Shutting down...")
        backend_proc.terminate()
        frontend_proc.terminate()
        try:
            backend_proc.wait(timeout=2)
            frontend_proc.wait(timeout=2)
        except:
            backend_proc.kill()
            frontend_proc.kill()
        print("[*] Done.")

if __name__ == "__main__":
    main()
