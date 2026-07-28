import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

TEMPLATES = {
    "nodejs": """name: {name}
services:
- name: web
  github:
    repo: {repo}
    branch: main
  build_command: npm install
  run_command: npm start
  http_port: 8080
  instance_count: 1
  instance_size_slug: apps-s-1vcpu-0.5gb
  envs:
  - key: NODE_ENV
    value: production""",
    
    "python": """name: {name}
services:
- name: web
  github:
    repo: {repo}
    branch: main
  build_command: pip install -r requirements.txt
  run_command: uvicorn main:app --host 0.0.0.0 --port 8080
  http_port: 8080
  instance_count: 1
  instance_size_slug: apps-s-1vcpu-0.5gb""",
    
    "static": """name: {name}
static_sites:
- name: site
  github:
    repo: {repo}
    branch: main
  output_dir: /
  index_document: index.html"""
}

def generate_app_spec(repo_files: str, user_prompt: str) -> str:
    """Generate DO App Spec using Gemini AI or fallback to templates."""
    
    # Try Gemini first
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(
            f"""Generate a DigitalOcean App Platform YAML specification.
            
Rules:
- Detect project type from files
- For Node.js: npm install, npm start, port 8080
- For Python: pip install, uvicorn, port 8080
- Include github repo reference
- instance_size_slug: apps-s-1vcpu-0.5gb
- Output ONLY valid YAML, no markdown

Repo files:
{repo_files}

User request: {user_prompt}

Generate app.yaml:"""
        )
        content = response.text.replace("```yaml", "").replace("```", "").strip()
        if "name:" in content and "services:" in content:
            return content
    except Exception as e:
        print(f"Gemini failed, using template: {e}")
    
    # Fallback to templates
    if "package.json" in repo_files:
        return TEMPLATES["nodejs"]
    elif "requirements.txt" in repo_files:
        return TEMPLATES["python"]
    elif "index.html" in repo_files:
        return TEMPLATES["static"]
    else:
        return TEMPLATES["nodejs"]