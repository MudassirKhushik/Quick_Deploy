import os
from dotenv import load_dotenv
from app.sandbox import create_sandbox_container, clone_repo, run_command, inject_do_token, stop_container, copy_to_container

load_dotenv()
DO_TOKEN = os.getenv("DO_API_TOKEN")

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

def detect_project_type(files: str, package_json: str) -> str:
    if "package.json" in files:
        return "nodejs"
    elif "requirements.txt" in files or "setup.py" in files or "pyproject.toml" in files:
        return "python"
    elif "index.html" in files:
        return "static"
    return "nodejs"

def extract_repo_name(repo_url: str) -> str:
    return repo_url.rstrip("/").rstrip(".git").split("/")[-1]

def extract_owner_repo(repo_url: str) -> str:
    parts = repo_url.rstrip("/").rstrip(".git").split("/")
    return f"{parts[-2]}/{parts[-1]}"

async def run_deployment(repo_url: str, user_prompt: str):
    container_id = None
    try:
        container_id = create_sandbox_container()
        print(f"Container: {container_id}")
        
        inject_do_token(container_id, DO_TOKEN)
        
        exit_code, output = clone_repo(container_id, repo_url)
        print(f"Clone exit: {exit_code}")
        if exit_code != 0:
            stop_container(container_id)
            return {"error": f"Clone failed: {output}", "success": False}
        
        exit_code, files = run_command(container_id, "find /workspace/repo -type f | head -50")
        exit_code, package_json = run_command(container_id, "cat /workspace/repo/package.json 2>/dev/null || echo '{}'")
        
        project_type = detect_project_type(files, package_json)
        print(f"Detected: {project_type}")
        
        repo_name = extract_repo_name(repo_url)
        owner_repo = extract_owner_repo(repo_url)
        
        app_spec = TEMPLATES[project_type].format(name=repo_name, repo=owner_repo)
        print(f"Spec generated")
        
        # Use docker cp to copy file (no escaping issues!)
        copy_to_container(container_id, app_spec, "/workspace/app.yaml")
        
        # Verify
        exit_code, cat_out = run_command(container_id, "cat /workspace/app.yaml")
        print(f"Verification:\n{cat_out[:300]}")
        
        # Deploy
        exit_code, deploy_output = run_command(container_id, "doctl apps create --spec /workspace/app.yaml --format URL --no-header 2>&1")
        print(f"Deploy exit: {exit_code}, output: {deploy_output[:300]}")
        
        stop_container(container_id)
        
        return {
            "project_type": project_type,
            "app_spec": app_spec,
            "deploy_output": deploy_output.strip(),
            "live_url": deploy_output.strip() if exit_code == 0 else None,
            "success": exit_code == 0
        }
    
    except Exception as e:
        if container_id:
            try:
                stop_container(container_id)
            except:
                pass
        return {"error": str(e), "success": False}