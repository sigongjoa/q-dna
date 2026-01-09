import requests
import uuid

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
# Use a known ID or fetch one
# Let's assume we can list questions or create one
# For test, we will try to create a dummy question first

def test_pdf_generation():
    print("🚀 Testing PDF Generation Endpoint...")
    
    # 1. Create a dummy question
    q_data = {
        "question_type": "short_answer",
        "content_stem": "PDF 테스트 문제입니다. 1+1은?",
        "content_metadata": {},
        "answer_key": {"answer": "2"},
        "create_by": "00000000-0000-0000-0000-000000000000",
        "status": "draft"
    }
    
    try:
        # Create Question
        print("1. Creating dummy question...")
        res = requests.post(f"{BASE_URL}/questions/", json=q_data)
        if res.status_code != 200:
            print(f"❌ Failed to create question: {res.text}")
            return
            
        q_id = res.json()["question_id"]
        print(f"✅ Created Question ID: {q_id}")
        
        # 2. Request PDF
        print("2. Requesting PDF (this triggers LLM, might take time)...")
        # We request PDF format
        pdf_res = requests.post(f"{BASE_URL}/questions/{q_id}/erroneous-solution", params={"output_format": "pdf"})
        
        if pdf_res.status_code == 200:
            # Check content type
            if "application/pdf" in pdf_res.headers.get("Content-Type", ""):
                 with open("test_download.pdf", "wb") as f:
                     f.write(pdf_res.content)
                 print("✅ PDF Downloaded successfully (test_download.pdf)")
                 print(f"   Size: {len(pdf_res.content)} bytes")
            else:
                 print(f"❌ Expected PDF content type, got: {pdf_res.headers.get('Content-Type')}")
                 print(f"   Body preview: {pdf_res.text[:200]}")
        else:
             print(f"❌ Failed to download PDF. Status: {pdf_res.status_code}")
             print(f"   Error: {pdf_res.text}")
             
    except Exception as e:
        print(f"❌ Exception during test: {e}")

if __name__ == "__main__":
    test_pdf_generation()
