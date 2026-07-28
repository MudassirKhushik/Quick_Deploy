import os
from dotenv import load_dotenv
from app.sandbox import create_sandbox_container, clone_repo, run_command, inject_do_token, stop_container, copy_to_container
from app.llm import generate_app_spec

load_dotenv()
DO_TOKEN = os.getenv("DO_API_TOKEN")

def detect_project_type(files: str) -> str:
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

async def run_deployment(repo_url: str, user_prompt: str = "Deploy to DigitalOcean"):
    """Deploy a GitHub repo to DigitalOcean App Platform."""
    
    container_id = None
    try:
        # Step 1: Create sandbox container
        container_id = create_sandbox_container()
        print(f"Container started: {container_id}")
        
        # Step 2: Authenticate with DO
        inject_do_token(container_id, DO_TOKEN)
        
        # Step 3: Clone the repo
        exit_code, output = clone_repo(container_id, repo_url)
        if exit_code != 0:
            stop_container(container_id)
            return {"error": f"Clone failed: {output}", "success": False}
        
        # Step 4: Analyze repo
        exit_code, files = run_command(container_id, "find /workspace/repo -type f | head -50")
        exit_code, package_json = run_command(container_id, "cat /workspace/repo/package.json 2>/dev/null || echo '{}'")
        
        repo_info = f"Files:\n{files}\n\npackage.json:\n{package_json}"
        project_type = detect_project_type(files)
        
        # Step 5: Generate App Spec
        repo_name = extract_repo_name(repo_url)
        owner_repo = extract_owner_repo(repo_url)
        
        app_spec = generate_app_spec(repo_info, user_prompt)
        
        # Replace placeholders with actual values
        app_spec = app_spec.replace("placeholder/repo", owner_repo)
        app_spec = app_spec.replace("sample-nodejs", repo_name)
        
        print(f"App Spec:\n{app_spec}")
        
        # Step 6: Copy spec to container
        copy_to_container(container_id, app_spec, "/workspace/app.yaml")
        
        # Step 7: Verify file
        exit_code, cat_out = run_command(container_id, "cat /workspace/app.yaml")
        print(f"Verification: {cat_out[:200]}")
        
        # Step 8: Deploy
        exit_code, deploy_output = run_command(
            container_id, 
            "doctl apps create --spec /workspace/app.yaml --format URL --no-header 2>&1"
        )
        print(f"Deploy result: {exit_code} - {deploy_output}")
        
        # Step 9: Cleanup
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