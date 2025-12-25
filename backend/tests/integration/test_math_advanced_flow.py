import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings

# This test requires a running Ollama instance and DB availability.
# We will use 'pytest-asyncio' for async test support.

@pytest.mark.asyncio
async def test_analyze_question_flow():
    """
    Test the full flow of Question Analysis (AI) API.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Prepare Test Payload
        test_stem = """
        [15] 다음 그림과 같이 가로가 10cm, 세로가 8cm인 직사각형 내부의 한 점 P에서
        각 변에 내린 수선의 발까지의 거리의 합이 최소가 되도록 할 때, 그 점 P의 위치를 구하시오.
        """
        
        # 2. Call /analyze Endpoint
        print(f"\n[Test] Sending Request to OLLAMA ({settings.OLLAMA_BASE_URL})...")
        response = await ac.post(
            f"{settings.API_V1_STR}/questions/analyze",
            params={"content_stem": test_stem}
        )

# ... (middle lines unchanged) ...

@pytest.mark.asyncio
async def test_twin_generation_flow():
    """
    Test Twin Generation Flow: Create Question -> Generate Twin.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        
        print(f"[Test] Response Status: {response.status_code}")
        print(f"[Test] Response Body: {response.json()}")

        # 3. Validation
        assert response.status_code == 200
        data = response.json()
        
        # Check if Metadata is structured correctly
        assert "source" in data
        assert "domain" in data
        assert "difficulty" in data
        
        # Verify AI inference (Loose check)
        assert data['domain'].get('major_domain') in ["Geometry", "Measurement", "Number", "Regularity", "Data"]
        # If the problem is about geometry (rectangle), it should likely be Geometry.
        if data['domain'].get('major_domain') == 'Geometry':
            print("[Pass] AI correctly identified Geometry domain.")
        else:
            print(f"[Warn] AI identified domain as {data['domain'].get('major_domain')}")

@pytest.mark.asyncio
async def test_twin_generation_flow():
    """
    Test Twin Generation Flow: Create Question -> Generate Twin.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Create a Base Question
        question_payload = {
            "question_type": "short_answer",
            "content_stem": "사과가 5개, 배가 3개 있다. 과일은 모두 몇 개인가?",
            "content_metadata": {
                "source": {"name": "Test", "year": 2024},
                "domain": {"major_domain": "Number"},
                "difficulty": {"estimated_level": 1}
            },
            "answer_key": {"answer": "8"},
            "create_by": "00000000-0000-0000-0000-000000000000",
            "status": "draft"
        }
        
        create_res = await ac.post(f"{settings.API_V1_STR}/questions/", json=question_payload)
        print(f"[Test] Create Response: {create_res.status_code} {create_res.text}")
        assert create_res.status_code == 200
        q_id = create_res.json()['question_id']
        print(f"\n[Test] Created Question ID: {q_id}")

        # 2. Call /twin Endpoint (This invokes OLLAMA)
        print(f"[Test] Requesting Twin Generation from OLLAMA...")
        twin_res = await ac.post(f"{settings.API_V1_STR}/questions/{q_id}/twin")
        
        print(f"[Test] Twin Response Status: {twin_res.status_code}")
        print(f"[Test] Twin Response Body: {twin_res.json()}")

        assert twin_res.status_code == 200
        twin_data = twin_res.json()
        
        # 3. Validation
        assert twin_data['is_twin_generated'] is True
        assert twin_data['original_question_id'] == q_id
        assert twin_data['content_stem'] != question_payload['content_stem']
        print("[Pass] Twin Question Generated Successfully.")
