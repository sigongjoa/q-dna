"""
Math Advanced Service for Node 2 (Q-DNA).
Refactored to use mathesis_core.generation.ProblemGenerator.
"""
from typing import Dict, Any
from mathesis_core.generation import ProblemGenerator
from mathesis_core.analysis import DNAAnalyzer
from mathesis_core.llm.clients import create_ollama_client
from mathesis_core.llm.parsers import LLMJSONParser
from mathesis_core.exceptions import GenerationError, AnalysisError
from app.core.config import settings
from app.schemas.question import QuestionMetadata, ExamSourceInfo, MathDomainInfo, DifficultyMetrics, QuestionCreate, Question
import logging

logger = logging.getLogger(__name__)


class MathAdvancedService:
    """
    Service for handling Advanced Math specific logic using mathesis_core modules.

    This is a thin service layer that:
    1. Delegates core generation logic to ProblemGenerator (from mathesis_core)
    2. Handles FastAPI-specific concerns (DB, API, Pydantic schemas)
    3. Maintains backward compatibility with existing API
    """

    def __init__(self):
        """Initialize MathAdvancedService with mathesis_core components."""
        # Create LLM client using mathesis_core
        self.client = create_ollama_client(
            base_url=settings.OLLAMA_URL,
            model=settings.OLLAMA_MODEL
        )

        # Use ProblemGenerator and DNAAnalyzer from mathesis_core
        self.generator = ProblemGenerator(self.client)
        self.dna_analyzer = DNAAnalyzer(self.client)

    async def analyze_question_metadata(self, content_stem: str) -> QuestionMetadata:
        """
        Analyze question text and extract metadata using DNAAnalyzer.

        This method maintains backward compatibility with the original API.
        Core logic is delegated to mathesis_core.analysis.DNAAnalyzer.

        Args:
            content_stem: Question text

        Returns:
            QuestionMetadata (Pydantic model)
        """
        try:
            # Use DNAAnalyzer to get metadata
            dna = await self.dna_analyzer.analyze(content_stem)
            metadata_dict = dna.get("metadata", {})

            # Convert to Pydantic schema expected by Node 2 API
            return QuestionMetadata(
                source=ExamSourceInfo(
                    name=metadata_dict.get("source_name", "Unknown"),
                    grade=metadata_dict.get("grade", 5),
                    year=metadata_dict.get("year", 2024),
                    number=metadata_dict.get("question_number", 1)
                ),
                domain=MathDomainInfo(
                    major_domain=metadata_dict.get("subject_area", "Number"),
                    advanced_topic=metadata_dict.get("curriculum_path", "General").split(".")[-1]
                ),
                difficulty=DifficultyMetrics(
                    estimated_level=int(metadata_dict.get("difficulty_estimation", 0.5) * 5),  # 0.0-1.0 → 1-5
                    required_skills=dna.get("keywords", [])[:3]  # Top 3 skills
                )
            )

        except AnalysisError as e:
            logger.error(f"Metadata analysis error: {e}")
            # Fallback to default if AI fails
            return QuestionMetadata(
                source=ExamSourceInfo(name="Unknown", grade=5),
                domain=MathDomainInfo(major_domain="Number"),
                difficulty=DifficultyMetrics()
            )

    async def generate_twin_question(self, original_question: Question) -> QuestionCreate:
        """
        Generate a twin question based on the original question logic.

        This method maintains backward compatibility with the original API.
        Core logic is delegated to mathesis_core.generation.ProblemGenerator.

        Args:
            original_question: Original Question object

        Returns:
            QuestionCreate (Pydantic schema for creating new question)

        Raises:
            GenerationError: If generation fails
        """
        try:
            meta = original_question.content_metadata
            original_text = original_question.content_stem

            # Prepare question dict for ProblemGenerator
            question_dict = {
                "content_stem": original_text,
                "answer_key": original_question.answer_key or {"answer": ""},
                "question_type": original_question.question_type,
                "content_metadata": {
                    "source": {
                        "name": meta.source.name if meta and meta.source else "Unknown",
                        "grade": meta.source.grade if meta and meta.source else 5
                    },
                    "domain": {
                        "major_domain": meta.domain.major_domain if meta and meta.domain else "Number"
                    },
                    "difficulty": {
                        "estimated_level": meta.difficulty.estimated_level if meta and meta.difficulty else 3
                    }
                } if meta else None
            }

            # Delegate to ProblemGenerator from mathesis_core
            result = await self.generator.generate_twin(question_dict, preserve_metadata=True)

            # Extract generated content
            new_stem = result.get("question_stem", "")
            new_answer_key = {
                "answer": result.get("answer", "See solution"),
                "explanation": result.get("solution_steps", "")
            }

            # Create QuestionCreate schema with preserved metadata
            return QuestionCreate(
                question_type=original_question.question_type,
                content_stem=new_stem,
                answer_key=new_answer_key,
                create_by=original_question.created_by,
                content_metadata=QuestionMetadata(
                    source=meta.source if meta else ExamSourceInfo(name="Generated", grade=5),
                    domain=meta.domain if meta else MathDomainInfo(major_domain="Number"),
                    difficulty=meta.difficulty if meta else DifficultyMetrics(),
                    is_twin_generated=True,
                    original_question_id=str(original_question.question_id)
                )
            )

        except GenerationError as e:
            logger.error(f"Twin question generation error: {e}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error in twin generation: {e}")
            raise GenerationError(f"Failed to generate twin question: {str(e)}")


# Singleton instance for backward compatibility
math_advanced_service = MathAdvancedService()
