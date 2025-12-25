import os
import re
import uuid
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from app.core.config import settings
from ollama import AsyncClient

# Use non-interactive backend to prevent GUI errors
matplotlib.use('Agg')

MODEL = "qwen2.5:latest"
STATIC_DIR = os.path.join(os.getcwd(), "backend", "static", "diagrams")

class DiagramService:
    def __init__(self):
        self.client = AsyncClient(host=settings.OLLAMA_BASE_URL)
        if not os.path.exists(STATIC_DIR):
            os.makedirs(STATIC_DIR)

    async def generate_diagram(self, description: str) -> str:
        """
        Generates a geometry diagram based on description.
        Returns the relative URL of the generated image.
        """
        # 1. Generate Code
        code = await self._get_python_code(description)
        
        # 2. Execute Code and Save Image
        filename = f"{uuid.uuid4()}.png"
        filepath = os.path.join(STATIC_DIR, filename)
        
        success = self._execute_and_save(code, filepath)
        
        if success:
            return f"/static/diagrams/{filename}"
        else:
            raise Exception("Failed to generate diagram image")

    async def _get_python_code(self, description: str) -> str:
        prompt = f"""
        You are an expert Math Diagram Generator using Python Matplotlib.
        Your goal is to generate Python code to draw a geometry figure based on the description.

        **Style Guidelines (Strict):**
        1. Use 'black' color for lines, 'k-' or 'k--'.
        2. Set `plt.axis('equal')` to ensure correct proportions.
        3. Remove axes: `plt.axis('off')`.
        4. Label points (A, B, C...) using `plt.text`.
        5. Do NOT use `plt.show()`. Use `plt.savefig(save_path, bbox_inches='tight', dpi=300)`.
        6. Ensure the code is complete and runnable. Import `matplotlib.pyplot as plt` and `numpy as np`.
        7. Assume `save_path` variable is already defined.
        
        **Description:**
        {description}

        **Output:**
        Return ONLY the Python code inside a markdown block (```python ... ```).
        """
        
        try:
            response = await self.client.chat(model=MODEL, messages=[
                {'role': 'system', 'content': 'You are a python coding assistant for math visualization.'},
                {'role': 'user', 'content': prompt}
            ])
            content = response['message']['content']
            
            # Extract code
            match = re.search(r"```python(.*?)```", content, re.DOTALL)
            if match:
                return match.group(1).strip()
            return content # Fallback if no block
        except Exception as e:
            print(f"LLM Generation Error: {e}")
            raise e

    def _execute_and_save(self, code: str, save_path: str) -> bool:
        try:
            # Create a localized scope
            local_scope = {
                "plt": plt,
                "np": np,
                "save_path": save_path
            }
            
            # Clear any existing plots
            plt.clf()
            
            # Execute
            exec(code, {}, local_scope)
            
            return os.path.exists(save_path)
        except Exception as e:
            print(f"Code Execution Error: {e}")
            print(f"Failed Code:\n{code}")
            return False

diagram_service = DiagramService()
