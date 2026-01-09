import asyncio
import threading
import uvicorn
from app.main import app
from app.grpc.server import serve_grpc
from app.mcp.server import Node2MCPServer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server-runner")

def run_fastapi():
    logger.info("Starting Node2 FastAPI on port 8002")
    uvicorn.run(app, host="0.0.0.0", port=8002)

async def run_mcp():
    logger.info("Starting Node2 MCP Server")
    server = Node2MCPServer()
    pass

async def main():
    api_thread = threading.Thread(target=run_fastapi, daemon=True)
    api_thread.start()

    logger.info("Starting Node2 Services (gRPC + MCP)")
    await asyncio.gather(
        serve_grpc(),
        run_mcp()
    )

if __name__ == "__main__":
    asyncio.run(main())
