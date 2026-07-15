import subprocess
import os
import tempfile

SANDBOX_IMAGE = "deploybot-sandbox"

def run_docker_command(cmd):
    """Run a docker command via subprocess."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        shell=True
    )
    return result.returncode, result.stdout + result.stderr

def create_sandbox_container():
    """Create an ephemeral container and return its ID."""
    exit_code, output = run_docker_command(
        f'docker run -d --rm {SANDBOX_IMAGE} tail -f /dev/null'
    )
    if exit_code != 0:
        raise Exception(f"Failed to create container: {output}")
    return output.strip()

def clone_repo(container_id: str, repo_url: str):
    """Clone a GitHub repo into the sandbox container."""
    exit_code, output = run_docker_command(
        f'docker exec {container_id} git clone {repo_url} /workspace/repo'
    )
    return exit_code, output

def run_command(container_id: str, command: str):
    """Run a command inside the sandbox and return output."""
    exit_code, output = run_docker_command(
        f'docker exec {container_id} {command}'
    )
    return exit_code, output

def inject_do_token(container_id: str, token: str):
    """Inject DO API token into the sandbox."""
    run_command(container_id, "mkdir -p /root/.config")
    run_command(container_id, f"doctl auth init -t {token}")

def copy_to_container(container_id: str, content: str, dest_path: str):
    """Copy a string to a file inside the container using docker cp."""
    # Create a temp file on host
    tmp = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml')
    tmp.write(content)
    tmp.close()
    
    # Copy to container
    exit_code, output = run_docker_command(
        f'docker cp {tmp.name} {container_id}:{dest_path}'
    )
    
    # Clean up
    os.unlink(tmp.name)
    
    return exit_code, output

def stop_container(container_id: str):
    """Stop and remove the container."""
    run_docker_command(f'docker stop {container_id}')