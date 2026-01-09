from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.models.attempt import AttemptLog
from app.models.question import Question, QuestionCurriculum
from app.models.curriculum import CurriculumNode
import uuid
from datetime import datetime, timedelta

class AnalyticsService:
    async def get_student_report_data(self, db: AsyncSession, student_id: uuid.UUID):
        # 1. Basic Stats (Total Attempts, Correct Count, Study Time)
        # Note: Time taken is in ms.
        stats_query = select(
            func.count(AttemptLog.log_id).label("total"),
            func.sum(func.cast(AttemptLog.is_correct,  # Cast boolean to integer/numeric if needed depending on DB, but func.count/case is better
                               kind=None) # Simplified: just count correct
            ).label("correct_count"),
             func.sum(AttemptLog.time_taken_ms).label("total_time_ms")
        ).where(AttemptLog.user_id == student_id)
        
        # Correct count proper way
        correct_query = select(func.count(AttemptLog.log_id)).where(
            AttemptLog.user_id == student_id,
            AttemptLog.is_correct == True
        )
        
        total_res = await db.execute(select(func.count(AttemptLog.log_id)).where(AttemptLog.user_id == student_id))
        total_count = total_res.scalar() or 0
        
        correct_res = await db.execute(correct_query)
        correct_count = correct_res.scalar() or 0
        
        time_res = await db.execute(select(func.sum(AttemptLog.time_taken_ms)).where(AttemptLog.user_id == student_id))
        total_time_ms = time_res.scalar() or 0
        
        accuracy = round((correct_count / total_count * 100) if total_count > 0 else 0, 1)
        study_time_min = total_time_ms // 60000
        study_time_str = f"{study_time_min // 60}시간 {study_time_min % 60}분"

        # 2. Weaknesses & Strengths by Curriculum Node
        # Join Attempt -> Question -> QuestionCurriculum -> CurriculumNode
        # Group by Node Name, calculate Avg Score
        
        performance_query = select(
            CurriculumNode.name,
            func.avg(AttemptLog.score).label("avg_score"),
            func.count(AttemptLog.log_id).label("attempt_count")
        ).select_from(AttemptLog)\
        .join(Question, AttemptLog.question_id == Question.question_id)\
        .join(QuestionCurriculum, Question.question_id == QuestionCurriculum.question_id)\
        .join(CurriculumNode, QuestionCurriculum.node_id == CurriculumNode.node_id)\
        .where(AttemptLog.user_id == student_id)\
        .group_by(CurriculumNode.name)\
        .order_by(desc("avg_score"))
        
        perf_res = await db.execute(performance_query)
        performances = perf_res.fetchall()
        
        # performances is list of (name, avg_score, attempt_count)
        # avg_score 100 based (from bulk import)
        
        strengths = []
        weaknesses = []
        
        for p in performances:
            name, score, count = p
            # Logic: Strength > 80%, Weakness < 60%
            if not score: score = 0
            
            if score >= 80:
                strengths.append(f"{name} ({int(score)}%)")
            elif score < 60:
                weaknesses.append({
                    "concept": name,
                    "accuracy": int(score),
                    "root_cause": "기초 개념 부족" # Dummy logic for MVP
                })
        
        # Fallback if no data
        if not strengths and total_count > 0:
            strengths = ["데이터 부족"]
        if not weaknesses and total_count > 0:
            pass # No weaknesses is good

        return {
            "period": f"{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} ~ {datetime.now().strftime('%Y-%m-%d')}",
            "study_time": study_time_str,
            "problem_count": total_count,
            "accuracy": accuracy,
            "strengths": strengths[:3], # Top 3
            "weaknesses": weaknesses[:3], # Top 3
            "predicted_score": f"{min(100, int(accuracy) + 5)} ~ {min(100, int(accuracy) + 10)}", # Dummy AI prediction
            "target_score": 90
        }

    async def get_knowledge_map(self, db: AsyncSession, student_id: uuid.UUID):
        # 1. Get all nodes
        nodes_res = await db.execute(select(CurriculumNode))
        nodes = nodes_res.scalars().all()
        
        # 2. Get scores for all nodes
        scores_query = select(
            QuestionCurriculum.node_id,
            func.avg(AttemptLog.score).label("avg_score")
        ).select_from(AttemptLog)\
        .join(Question, AttemptLog.question_id == Question.question_id)\
        .join(QuestionCurriculum, Question.question_id == QuestionCurriculum.question_id)\
        .where(AttemptLog.user_id == student_id)\
        .group_by(QuestionCurriculum.node_id)
        
        scores_res = await db.execute(scores_query)
        scores_map = {row.node_id: row.avg_score for row in scores_res.fetchall()}
        
        # 3. Build Tree
        # Helper to find children
        def build_node(current_node):
            children = [n for n in nodes if n.path.startswith(current_node.path + ".") and n.path.count(".") == current_node.path.count(".") + 1]
            
            node_data = {
                "name": current_node.name,
                "id": current_node.name, # Use name for ID in sunburst
            }
            
            score = scores_map.get(current_node.node_id, None)
            
            # Color logic based on score
            if score is None:
                color = "#e0e0e0" # Grey (No data)
                score = 0
            elif score >= 90: color = "#4caf50" # Green
            elif score >= 70: color = "#ffeb3b" # Yellow
            else: color = "#f44336" # Red (Low score, including 0)
            
            node_data["color"] = color
            
            if children:
                node_data["children"] = [build_node(child) for child in children]
            else:
                node_data["loc"] = 100 # Leaf node size
                node_data["score"] = int(score)
                
            return node_data

        # Find root (Math)
        root = next((n for n in nodes if n.path == "Math"), None)
        if not root:
             # Fallback if seed didn't work or named differently
             return {"name": "No Data", "children": []}
             
        return build_node(root)
        
    # Alias for compatibility with existing endpoints
    async def get_user_mastery_map(self, db: AsyncSession, user_id: uuid.UUID):
        return await self.get_knowledge_map(db, user_id)

    # Stub for BKT (Bayesian Knowledge Tracing)
    async def update_bkt(self, db: AsyncSession, user_id: uuid.UUID, skill_id: str, is_correct: bool):
        # Simplified: just return 0.5 for now, real implementation would track per-user-skill mastery
        return 0.8 if is_correct else 0.4

    # Stub for Recommendation
    async def recommend_next_questions(self, db: AsyncSession, user_id: uuid.UUID):
        return []

analytics_service = AnalyticsService()
