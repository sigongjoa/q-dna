import math
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
import uuid


class AnalyticsService:
    """
    Implements BKT (Bayesian Knowledge Tracing) and IRT (Item Response Theory).
    Now with real database integration.
    """

    async def update_bkt(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        skill_id: str,
        is_correct: bool
    ) -> float:
        """
        Update knowledge state for a user on a specific skill using BKT.

        Args:
            db: Database session
            user_id: Student UUID
            skill_id: Skill path (e.g., "Math.Algebra.Quadratics")
            is_correct: Whether the attempt was correct

        Returns:
            Updated mastery probability (0.0-1.0)
        """
        from app.models.student_mastery import StudentMastery

        # Get or create mastery record
        stmt = select(StudentMastery).where(
            and_(
                StudentMastery.user_id == user_id,
                StudentMastery.skill_id == skill_id
            )
        )
        result = await db.execute(stmt)
        mastery = result.scalars().first()

        if not mastery:
            # Create new record with default BKT parameters
            mastery = StudentMastery(
                user_id=user_id,
                skill_id=skill_id,
                p_mastery=0.1,  # P(L0) - Initial knowledge
                p_transit=0.1,  # P(T) - Learning rate
                p_slip=0.1,     # P(S) - Slip probability
                p_guess=0.2     # P(G) - Guess probability
            )
            db.add(mastery)

        # BKT Update Algorithm
        p_L = mastery.p_mastery
        p_S = mastery.p_slip
        p_G = mastery.p_guess
        p_T = mastery.p_transit

        if is_correct:
            # P(L|Correct) = P(L)*(1-P(S)) / [P(L)*(1-P(S)) + (1-P(L))*P(G)]
            numerator = p_L * (1 - p_S)
            denominator = numerator + (1 - p_L) * p_G
            p_L_given_obs = numerator / denominator if denominator > 0 else p_L
        else:
            # P(L|Incorrect) = P(L)*P(S) / [P(L)*P(S) + (1-P(L))*(1-P(G))]
            numerator = p_L * p_S
            denominator = numerator + (1 - p_L) * (1 - p_G)
            p_L_given_obs = numerator / denominator if denominator > 0 else p_L

        # Update for next step: P(L_next) = P(L|obs) + (1-P(L|obs))*P(T)
        p_L_next = p_L_given_obs + (1 - p_L_given_obs) * p_T

        # Clamp to [0, 1]
        p_L_next = max(0.0, min(1.0, p_L_next))

        # Update record
        mastery.p_mastery = p_L_next
        mastery.attempts_count += 1
        if is_correct:
            mastery.correct_count += 1
        mastery.last_attempt_at = datetime.now()

        db.add(mastery)
        await db.commit()
        await db.refresh(mastery)

        return p_L_next

    async def get_user_mastery_map(
        self,
        db: AsyncSession,
        user_id: uuid.UUID
    ) -> Dict[str, float]:
        """
        Get all skill mastery levels for a user.

        Returns: {"Math.Algebra": 0.85, "Math.Geometry": 0.65, ...}
        """
        from app.models.student_mastery import StudentMastery

        stmt = select(StudentMastery).where(StudentMastery.user_id == user_id)
        result = await db.execute(stmt)
        masteries = result.scalars().all()

        return {m.skill_id: m.p_mastery for m in masteries}

    async def recommend_next_questions(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        target_difficulty: Optional[float] = None
    ) -> List[uuid.UUID]:
        """
        Recommend questions based on student's mastery levels.
        Uses simple IRT-like matching: find questions near student's ability level.

        Args:
            db: Database session
            user_id: Student UUID
            target_difficulty: Override difficulty (0.0-1.0), otherwise auto-calculate

        Returns: List of recommended question IDs
        """
        from app.models.question import Question
        from app.models.student_mastery import StudentMastery

        # Calculate average mastery if no target specified
        if target_difficulty is None:
            mastery_map = await self.get_user_mastery_map(db, user_id)
            if mastery_map:
                avg_mastery = sum(mastery_map.values()) / len(mastery_map)
                # Target slightly above current level (zone of proximal development)
                target_difficulty = min(0.95, avg_mastery + 0.1)
            else:
                target_difficulty = 0.3  # Start easy for new students

        # Find questions near target difficulty
        # In real system, would use more sophisticated IRT matching
        stmt = select(Question).where(
            and_(
                Question.status == "active",
                Question.difficulty_index.between(
                    target_difficulty - 0.15,
                    target_difficulty + 0.15
                )
            )
        ).limit(10)

        result = await db.execute(stmt)
        questions = result.scalars().all()

        return [q.question_id for q in questions]

    def estimate_irt_theta(self, responses: List[Dict]) -> float:
        """
        Simple IRT ability estimation using percent correct.

        In production, use proper IRT estimation (Maximum Likelihood or EAP).

        Args:
            responses: [{"is_correct": bool, "difficulty": float}, ...]

        Returns: Estimated ability theta (-3 to +3 scale)
        """
        if not responses:
            return 0.0

        # Simple approach: convert percent correct to theta scale
        correct_count = sum(1 for r in responses if r.get("is_correct"))
        percent_correct = correct_count / len(responses)

        # Map percent to theta using inverse normal CDF approximation
        # 50% correct ≈ theta=0, 84% ≈ theta=1, 16% ≈ theta=-1
        if percent_correct >= 0.99:
            return 3.0
        elif percent_correct <= 0.01:
            return -3.0
        else:
            # Simple linear approximation
            theta = (percent_correct - 0.5) * 4
            return max(-3.0, min(3.0, theta))


analytics_service = AnalyticsService()

