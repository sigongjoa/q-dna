import httpx
import base64
from typing import Optional, Dict, Any, List
from app.core.config import settings
import json


class OllamaService:
    """
    Ollama LLM Service for AI-powered features.
    Supports both text and vision models.
    """

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.vision_model = settings.OLLAMA_VISION_MODEL
        self.text_model = settings.OLLAMA_TEXT_MODEL

    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        format: Optional[str] = None
    ) -> str:
        """
        Generate text using Ollama text model.

        Args:
            prompt: User prompt
            model: Override default text model
            system: System prompt
            temperature: Creativity (0.0-1.0)
            format: 'json' for JSON output
        """
        model = model or self.text_model

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }

        if system:
            payload["system"] = system

        if format == "json":
            payload["format"] = "json"

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
            except httpx.HTTPError as e:
                print(f"Ollama API error: {e}")
                raise Exception(f"Failed to generate text: {str(e)}")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        format: Optional[str] = None
    ) -> str:
        """
        Chat completion using Ollama.

        Args:
            messages: List of {"role": "user/assistant/system", "content": "..."}
            model: Override default text model
            temperature: Creativity (0.0-1.0)
            format: 'json' for JSON output
        """
        model = model or self.text_model

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }

        if format == "json":
            payload["format"] = "json"

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                return result.get("message", {}).get("content", "")
            except httpx.HTTPError as e:
                print(f"Ollama API error: {e}")
                raise Exception(f"Failed to chat: {str(e)}")

    async def analyze_image(
        self,
        image_bytes: bytes,
        prompt: str,
        model: Optional[str] = None
    ) -> str:
        """
        Analyze image using Ollama vision model (e.g., llama3.2-vision).

        Args:
            image_bytes: Image file bytes
            prompt: What to analyze in the image
            model: Override default vision model
        """
        model = model or self.vision_model

        # Encode image to base64
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')

        payload = {
            "model": model,
            "prompt": prompt,
            "images": [image_b64],
            "stream": False
        }

        async with httpx.AsyncClient(timeout=180.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
            except httpx.HTTPError as e:
                print(f"Ollama vision API error: {e}")
                raise Exception(f"Failed to analyze image: {str(e)}")

    async def extract_json(self, text: str, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Helper to extract structured JSON from text.
        """
        try:
            # Try to parse as JSON directly
            return json.loads(text)
        except json.JSONDecodeError:
            # If failed, try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))

            # Last resort: ask model to clean it up
            cleaned = await self.generate_text(
                prompt=f"Extract only valid JSON from this text, no explanation:\n{text}",
                model=model,
                format="json"
            )
            return json.loads(cleaned)

    async def health_check(self) -> bool:
        """
        Check if Ollama service is running.
        """
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
            except:
                return False


ollama_service = OllamaService()
