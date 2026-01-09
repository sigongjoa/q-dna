"""
Error Solution Service for Node 2 (Q-DNA).
Refactored to use mathesis_core.generation.ProblemGenerator.
"""
from typing import List, Optional
from fastapi import HTTPException
from mathesis_core.generation import ProblemGenerator
from mathesis_core.llm.clients import create_ollama_client
from mathesis_core.exceptions import GenerationError
from app.schemas.error_solution import ErrorType
from app.constants.error_types import ERROR_TYPE_DATABASE
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class ErrorSolutionService:
    """
    Service for generating intentionally incorrect solutions for educational purposes.

    This is a thin service layer that:
    1. Delegates core generation logic to ProblemGenerator (from mathesis_core)
    2. Handles FastAPI-specific concerns (error type mapping, HTTP exceptions)
    3. Maintains backward compatibility with existing API
    """

    def __init__(self):
        """Initialize ErrorSolutionService with mathesis_core components."""
        # Create LLM client using mathesis_core
        self.client = create_ollama_client(
            base_url=settings.OLLAMA_URL,
            model=settings.OLLAMA_MODEL
        )

        # Use ProblemGenerator from mathesis_core
        self.generator = ProblemGenerator(self.client)

    async def generate_erroneous_solution(
        self,
        question_content: str,
        correct_answer: str,
        error_types: List[ErrorType] = None,
        difficulty: int = 2
    ) -> dict:
        """
        Generate intentionally incorrect solution using ProblemGenerator.

        This method maintains backward compatibility with the original API.
        Core logic is delegated to mathesis_core.generation.ProblemGenerator.

        Args:
            question_content: Question text
            correct_answer: Correct answer for reference
            error_types: List of ErrorType enums
            difficulty: Solution complexity level (1-5)

        Returns:
            Dict with keys:
                - steps: List of solution steps with error markers
                - final_wrong_answer: The incorrect final answer

        Raises:
            HTTPException: If generation fails
        """
        if not error_types:
            # Default error types if none provided
            error_types = [ErrorType.CONCEPT_MISAPPLICATION, ErrorType.ARITHMETIC_ERROR]

        # Convert ErrorType enums to string values for mathesis_core
        error_type_strings = [et.value for et in error_types]

        # Get descriptions from database for better prompting
        error_descriptions = []
        for et_value in error_type_strings:
            if et_value in ERROR_TYPE_DATABASE:
                error_descriptions.append(ERROR_TYPE_DATABASE[et_value]["description"])
            else:
                error_descriptions.append(et_value)  # Fallback to raw value

        try:
            # Delegate to ProblemGenerator from mathesis_core
            result = await self.generator.generate_error_solution(
                question_content=question_content,
                correct_answer=correct_answer,
                error_types=error_type_strings,
                difficulty=difficulty
            )

            return result

        except GenerationError as e:
            logger.error(f"Error solution generation failed: {e}")
            raise HTTPException(status_code=500, detail=f"LLM Generation Failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in error solution generation: {e}")
            raise HTTPException(status_code=500, detail=f"Generation Failed: {str(e)}")

    async def generate_correct_solution(
        self,
        question_content: str,
        correct_answer: str
    ) -> dict:
        """
        Generate correct model solution using ProblemGenerator.

        This method maintains backward compatibility with the original API.
        Core logic is delegated to mathesis_core.generation.ProblemGenerator.

        Args:
            question_content: Question text
            correct_answer: Correct answer

        Returns:
            Dict with key:
                - steps: List of correct solution steps

        Raises:
            HTTPException: If generation fails
        """
        try:
            # Delegate to ProblemGenerator from mathesis_core
            result = await self.generator.generate_correct_solution(
                question_content=question_content,
                correct_answer=correct_answer
            )

            return result

        except GenerationError as e:
            logger.error(f"Correct solution generation failed: {e}")
            raise HTTPException(status_code=500, detail=f"LLM Generation Failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in correct solution generation: {e}")
            raise HTTPException(status_code=500, detail=f"Generation Failed: {str(e)}")


# Singleton instance for backward compatibility
error_solution_service = ErrorSolutionService()
