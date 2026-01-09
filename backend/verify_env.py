import sys
import os
import requests
import asyncio
import json

def check_step(name, status, details=""):
    symbol = "✅" if status else "❌"
    print(f"{symbol} [{name}]: {details}")
    return status

async def verify_environment():
    print("🚀 Verifying Environment for PDF & AI Features...\n")
    all_passed = True

    # 1. Check WeasyPrint & GTK
    try:
        from weasyprint import HTML
        from weasyprint.text.fonts import FontConfiguration
        
        # Test PDF Generation
        html = "<h1>Test PDF</h1><p>If you can read this, WeasyPrint is working.</p>"
        pdf_bytes = HTML(string=html).write_pdf()
        
        # Save check
        with open("test_output.pdf", "wb") as f:
            f.write(pdf_bytes)
            
        check_step("PDF Generation (WeasyPrint)", True, "Successfully generated test_output.pdf")
        
        # Clean up
        if os.path.exists("test_output.pdf"):
            os.remove("test_output.pdf")
            
    except ImportError:
        check_step("PDF Generation (WeasyPrint)", False, "Library not installed")
        all_passed = False
    except OSError as e:
        if "library not found" in str(e).lower() or "dll" in str(e).lower():
            check_step("PDF Generation (WeasyPrint)", False, f"GTK3 libraries likely missing everywhere. Error: {e}")
            print("  👉 solution: Download GTK3 installer for Windows (https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer)")
        else:
            check_step("PDF Generation (WeasyPrint)", False, f"Error: {e}")
        all_passed = False
    except Exception as e:
        check_step("PDF Generation (WeasyPrint)", False, f"Unexpected error: {e}")
        all_passed = False

    # 2. Check Ollama Connection
    ollama_url = "http://localhost:11434"
    try:
        resp = requests.get(f"{ollama_url}/api/tags", timeout=2)
        if resp.status_code == 200:
            models = resp.json().get('models', [])
            model_names = [m['name'] for m in models]
            
            check_step("Ollama Connection", True, f"Connected. Found {len(models)} models.")
            
            # Check for specific model
            target_model = "qwen2.5:latest" 
            # Note: exact match might fail if tag is slightly different, check general presence
            has_model = any("qwen2.5" in m for m in model_names)
            
            if has_model:
                check_step("AI Model (qwen2.5)", True, "Model found.")
            else:
                check_step("AI Model (qwen2.5)", False, f"Model 'qwen2.5' not found. Found: {model_names}")
                print(f"  👉 command: ollama pull qwen2.5")
                all_passed = False
        else:
            check_step("Ollama Connection", False, f"Status Code: {resp.status_code}")
            all_passed = False
            
    except requests.exceptions.ConnectionError:
        check_step("Ollama Connection", False, "Could not connect to localhost:11434. Is Ollama running?")
        all_passed = False
    except Exception as e:
        check_step("Ollama Connection", False, f"Error: {e}")
        all_passed = False

    print("\n---------------------------------------------------")
    if all_passed:
        print("🎉 All Systems Go! The feature should work perfectly.")
    else:
        print("⚠️ Some checks failed. Please address the issues above.")

if __name__ == "__main__":
    asyncio.run(verify_environment())
