import asyncio
import re
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings
from ollama import AsyncClient

# Configuration
MODEL = "qwen2.5:latest"  # Using the reliable model we have

async def generate_geometry_code(description: str):
    client = AsyncClient(host=settings.OLLAMA_BASE_URL)
    
    prompt = f"""
    You are an expert Math Diagram Generator using Python Matplotlib.
    Your goal is to generate Python code to draw a geometry figure based on the description.

    **Style Guidelines (Strict):**
    1. Use 'black' color for lines, 'k-' or 'k--'.
    2. Set `plt.axis('equal')` to ensure correct proportions.
    3. Remove axes: `plt.axis('off')`.
    4. Label points (A, B, C...) using `plt.text`.
    5. Do NOT use `plt.show()`. Use `plt.savefig('output_geometry.png', bbox_inches='tight', dpi=300)`.
    6. Ensure the code is complete and runnable. Import `matplotlib.pyplot as plt` and `numpy as np`.
    
    **Description:**
    {description}

    **Output:**
    Return ONLY the Python code inside a markdown block (```python ... ```).
    """

    print(f"🤖 User Request: {description}")
    print("⏳ Generating code via Ollama...")
    
    response = await client.chat(model=MODEL, messages=[
        {'role': 'system', 'content': 'You are a python coding assistant for math visualization.'},
        {'role': 'user', 'content': prompt}
    ])
    
    content = response['message']['content']
    return content

def extract_and_run_code(llm_output: str):
    # Extract python code block
    match = re.search(r"```python(.*?)```", llm_output, re.DOTALL)
    if not match:
        print("❌ No code block found in LLM response.")
        print("Raw response:\n", llm_output)
        return

    code = match.group(1).strip()
    print("\n🖥️  Generated Code:\n" + "-"*40 + "\n" + code + "\n" + "-"*40)
    
    try:
        # Execute the code
        # We need to define a local scope to capture variables if needed, 
        # but for plotting we just care about the side effect (saving file)
        exec(code, {"plt": plt, "np": np})
        print("✅ Code executed successfully.")
        
        if os.path.exists("output_geometry.png"):
            print("🖼️  Image saved to: output_geometry.png")
        else:
            print("⚠️ Code ran but 'output_geometry.png' was not found.")
            
    except Exception as e:
        print(f"❌ Execution Error: {e}")

async def main():
    # Test Case: Standard Exam Problem
    # "Draw a triangle ABC where A=(0, 4), B=(-3, 0), C=(3, 0). Draw its inscribed circle (incircle)."
    description = "Draw a triangle ABC with vertices A(0, 4), B(-3, 0), and C(3, 0). Calculate and draw its inscribed circle (incircle) clearly. Label the vertices."
    
    llm_output = await generate_geometry_code(description)
    extract_and_run_code(llm_output)

if __name__ == "__main__":
    asyncio.run(main())
