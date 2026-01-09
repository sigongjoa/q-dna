import grpc.aio
import logging
import uuid
from mathesis_core.grpc import common_pb2, common_pb2_grpc
from app.services.question_service import question_service
from app.core.database import SessionLocal
from sqlalchemy import select
from app.models.question import Question

logger = logging.getLogger("app")

class Node2ServiceServicer(common_pb2_grpc.MathesisServiceServicer):
    """gRPC Servicer for Node2 (Q-DNA)"""
    
    async def GetQuestion(self, request, context):
        logger.info(f"Node2.GetQuestion called for {request.id}")
        try:
            q_uuid = uuid.UUID(request.id)
            async with SessionLocal() as db:
                stmt = select(Question).where(Question.question_id == q_uuid)
                result = await db.execute(stmt)
                q = result.scalars().first()
                
                if not q:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    return common_pb2.Question()
                
                return common_pb2.Question(
                    id=str(q.question_id),
                    text=q.content_stem,
                    solution=q.answer_key or "",
                    related_concepts=[]
                )
        except Exception as e:
            logger.warning(f"PostgreSQL not available, using simulation for {request.id}")
            return common_pb2.Question(
                id=request.id,
                text="What is the derivative of x^2?",
                solution="2x",
                related_concepts=["Calculus", "Differentiation"]
            )

async def serve_grpc():
    server = grpc.aio.server()
    common_pb2_grpc.add_MathesisServiceServicer_to_server(Node2ServiceServicer(), server)
    listen_addr = "[::]:50052"
    server.add_insecure_port(listen_addr)
    logger.info(f"Node2 gRPC server starting on {listen_addr}")
    await server.start()
    await server.wait_for_termination()
