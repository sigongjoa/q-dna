#!/usr/bin/env python3
"""
Node 2 (Q-DNA) MCP Server

제공하는 Tool:
1. get_student_mastery - BKT로 학생 숙련도 계산
2. recommend_questions - IRT 기반 문제 추천
3. get_question_dna - 문제 DNA 분석
4. estimate_learning_time - 학습 시간 추정
"""
import asyncio
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# Mock data for testing (replace with actual service calls later)
MOCK_MASTERY = {
    "도함수": 0.45,
    "적분": 0.55,
    "극한": 0.75,
    "미분": 0.65,
    "삼각함수": 0.80
}

server = Server("node2-q-dna")


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """사용 가능한 Tool 목록 반환"""
    return [
        Tool(
            name="get_student_mastery",
            description="BKT 알고리즘으로 학생의 개념별 숙련도를 계산합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {"type": "string", "description": "학생 ID"},
                    "concepts": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "조회할 개념 목록 (없으면 전체)"
                    }
                },
                "required": ["student_id"]
            }
        ),
        Tool(
            name="recommend_questions",
            description="IRT 기반으로 학생 능력에 맞는 문제를 추천합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {"type": "string", "description": "학생 ID"},
                    "concept": {"type": "string", "description": "학습 개념"},
                    "num_questions": {"type": "integer", "description": "추천할 문제 수", "default": 10}
                },
                "required": ["student_id", "concept"]
            }
        ),
        Tool(
            name="get_question_dna",
            description="문제의 DNA 분석 결과를 반환합니다 (난이도, 개념, Bloom 레벨 등).",
            inputSchema={
                "type": "object",
                "properties": {
                    "question_id": {"type": "string", "description": "문제 ID"}
                },
                "required": ["question_id"]
            }
        ),
        Tool(
            name="estimate_learning_time",
            description="특정 개념의 학습 소요 시간을 추정합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {"type": "string", "description": "학생 ID"},
                    "concept": {"type": "string", "description": "학습 개념"},
                    "current_mastery": {"type": "number", "description": "현재 숙련도 (0-1)"}
                },
                "required": ["student_id", "concept"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Tool 호출 처리"""

    if name == "get_student_mastery":
        student_id = arguments["student_id"]
        concepts = arguments.get("concepts", None)

        # TODO: 실제 BKT 계산 서비스 호출
        # from app.services.analytics_service import AnalyticsService
        # mastery = await analytics_service.get_student_mastery(student_id)

        # Mock response
        mastery = MOCK_MASTERY if not concepts else {c: MOCK_MASTERY.get(c, 0.5) for c in concepts}

        result = {
            "student_id": student_id,
            "concept_scores": mastery,
            "timestamp": "2026-01-10T23:45:00"
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False)
        )]

    elif name == "recommend_questions":
        student_id = arguments["student_id"]
        concept = arguments["concept"]
        num_questions = arguments.get("num_questions", 10)

        # TODO: 실제 추천 알고리즘 호출
        # from app.services.question_service import QuestionService
        # questions = await question_service.recommend(student_id, concept, num_questions)

        # Mock response
        questions = [
            {
                "id": f"q_{i}",
                "content": f"문제 {i}: {concept}에 관한 문제",
                "difficulty": "medium" if i % 3 == 0 else "easy",
                "concepts": [concept],
                "bloom_level": "apply"
            }
            for i in range(1, num_questions + 1)
        ]

        result = {
            "student_id": student_id,
            "concept": concept,
            "questions": questions,
            "total": len(questions)
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False)
        )]

    elif name == "get_question_dna":
        question_id = arguments["question_id"]

        # TODO: 실제 Q-DNA 분석 호출
        # from app.services.analytics_service import AnalyticsService
        # dna = await analytics_service.analyze_question_dna(question_id)

        # Mock response
        result = {
            "question_id": question_id,
            "difficulty": 0.65,  # IRT difficulty parameter
            "concepts": ["이차함수", "최댓값", "도함수"],
            "bloom_level": "apply",
            "cognitive_load": "medium",
            "prerequisite_concepts": ["함수", "도함수"],
            "estimated_time_minutes": 5
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False)
        )]

    elif name == "estimate_learning_time":
        student_id = arguments["student_id"]
        concept = arguments["concept"]
        current_mastery = arguments.get("current_mastery", 0.5)

        # TODO: 실제 학습 시간 추정 모델 호출
        # time_estimator = LearningTimeEstimator()
        # estimated_hours = time_estimator.estimate(concept, current_mastery)

        # Mock response (간단한 공식)
        base_hours = {
            "극한": 4, "도함수": 6, "적분": 8,
            "미분": 5, "삼각함수": 3
        }.get(concept, 4)

        adjustment = (1.0 - current_mastery) * 2
        estimated_hours = int(base_hours + adjustment)

        result = {
            "student_id": student_id,
            "concept": concept,
            "current_mastery": current_mastery,
            "estimated_hours": estimated_hours,
            "confidence": 0.75
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False)
        )]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """MCP 서버 시작"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
