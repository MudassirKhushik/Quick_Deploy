import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """Generate a DigitalOcean App Platform YAML spec. Output ONLY valid YAML, no markdown, no backticks.

Rules:
- name: from repo
- services with github repo, branch main
- detect Node.js: build_command npm install, run_command npm start
- detect Python: build_command pip install -r requirements.txt, run_command uvicorn main:app --host 0.0.0.0 --port 8080
- http_port: 8080
- instance_count: 1
- instance_size_slug: apps-s-1vcpu-0.5gb

Example:
name: sample-app
services:
- name: web
  github:
    repo: owner/repo
    branch: main
  build_command: npm install
  run_command: npm start
  http_port: 8080
  instance_count: 1
  instance_size_slug: apps-s-1vcpu-0.5gb"""

def generate_app_spec(repo_files: str, user_prompt: str) -> str:
    """Generate a DO App Spec YAML from repo analysis."""
    
    models_to_try = [
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite", 
        "gemini-1.5-flash",
        "gemini-pro"
    ]
    
    for model_name in models_to_try:
        try:
            print(f"Trying model: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                f"{SYSTEM_PROMPT}\n\nRepo files:\n{repo_files}\n\nUser request: {user_prompt}\n\nGenerate app.yaml:"
            )
            content = response.text
            print(f"Got response from {model_name}")
            
            # Clean up - remove any markdown formatting
            content = content.replace("```yaml", "").replace("```", "").strip()
            return content
            
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            time.sleep(2)
    
    # Fallback if all models fail
    return """name: nodejs-app
services:
- name: web
  github:
    repo: placeholder/repo
    branch: main
  build_command: npm install
  run_command: npm start
  http_port: 8080
  instance_count: 1
  instance_size_slug: apps-s-1vcpu-0.5gb"""