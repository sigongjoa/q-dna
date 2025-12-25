from typing import List, Dict
from app.services.ollama_service import ollama_service


class TaggingService:
    """
    AI-powered tagging service using Ollama LLM.
    Analyzes question content and generates relevant tags.
    """

    async def get_tag_recommendations(self, question_text: str) -> List[Dict]:
        """
        AI Auto-Tagging logic using Ollama LLM.
        Extracts curriculum path, cognitive level, skills, and concepts.

        Returns: List of {"tag": str, "confidence": float, "type": str}
        """
        prompt = f"""Analyze this educational question and generate relevant tags.

Question:
{question_text}

Identify and categorize tags in these types:
1. subject: Main subject area (Math, Science, English, etc.)
2. concept: Specific concepts (Algebra, Geometry, Quadratic Equations, etc.)
3. skill: Required skills (Problem Solving, Critical Thinking, etc.)
4. cognitive_level: Bloom's taxonomy (Remember, Understand, Apply, Analyze, Evaluate, Create)
5. difficulty: Difficulty level (Easy, Medium, Hard)

Return JSON array of tags with confidence scores (0.0-1.0):
{{
    "tags": [
        {{"tag": "Mathematics", "type": "subject", "confidence": 0.99}},
        {{"tag": "Algebra", "type": "concept", "confidence": 0.95}},
        {{"tag": "Apply", "type": "cognitive_level", "confidence": 0.90}}
    ]
}}

Be precise and assign high confidence (>0.9) only to clearly relevant tags."""

        try:
            response = await ollama_service.generate_text(
                prompt=prompt,
                format="json",
                temperature=0.3  # Lower temperature for consistency
            )

            result = await ollama_service.extract_json(response)
            tags = result.get("tags", [])

            # Validate and filter
            valid_tags = []
            for tag_obj in tags:
                if all(k in tag_obj for k in ["tag", "type", "confidence"]):
                    # Ensure confidence is float
                    tag_obj["confidence"] = float(tag_obj["confidence"])
                    valid_tags.append(tag_obj)

            return valid_tags

        except Exception as e:
            print(f"Tagging error: {e}")
            # Fallback to basic keyword matching
            return self._fallback_tagging(question_text)

    async def generate_metadata(self, question_text: str) -> Dict:
        """
        Generate comprehensive metadata using Ollama LLM.

        Returns:
            {
                "cognitive_level": str,
                "difficulty_estimation": float (0.0-1.0),
                "estimated_time_minutes": int,
                "subject_area": str,
                "curriculum_path": str (e.g., "Math.Algebra.Quadratics")
            }
        """
        prompt = f"""Analyze this educational question and provide metadata.

Question:
{question_text}

Return JSON with exact fields:
{{
    "cognitive_level": "one of: Remember|Understand|Apply|Analyze|Evaluate|Create",
    "difficulty_estimation": 0.0-1.0 (0.0=easiest, 1.0=hardest),
    "estimated_time_minutes": integer (realistic time to solve),
    "subject_area": "Math|Science|English|Social Studies|etc",
    "curriculum_path": "Subject.Topic.Subtopic (e.g., Math.Algebra.Quadratics)",
    "requires_calculator": true/false,
    "language": "Korean|English|Mixed"
}}"""

        try:
            response = await ollama_service.generate_text(
                prompt=prompt,
                format="json",
                temperature=0.2
            )

            metadata = await ollama_service.extract_json(response)

            # Set defaults for missing fields
            metadata.setdefault("cognitive_level", "Apply")
            metadata.setdefault("difficulty_estimation", 0.5)
            metadata.setdefault("estimated_time_minutes", 5)
            metadata.setdefault("subject_area", "General")
            metadata.setdefault("curriculum_path", "General.Unknown")
            metadata.setdefault("requires_calculator", False)
            metadata.setdefault("language", "Korean")

            return metadata

        except Exception as e:
            print(f"Metadata generation error: {e}")
            return {
                "cognitive_level": "Apply",
                "difficulty_estimation": 0.5,
                "estimated_time_minutes": 5,
                "subject_area": "General",
                "curriculum_path": "General.Unknown",
                "requires_calculator": False,
                "language": "Korean"
            }

    async def suggest_curriculum_path(self, question_text: str) -> str:
        """
        Suggest ltree curriculum path for the question.

        Returns: String like "Math.Algebra.Quadratics.Factoring"
        """
        prompt = f"""Given this question, suggest the most specific curriculum path in dot notation.

Question: {question_text}

Example paths:
- Math.Algebra.Linear_Equations
- Math.Geometry.Triangles.Pythagorean_Theorem
- Science.Physics.Mechanics.Kinematics
- Math.Calculus.Derivatives.Chain_Rule

Return ONLY the path string, no explanation."""

        try:
            path = await ollama_service.generate_text(
                prompt=prompt,
                temperature=0.1
            )
            # Clean up the response
            path = path.strip().strip('"\'').split('\n')[0]
            return path if '.' in path else "General.Unknown"
        except:
            return "General.Unknown"

    def _fallback_tagging(self, question_text: str) -> List[Dict]:
        """
        Simple keyword-based fallback when AI fails.
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


tagging_service = TaggingService()

