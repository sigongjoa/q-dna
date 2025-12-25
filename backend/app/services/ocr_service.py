from PIL import Image
import io
import pytesseract
from typing import Dict, Any
from app.services.ollama_service import ollama_service


class OCRService:
    """
    OCR Service using Tesseract for basic text + Ollama vision for math equations.
    Combines both for best results in educational content.
    """

    async def extract_from_image_bytes(self, image_content: bytes) -> Dict[str, Any]:
        """
        Extract text and math from image bytes.

        Returns:
            {
                "text": "extracted text",
                "latex": "extracted LaTeX math",
                "combined": "full content with LaTeX",
                "has_math": bool
            }
        """
        try:
            # Step 1: Use Tesseract for basic text extraction
            image = Image.open(io.BytesIO(image_content))
            tesseract_text = pytesseract.image_to_string(image, lang='eng+kor')

            # Step 2: Use Ollama vision to extract math and refine
            vision_prompt = """Analyze this image and extract:
1. All text content (Korean and English)
2. All mathematical expressions in LaTeX format
3. Structure and formatting

Return in this exact JSON format:
{
    "text": "extracted plain text",
    "latex_expressions": ["\\\\frac{1}{2}", "x^2 + y^2 = z^2"],
    "combined_content": "full content with $latex$ inline and $$latex$$ display math",
    "has_mathematical_content": true/false
}"""

            vision_result = await ollama_service.analyze_image(
                image_bytes=image_content,
                prompt=vision_prompt
            )

            # Parse vision result
            try:
                vision_data = await ollama_service.extract_json(vision_result)
            except:
                # Fallback if JSON parsing fails
                vision_data = {
                    "text": tesseract_text,
                    "latex_expressions": [],
                    "combined_content": tesseract_text,
                    "has_mathematical_content": False
                }

            # Combine results
            result = {
                "text": vision_data.get("text", tesseract_text),
                "latex": vision_data.get("latex_expressions", []),
                "combined": vision_data.get("combined_content", tesseract_text),
                "has_math": vision_data.get("has_mathematical_content", False),
                "tesseract_fallback": tesseract_text
            }

            return result

        except Exception as e:
            print(f"OCR Error: {e}")
            # Emergency fallback
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
        """
        with open(file_path, 'rb') as f:
            image_bytes = f.read()
        return await self.extract_from_image_bytes(image_bytes)

    async def extract_question_from_image(self, image_content: bytes) -> Dict[str, Any]:
        """
        Specialized method to extract structured question data from image.

        Returns:
            {
                "question_stem": "문제 본문",
                "choices": ["A) ...", "B) ..."],
                "answer_key": "정답",
                "metadata": {...}
            }
        """
        # First get OCR results
        ocr_result = await self.extract_from_image_bytes(image_content)

        # Use Ollama to structure the question
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

        structured = await ollama_service.generate_text(
            prompt=structure_prompt,
            format="json"
        )

        try:
            question_data = await ollama_service.extract_json(structured)
            question_data["ocr_raw"] = ocr_result
            return question_data
        except:
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


ocr_service = OCRService()

