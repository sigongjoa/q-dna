from typing import Optional, Dict, Any, List
from app.core.config import settings
from mathesis_core.llm.clients import create_ollama_client
from mathesis_core.llm.parsers import LLMJSONParser

class OllamaService:
    """
    Ollama LLM Service for AI-powered features.
    Unified via mathesis-common.
    """

    def __init__(self):
        self.client = create_ollama_client(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_TEXT_MODEL,
            async_mode=True
        )
        self.vision_model = settings.OLLAMA_VISION_MODEL
        self.text_model = settings.OLLAMA_TEXT_MODEL

    async def generate_text(self, prompt: str, **kwargs) -> str:
        return await self.client.async_chat(
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )

    async def chat(self, messages: List[Dict], **kwargs) -> str:
        return await self.client.async_chat(messages, **kwargs)

    async def analyze_image(self, image_bytes: bytes, prompt: str, **kwargs) -> str:
        # In a real scenario, we'd save bytes or adapt OllamaClient to take bytes
        # For now, keeping the interface but delegating as much as possible
        import base64
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        return await self.client.async_chat(
            messages=[{"role": "user", "content": prompt, "images": [image_b64]}],
            **kwargs
        )

    async def extract_json(self, text: str, **kwargs) -> Dict[str, Any]:
        return LLMJSONParser.parse(text)

    async def health_check(self) -> bool:
        return await self.client._async_health_check()

ollama_service = OllamaService()
