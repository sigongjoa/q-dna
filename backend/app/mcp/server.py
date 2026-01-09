from mathesis_core.mcp.server import BaseMCPServer
from app.services.ollama_service import ollama_service
from app.services.tagging_service import tagging_service
from app.services.crawler_service import crawler_service
import logging

logger = logging.getLogger("app")

class Node2MCPServer(BaseMCPServer):
    """MCP Server adapter for Node2 (Q-DNA)"""
    def __init__(self):
        super().__init__(name="node2-q-dna", version="1.0.0")

    async def analyze_problem(self, problem_text: str):
        """Analyze a math problem and provide a detailed breakdown."""
        logger.info(f"MCP tool 'analyze_problem' called for: {problem_text[:50]}...")
        prompt = f"Analyze this math problem and explain the solution steps: {problem_text}"
        result = await ollama_service.generate_text(prompt)
        return {"analysis": result}

    async def get_tag_recommendations(self, content: str):
        """Get recommended educational tags for piece of content."""
        logger.info(f"MCP tool 'get_tag_recommendations' called")
        recommendations = await tagging_service.get_tag_recommendations(content)
        return {"recommendations": recommendations}

    async def get_node2_status(self):
        return {"status": "operational", "engine": "Q-DNA"}

    async def list_available_exam_sources(self):
        """List available public exam sources for crawling."""
        logger.info("MCP tool 'list_available_exam_sources' called")
        return {"sources": crawler_service.list_available_sources()}

    async def fetch_public_exams(self, source_id: str, year: str = "2025"):
        """Fetch and download public exams from a specific source."""
        logger.info(f"MCP tool 'fetch_public_exams' called for {source_id} ({year})")
        downloaded = crawler_service.download_exam(source_id, year)
        return {"downloaded_files": downloaded, "status": "success" if downloaded else "failed"}
