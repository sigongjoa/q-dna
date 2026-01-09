"""
OCR Service for Node 2 (Q-DNA).
Refactored to use mathesis_core.vision.OCREngine.
"""
from typing import Dict, Any
from mathesis_core.vision import OCREngine
from mathesis_core.llm.clients import create_ollama_client
from mathesis_core.llm.parsers import LLMJSONParser
from mathesis_core.exceptions import OCRError
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class OCRService:
    """
    OCR Service using mathesis_core.vision.OCREngine.

    This is a thin service layer that:
    1. Delegates core OCR logic to OCREngine (from mathesis_core)
    2. Handles FastAPI-specific concerns (DB, API)
    3. Maintains backward compatibility with existing API
    """

    def __init__(self):
        """Initialize OCR Service with mathesis_core components."""
        # Create LLM client using mathesis_core
        self.llm_client = create_ollama_client(
            base_url=settings.OLLAMA_URL,
            model=settings.OLLAMA_MODEL
        )

        # Use OCREngine from mathesis_core
        self.ocr_engine = OCREngine(self.llm_client)

    async def extract_from_image_bytes(self, image_content: bytes) -> Dict[str, Any]:
        """
        Extract text and math from image bytes.

        This method maintains backward compatibility with the original API.
        Core logic is delegated to mathesis_core.vision.OCREngine.

        Args:
            image_content: Raw image bytes

        Returns:
            {
                "text": "extracted text",
                "latex": "extracted LaTeX math",
                "combined": "full content with LaTeX",
                "has_math": bool,
                "tesseract_fallback": str (optional),
                "confidence": float (optional)
            }

        Raises:
            OCRError: If extraction fails completely
        """
        try:
            # Delegate to OCREngine from mathesis_core
            result = await self.ocr_engine.extract(image_content)
            return result

        except OCRError as e:
            logger.error(f"OCR Error: {e}")
            # Emergency fallback for backward compatibility
            return {
                "text": "OCR processing failed. Please try again.",
                "latex": [],
                "combined": str(e),
                "has_math": False,
                "error": str(e)
            }

    async def process_image_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process image from file path.

        Args:
            file_path: Path to image file

        Returns:
            OCR result dictionary
        """
        with open(file_path, 'rb') as f:
            image_bytes = f.read()
        return await self.extract_from_image_bytes(image_bytes)

    async def extract_question_from_image(self, image_content: bytes) -> Dict[str, Any]:
        """
        Specialized method to extract structured question data from image.

        This method combines OCR with question structuring.

        Args:
            image_content: Raw image bytes

        Returns:
            {
                "question_stem": "문제 본문",
                "choices": ["A) ...", "B) ..."] or None,
                "question_type": "mcq|short_answer|essay",
                "subject_area": "Math|Science|etc",
                "estimated_difficulty": 0.1-1.0,
                "keywords": ["keyword1", "keyword2"],
                "ocr_raw": {...}
            }
        """
        # Step 1: Get OCR results using OCREngine
        ocr_result = await self.extract_from_image_bytes(image_content)

        # Step 2: Structure the question using LLM
        structure_prompt = f"""Given this OCR text from a question image:

{ocr_result['combined']}

Extract and structure this as an educational question in JSON format:
{{
    "question_stem": "main question text with math in LaTeX",
    "question_type": "mcq|short_answer|essay",
    "choices": ["choice A", "choice B", ...] or null,
    "subject_area": "Math|Science|etc",
    "estimated_difficulty": 0.1-1.0,
    "keywords": ["keyword1", "keyword2"]
}}"""

        try:
            structured = await self.llm_client.generate(
                prompt=structure_prompt,
                format="json",
                temperature=0.3
            )

            question_data = LLMJSONParser.safe_parse(structured, default={
                "question_stem": ocr_result["combined"],
                "question_type": "short_answer",
                "choices": None,
                "subject_area": "Unknown",
                "estimated_difficulty": 0.5,
                "keywords": []
            })

            # Include raw OCR result
            question_data["ocr_raw"] = ocr_result
            return question_data

        except Exception as e:
            logger.warning(f"Question structuring failed: {e}, using fallback")
            # Fallback
            return {
                "question_stem": ocr_result["combined"],
                "question_type": "short_answer",
                "choices": None,
                "subject_area": "Unknown",
                "estimated_difficulty": 0.5,
                "keywords": [],
                "ocr_raw": ocr_result
            }


# Singleton instance for backward compatibility
ocr_service = OCRService()
