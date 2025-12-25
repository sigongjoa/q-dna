import requests
import time
import json

BASE_URL = "http://localhost:8000/api/v1"

def wait_for_server(retries=20):
    print("[*] Waiting for server to come online...")
    for i in range(retries):
        try:
            # Try a simple GET
            res = requests.get(f"{BASE_URL}/questions/")
            if res.status_code == 200:
                print("[+] Server is ONLINE!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(2)
        print(f"    Retry {i+1}...")
    return False

def verify_analyze():
    print("\n[1] Testing AI Analyze...")
    stem = "가로 5cm, 세로 3cm 직사각형의 넓이는?"
    try:
        res = requests.post(f"{BASE_URL}/questions/analyze", params={"content_stem": stem})
        if res.status_code == 200:
            print(f"[+] Analyze Success: {res.json()}")
            return True
        else:
            print(f"[-] Analyze Failed: {res.status_code} {res.text}")
    except Exception as e:
        print(f"[!] Error: {e}")
    return False

def verify_twin_flow():
    print("\n[2] Testing Create -> Twin Flow...")
    # 1. Create Question
    payload = {
        "question_type": "short_answer",
        "content_stem": "사과 3개가 있다. 2개를 더 받으면 몇 개인가?",
        "content_metadata": {
            "source": {"name": "Test", "year": 2024},
            "domain": {"major_domain": "Number"},
            "difficulty": {"estimated_level": 1}
        },
        "answer_key": {"answer": "5"},
        "create_by": "00000000-0000-0000-0000-000000000000",
        "difficulty_index": 0.5,
        "status": "draft"
    }
    
    try:
        # Create
        res = requests.post(f"{BASE_URL}/questions/", json=payload)
        if res.status_code != 200:
            print(f"[-] Create Failed: {res.status_code} {res.text}")
            return False
            
        created_q = res.json()
        q_id = created_q['question_id']
        print(f"[+] Created Question: {q_id}")
        
        # Generate Twin
        print(f"    Invoking Twin Generation (This may take a few seconds)...")
        twin_res = requests.post(f"{BASE_URL}/questions/{q_id}/twin")
        
        if twin_res.status_code == 200:
            print(f"[+] Twin Generated!: {twin_res.json()['content_stem']}")
            return True
        else:
            print(f"[-] Twin Gen Failed: {twin_res.status_code} {twin_res.text}")
            
    except Exception as e:
        print(f"[!] Error: {e}")
    return False

if __name__ == "__main__":
    if wait_for_server():
        ok_analyze = verify_analyze()
        ok_twin = verify_twin_flow()
        
        if ok_analyze and ok_twin:
            print("\n=== [SUCCESS] All Systems Operational ===")
            exit(0)
        else:
            print("\n=== [FAILURE] Some checks failed ===")
            exit(1)
    else:
        print("\n[!] Server did not start. Check logs.")
        exit(1)
