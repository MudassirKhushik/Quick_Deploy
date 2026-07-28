# 🚀 Quick Deploy - AI-Powered Deployment Agent

An AI agent that automatically deploys GitHub repositories to DigitalOcean App Platform with a single command. Built as a portfolio project demonstrating AI integration, cloud DevOps, and full-stack engineering.

## ✨ Features

- 🤖 **AI-Powered** - Uses Google Gemini to analyze repos and generate deployment configs
- 🐳 **Sandboxed** - All deployments run in isolated Docker containers
- ⚡ **One-Command Deploy** - Paste a GitHub URL, get a live app
- 🔍 **Auto-Detection** - Identifies Node.js, Python, or static sites
- 📦 **Template Fallback** - Works even without AI (pre-built templates)

## 🏗️ Architecture
User Request (GitHub URL)
│
▼
┌──────────────────┐
│ FastAPI Server │ ← Main backend
└────────┬─────────┘
│
▼
┌──────────────────┐
│ AI Agent │ ← Gemini LLM + Templates
└────────┬─────────┘
│
▼
┌──────────────────┐
│ Docker Sandbox │ ← Isolated container
│ ├── Clone Repo │
│ ├── Generate YAML│
│ └── doctl deploy │
└────────┬─────────┘
│
▼
┌──────────────────┐
│ DigitalOcean │
│ App Platform │ ← Live deployed app
└──────────────────┘


## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, Uvicorn
- **AI**: Google Gemini 2.0 Flash
- **Sandbox**: Docker, Ubuntu
- **Deployment**: DigitalOcean App Platform, doctl
- **Language Detection**: File analysis (package.json, requirements.txt)

## 📋 Prerequisites

1. **Docker Desktop** - [Install](https://docs.docker.com/get-docker/)
2. **DigitalOcean Account** - [Sign Up](https://m.do.co/c/your-referral) ($200 free credit for new users)
3. **GitHub linked to DO** - Authorize at [DO Apps](https://cloud.digitalocean.com/apps)
4. **DO API Token** - Generate at [API Tokens](https://cloud.digitalocean.com/account/api/tokens)
5. **Gemini API Key** - Get from [Google AI Studio](https://aistudio.google.com/app/apikey) (Free)

## 🚀 Installation

```bash
# 1. Clone the repo
git clone https://github.com/MudassirKhushik/Quick_Deploy.git
cd Quick_Deploy

# 2. Set up Python environment
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your DO_API_TOKEN and GEMINI_API_KEY

# 5. Build sandbox Docker image
cd ..
docker build -t deploybot-sandbox sandbox/

# 6. Start the server
cd backend
uvicorn app.main:app --reload