"""
Tagging Service for Node 2 (Q-DNA).
Refactored to use mathesis_core.analysis.DNAAnalyzer.
"""
from typing import List, Dict
from mathesis_core.analysis import DNAAnalyzer
from mathesis_core.llm.clients import create_ollama_client
from mathesis_core.exceptions import AnalysisError
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class TaggingService:
    """
    AI-powered tagging service using mathesis_core.analysis.DNAAnalyzer.

    This is a thin service layer that:
    1. Delegates core DNA analysis to DNAAnalyzer (from mathesis_core)
    2. Handles FastAPI-specific concerns (DB, API)
    3. Maintains backward compatibility with existing API
    """

    def __init__(self):
        """Initialize Tagging Service with mathesis_core components."""
        # Create LLM client using mathesis_core
        self.llm_client = create_ollama_client(
            base_url=settings.OLLAMA_URL,
            model=settings.OLLAMA_MODEL
        )

        # Use DNAAnalyzer from mathesis_core
        self.dna_analyzer = DNAAnalyzer(self.llm_client)

    async def get_tag_recommendations(self, question_text: str) -> List[Dict]:
        """
        AI Auto-Tagging logic using DNAAnalyzer.
        Extracts curriculum path, cognitive level, skills, and concepts.

        This method maintains backward compatibility with the original API.
        Core logic is delegated to mathesis_core.analysis.DNAAnalyzer.

        Args:
            question_text: Question content

        Returns:
            List of {"tag": str, "confidence": float, "type": str}
        """
        try:
            # Delegate to DNAAnalyzer from mathesis_core
            dna = await self.dna_analyzer.analyze(question_text)

            # Extract tags from DNA result
            tags = dna.get("tags", [])

            # Validate and filter (same as before)
            valid_tags = []
            for tag_obj in tags:
                if all(k in tag_obj for k in ["tag", "type", "confidence"]):
                    # Ensure confidence is float
                    tag_obj["confidence"] = float(tag_obj["confidence"])
                    valid_tags.append(tag_obj)

            return valid_tags

        except AnalysisError as e:
            logger.error(f"Tagging error: {e}")
            # Fallback to basic keyword matching
            return self._fallback_tagging(question_text)

        except Exception as e:
            logger.error(f"Unexpected tagging error: {e}")
            return self._fallback_tagging(question_text)

    async def generate_metadata(self, question_text: str) -> Dict:
        """
        Generate comprehensive metadata using DNAAnalyzer.

        This method maintains backward compatibility with the original API.
        Core logic is delegated to mathesis_core.analysis.DNAAnalyzer.

        Args:
            question_text: Question content

        Returns:
            {
                "cognitive_level": str,
                "difficulty_estimation": float (0.0-1.0),
                "estimated_time_minutes": int,
                "subject_area": str,
                "curriculum_path": str (e.g., "Math.Algebra.Quadratics"),
                "requires_calculator": bool,
                "language": str
            }
        """
        try:
            # Delegate to DNAAnalyzer from mathesis_core
            dna = await self.dna_analyzer.analyze(question_text)

            # Extract metadata from DNA result
            metadata = dna.get("metadata", {})

            # Set defaults for missing fields (backward compatibility)
            metadata.setdefault("cognitive_level", "Apply")
            metadata.setdefault("difficulty_estimation", 0.5)
            metadata.setdefault("estimated_time_minutes", 5)
            metadata.setdefault("subject_area", "General")
            metadata.setdefault("curriculum_path", dna.get("curriculum_path", "General.Unknown"))
            metadata.setdefault("requires_calculator", False)
            metadata.setdefault("language", "Korean")

            return metadata

        except AnalysisError as e:
            logger.error(f"Metadata generation error: {e}")
            return self._default_metadata()

        except Exception as e:
            logger.error(f"Unexpected metadata error: {e}")
            return self._default_metadata()

    async def suggest_curriculum_path(self, question_text: str) -> str:
        """
        Suggest ltree curriculum path for the question using DNAAnalyzer.

        This method maintains backward compatibility with the original API.
        Core logic is delegated to mathesis_core.analysis.DNAAnalyzer.

        Args:
            question_text: Question content

        Returns:
            String like "Math.Algebra.Quadratics.Factoring"
        """
        try:
            # Delegate to DNAAnalyzer from mathesis_core
            dna = await self.dna_analyzer.analyze(question_text)

            # Extract curriculum path from DNA result
            path = dna.get("curriculum_path", "General.Unknown")

            # Clean up the response (same as before)
            path = path.strip().strip('"\'').split('\n')[0]
            return path if '.' in path else "General.Unknown"

        except Exception as e:
            logger.error(f"Curriculum path suggestion error: {e}")
            return "General.Unknown"

    def _fallback_tagging(self, question_text: str) -> List[Dict]:
        """
        Simple keyword-based fallback when AI fails.
        This is service-specific logic (not in mathesis_core).
        """
        tags = []
        text_lower = question_text.lower()

        # Math detection
        if any(word in text_lower for word in ["방정식", "equation", "x =", "solve"]):
            tags.append({"tag": "Mathematics", "type": "subject", "confidence": 0.8})
            tags.append({"tag": "Algebra", "type": "concept", "confidence": 0.7})

        # Geometry
        if any(word in text_lower for word in ["삼각형", "triangle", "원", "circle", "각", "angle"]):
            tags.append({"tag": "Geometry", "type": "concept", "confidence": 0.75})

        # Calculus
        if any(word in text_lower for word in ["미분", "적분", "derivative", "integral", "limit"]):
            tags.append({"tag": "Calculus", "type": "concept", "confidence": 0.85})

        # Default cognitive level
        tags.append({"tag": "Apply", "type": "cognitive_level", "confidence": 0.6})

        return tags if tags else [
            {"tag": "General", "type": "subject", "confidence": 0.5}
        ]

    def _default_metadata(self) -> Dict:
        """Return default metadata when analysis fails."""
        return {
            "cognitive_level": "Apply",
            "difficulty_estimation": 0.5,
            "estimated_time_minutes": 5,
            "subject_area": "General",
            "curriculum_path": "General.Unknown",
            "requires_calculator": False,
            "language": "Korean"
        }


# Singleton instance for backward compatibility
tagging_service = TaggingService()
