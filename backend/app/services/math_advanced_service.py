from typing import List, Optional, Dict, Any
import json
import ollama
from uuid import UUID
from app.schemas.question import QuestionMetadata, ExamSourceInfo, MathDomainInfo, DifficultyMetrics, QuestionCreate, Question
from app.core.config import settings

class MathAdvancedService:
    """
    Service for handling Advanced Math specific logic using Ollama LLM.
    """
    
    def __init__(self):
        self.client = ollama.AsyncClient(host=settings.OLLAMA_BASE_URL)
        self.model = settings.OLLAMA_TEXT_MODEL

    async def analyze_question_metadata(self, content_stem: str) -> QuestionMetadata:
        """
        Analyze question text and extract metadata using Ollama (JSON Mode).
        """
        prompt = f"""
        You are an expert Math Curriculum Specialist for Elementary Advanced Math (Korean Market).
        Analyze the following math problem and extract metadata in JSON format.

        target_schema = {{
            "source": {{
                "name": "Exam Name (e.g. KMC, HME, KJMO, Sungkyunkwan)",
                "grade": int (Target Grade 1-6),
                "year": int (Estimate if unknown, default 2024),
                "number": int (Question number if visible, else 1)
            }},
            "domain": {{
                "major_domain": "One of ['Number', 'Geometry', 'Measurement', 'Regularity', 'Data']",
                "advanced_topic": "Specific topic (e.g., Pigeonhole Principle, Congruence, Prime Factorization)"
            }},
            "difficulty": {{
                "estimated_level": int (1-5, where 5 is Olympiad level),
                "required_skills": ["List of 2-3 key cognitive skills"]
            }}
        }}

        Problem Content:
        {content_stem}
        
        Respond ONLY with the JSON object. Do not include markdown formatting or explanations.
        """

        try:
            response = await self.client.chat(model=self.model, messages=[
                {'role': 'system', 'content': 'You are a strict JSON outputting AI.'},
                {'role': 'user', 'content': prompt}
            ], format='json')
            
            raw_json = response['message']['content']
            data = json.loads(raw_json)
            
            # Safe Parsing to Pydantic Model
            return QuestionMetadata(
                source=ExamSourceInfo(**data.get('source', {})),
                domain=MathDomainInfo(**data.get('domain', {})),
                difficulty=DifficultyMetrics(**data.get('difficulty', {}))
            )

        except Exception as e:
            print(f"LLM Analysis Error: {e}")
            # Fallback to default if AI fails
            return QuestionMetadata(
                source=ExamSourceInfo(name="Unknown", grade=5),
                domain=MathDomainInfo(major_domain="Number"),
                difficulty=DifficultyMetrics()
            )

    async def generate_twin_question(self, original_question: Question) -> QuestionCreate:
        """
        Generate a twin question based on the original question logic.
        """
        meta = original_question.content_metadata
        original_text = original_question.content_stem
        
        prompt = f"""
        You are an expert Math Item Writer for Elementary Advanced Math (Olympiad level).
        Your task is to create a "Twin Problem" (Isomorphic Problem) based on the original problem.

        **Rules (Strict):**
        1. **Logic**: Keep the EXACT SAME mathematical logic, formula, and solving steps.
        2. **Variation**: Change the story context (objects, names) and numbers.
        3. **Language**: Output must be in **Natural Korean (한국어)**.
        4. **Format**: Respond ONLY in JSON format.

        Original Problem:
        {original_text}

        Target JSON Structure:
        {{
            "question_stem": "The new problem text...",
            "answer": "The final answer (e.g. '15개')",
            "solution_steps": "Step-by-step explanation of the solution"
        }}
        """
        
        try:
            # Use JSON mode for structure reliability
            response = await self.client.chat(model=self.model, messages=[
                {'role': 'system', 'content': 'You are a professional math content generator. Output valid JSON.'},
                {'role': 'user', 'content': prompt}
            ], format='json')
            
            generated_text = response['message']['content']
            data = json.loads(generated_text)
            
            new_stem = data.get("question_stem", "")
            new_answer_key = {
                "answer": data.get("answer", "See solution"),
                "explanation": data.get("solution_steps", "")
            }

            return QuestionCreate(
                question_type=original_question.question_type,
                content_stem=new_stem,
                answer_key=new_answer_key,
                create_by=original_question.created_by,
                content_metadata=QuestionMetadata(
                    source=meta.source,
                    domain=meta.domain,
                    difficulty=meta.difficulty,
                    is_twin_generated=True,
                    original_question_id=str(original_question.question_id)
                )
            )
            
        except Exception as e:
            print(f"LLM Generation Error: {e}")
            raise e

math_advanced_service = MathAdvancedService()
