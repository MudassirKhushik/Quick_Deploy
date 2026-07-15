from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio

from app.agent import run_deployment

app = FastAPI(title="DeployBot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class DeployRequest(BaseModel):
    repo_url: str
    prompt: str = "Deploy this app to DigitalOcean App Platform"

@app.get("/health")
async def health():
    return {"status": "ok", "service": "DeployBot"}

@app.post("/deploy")
async def deploy(request: DeployRequest):
    result = await run_deployment(request.repo_url, request.prompt)
    return result