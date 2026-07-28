import subprocess
import os
import tempfile

SANDBOX_IMAGE = "deploybot-sandbox"

def run_docker_command(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    return result.returncode, result.stdout + result.stderr

def create_sandbox_container():
    exit_code, output = run_docker_command(f'docker run -d --rm {SANDBOX_IMAGE} tail -f /dev/null')
    if exit_code != 0:
        raise Exception(f"Failed to create container: {output}")
    return output.strip()

def clone_repo(container_id: str, repo_url: str):
    exit_code, output = run_docker_command(f'docker exec {container_id} git clone {repo_url} /workspace/repo')
    return exit_code, output

def run_command(container_id: str, command: str):
    exit_code, output = run_docker_command(f'docker exec {container_id} {command}')
    return exit_code, output

def inject_do_token(container_id: str, token: str):
    run_command(container_id, "mkdir -p /root/.config")
    run_command(container_id, f"doctl auth init -t {token}")

def copy_to_container(container_id: str, content: str, dest_path: str):
    tmp = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml')
    tmp.write(content)
    tmp.close()
    exit_code, output = run_docker_command(f'docker cp {tmp.name} {container_id}:{dest_path}')
    os.unlink(tmp.name)
    return exit_code, output

def stop_container(container_id: str):
    run_docker_command(f'docker stop {container_id}')