"""
Prometheus — Ultimate Full-Stack Development Platform
FastAPI backend — single file, all endpoints functional.
"""

import asyncio
import json
import os
import shutil
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import git
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# git_replica imports
# ---------------------------------------------------------------------------
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from git_replica.code_generator import LocalCodeGenerator
from git_replica.completer import CompletionEngine
from git_replica.app_generator import AppGenerator
from git_replica.runner import AppRunner

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Prometheus Dev Platform",
    description="The Ultimate Full-Stack Development Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

DATA_DIR = Path.home() / ".prometheus"
PROJECTS_FILE = DATA_DIR / "projects.json"
PROJECTS_DIR = DATA_DIR / "projects"

DATA_DIR.mkdir(exist_ok=True)
PROJECTS_DIR.mkdir(exist_ok=True)

if not PROJECTS_FILE.exists():
    PROJECTS_FILE.write_text("[]")


def load_projects() -> List[Dict]:
    try:
        return json.loads(PROJECTS_FILE.read_text())
    except Exception:
        return []


def save_projects(projects: List[Dict]):
    PROJECTS_FILE.write_text(json.dumps(projects, indent=2))


def get_project(project_id: str) -> Dict:
    for p in load_projects():
        if p["id"] == project_id:
            return p
    raise HTTPException(status_code=404, detail=f"Project {project_id} not found")


def project_dir(project_id: str) -> Path:
    d = PROJECTS_DIR / project_id
    d.mkdir(parents=True, exist_ok=True)
    return d


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    framework: str = "fastapi"
    app_type: str = "api"


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    framework: Optional[str] = None
    status: Optional[str] = None


class FileWrite(BaseModel):
    content: str
    encoding: str = "utf-8"


class GenerateRequest(BaseModel):
    prompt: str
    language: str = "python"
    project_id: Optional[str] = None


class CompleteRequest(BaseModel):
    code: str
    language: str = "python"
    line: int = 0


class ScaffoldRequest(BaseModel):
    prompt: str = ""
    app_type: str = "api"
    app_name: str = "my-app"
    framework: Optional[str] = None
    project_id: Optional[str] = None


class DocstringRequest(BaseModel):
    code: str
    language: str = "python"


class TypesRequest(BaseModel):
    code: str
    language: str = "python"


class ImportsRequest(BaseModel):
    code: str
    language: str = "python"


class ExecRequest(BaseModel):
    command: str
    timeout: int = 30


class GitCommitRequest(BaseModel):
    message: str
    files: List[str] = []


class GitDiffRequest(BaseModel):
    ref: str = "HEAD"


class PackageInstallRequest(BaseModel):
    packages: List[str]
    manager: str = "pip"


class DeployConfig(BaseModel):
    port: int = 8000
    env_vars: Dict[str, str] = {}


# ---------------------------------------------------------------------------
# Health / stats
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "prometheus", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/stats")
def stats():
    projects = load_projects()
    running = sum(1 for p in projects if p.get("status") == "running")
    total_files = 0
    for p in projects:
        pd = PROJECTS_DIR / p["id"]
        if pd.exists():
            total_files += sum(1 for f in pd.rglob("*") if f.is_file())
    return {
        "projects": len(projects),
        "running": running,
        "total_files": total_files,
        "frameworks_supported": 10,
        "languages_supported": 8,
        "snippets_available": 500,
    }


# ---------------------------------------------------------------------------
# Projects CRUD
# ---------------------------------------------------------------------------

@app.get("/api/projects")
def list_projects():
    return load_projects()


@app.post("/api/projects", status_code=201)
def create_project(body: ProjectCreate):
    project_id = str(uuid.uuid4())[:8]
    now = datetime.now(timezone.utc).isoformat()
    project = {
        "id": project_id,
        "name": body.name,
        "description": body.description,
        "framework": body.framework,
        "app_type": body.app_type,
        "status": "stopped",
        "created_at": now,
        "updated_at": now,
    }
    # Scaffold files
    pd = project_dir(project_id)
    try:
        gen = AppGenerator()
        gen.create_app(body.app_type, body.name, body.framework, str(pd))
        # Move scaffolded files from pd/name to pd
        inner = pd / body.name
        if inner.exists():
            for item in inner.iterdir():
                dest = pd / item.name
                if not dest.exists():
                    shutil.move(str(item), str(dest))
            shutil.rmtree(str(inner), ignore_errors=True)
    except Exception:
        # Fallback: create a basic README
        (pd / "README.md").write_text(f"# {body.name}\n\n{body.description}\n")

    projects = load_projects()
    projects.append(project)
    save_projects(projects)
    return project


@app.get("/api/projects/{project_id}")
def get_project_detail(project_id: str):
    return get_project(project_id)


@app.put("/api/projects/{project_id}")
def update_project(project_id: str, body: ProjectUpdate):
    projects = load_projects()
    for p in projects:
        if p["id"] == project_id:
            if body.name is not None:
                p["name"] = body.name
            if body.description is not None:
                p["description"] = body.description
            if body.framework is not None:
                p["framework"] = body.framework
            if body.status is not None:
                p["status"] = body.status
            p["updated_at"] = datetime.now(timezone.utc).isoformat()
            save_projects(projects)
            return p
    raise HTTPException(status_code=404, detail="Project not found")


@app.delete("/api/projects/{project_id}", status_code=204)
def delete_project(project_id: str):
    projects = load_projects()
    orig = len(projects)
    projects = [p for p in projects if p["id"] != project_id]
    if len(projects) == orig:
        raise HTTPException(status_code=404, detail="Project not found")
    save_projects(projects)
    pd = PROJECTS_DIR / project_id
    if pd.exists():
        shutil.rmtree(str(pd))


# ---------------------------------------------------------------------------
# File management
# ---------------------------------------------------------------------------

def _file_tree(directory: Path, base: Path) -> List[Dict]:
    items = []
    try:
        entries = sorted(directory.iterdir(), key=lambda p: (p.is_file(), p.name))
        for item in entries:
            rel = str(item.relative_to(base))
            if item.is_dir():
                items.append({
                    "name": item.name,
                    "path": rel,
                    "type": "directory",
                    "children": _file_tree(item, base),
                })
            else:
                items.append({
                    "name": item.name,
                    "path": rel,
                    "type": "file",
                    "size": item.stat().st_size,
                })
    except PermissionError:
        pass
    return items


@app.get("/api/projects/{project_id}/files")
def list_files(project_id: str):
    get_project(project_id)
    pd = project_dir(project_id)
    return {"tree": _file_tree(pd, pd), "root": str(pd)}


@app.get("/api/projects/{project_id}/files/{file_path:path}")
def read_file(project_id: str, file_path: str):
    get_project(project_id)
    pd = project_dir(project_id)
    fp = (pd / file_path).resolve()
    if not str(fp).startswith(str(pd)):
        raise HTTPException(status_code=400, detail="Path traversal not allowed")
    if not fp.exists():
        raise HTTPException(status_code=404, detail="File not found")
    if fp.is_dir():
        raise HTTPException(status_code=400, detail="Path is a directory")
    try:
        content = fp.read_text(errors="replace")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"path": file_path, "content": content, "size": fp.stat().st_size}


@app.post("/api/projects/{project_id}/files/{file_path:path}", status_code=201)
def create_file(project_id: str, file_path: str, body: FileWrite):
    get_project(project_id)
    pd = project_dir(project_id)
    fp = (pd / file_path).resolve()
    if not str(fp).startswith(str(pd)):
        raise HTTPException(status_code=400, detail="Path traversal not allowed")
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(body.content, encoding=body.encoding)
    return {"path": file_path, "size": fp.stat().st_size, "created": True}


@app.put("/api/projects/{project_id}/files/{file_path:path}")
def update_file(project_id: str, file_path: str, body: FileWrite):
    get_project(project_id)
    pd = project_dir(project_id)
    fp = (pd / file_path).resolve()
    if not str(fp).startswith(str(pd)):
        raise HTTPException(status_code=400, detail="Path traversal not allowed")
    if not fp.exists():
        fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(body.content, encoding=body.encoding)
    return {"path": file_path, "size": fp.stat().st_size, "updated": True}


@app.delete("/api/projects/{project_id}/files/{file_path:path}", status_code=204)
def delete_file(project_id: str, file_path: str):
    get_project(project_id)
    pd = project_dir(project_id)
    fp = (pd / file_path).resolve()
    if not str(fp).startswith(str(pd)):
        raise HTTPException(status_code=400, detail="Path traversal not allowed")
    if not fp.exists():
        raise HTTPException(status_code=404, detail="File not found")
    if fp.is_file():
        fp.unlink()
    else:
        shutil.rmtree(str(fp))


# ---------------------------------------------------------------------------
# Code generation
# ---------------------------------------------------------------------------

@app.post("/api/generate")
def generate_code(body: GenerateRequest):
    gen = LocalCodeGenerator()
    code = gen.generate(body.prompt, body.language)
    return {"code": code, "language": body.language, "prompt": body.prompt}


@app.post("/api/complete")
def complete_code(body: CompleteRequest):
    engine = CompletionEngine()
    lines = body.code.splitlines()
    cursor_line = min(body.line, len(lines) - 1) if lines else 0
    code_before = "\n".join(lines[:cursor_line + 1])
    current_line = lines[cursor_line] if lines else ""
    completions = engine.complete(code_before, body.language)
    return {
        "completions": [
            {"label": c.label, "insert_text": c.insert_text, "kind": c.kind, "detail": c.detail}
            for c in completions[:20]
        ]
    }


@app.post("/api/scaffold")
def scaffold_app(body: ScaffoldRequest):
    gen = AppGenerator()
    base = str(PROJECTS_DIR / (body.project_id or "scaffold_tmp"))
    Path(base).mkdir(parents=True, exist_ok=True)
    app_path = Path(base) / body.app_name
    if app_path.exists():
        shutil.rmtree(app_path)
    try:
        path = gen.create_app(body.app_type, body.app_name, body.framework, base)
        files = []
        pd = Path(path)
        for f in pd.rglob("*"):
            if f.is_file():
                files.append(str(f.relative_to(pd)))
        return {"path": path, "files": files, "app_type": body.app_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate/docstring")
def generate_docstring(body: DocstringRequest):
    gen = LocalCodeGenerator()
    prompt = f"Generate a docstring for this {body.language} code:\n{body.code}"
    result = gen.generate(prompt, body.language)
    return {"docstring": result}


@app.post("/api/generate/types")
def generate_types(body: TypesRequest):
    gen = LocalCodeGenerator()
    prompt = f"Add type hints to this {body.language} code:\n{body.code}"
    result = gen.generate(prompt, body.language)
    return {"typed_code": result}


@app.post("/api/generate/imports")
def generate_imports(body: ImportsRequest):
    engine = CompletionEngine()
    suggestions = engine.suggest_imports(body.code)
    return {"imports": suggestions}


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

TEMPLATES = [
    {"id": "fastapi", "name": "FastAPI REST API", "type": "api", "framework": "fastapi",
     "description": "Production-ready REST API with FastAPI and Pydantic v2", "language": "python"},
    {"id": "flask", "name": "Flask Web App", "type": "web", "framework": "flask",
     "description": "Classic Flask web application with templates", "language": "python"},
    {"id": "react", "name": "React + Vite", "type": "react", "framework": "vite",
     "description": "Modern React 18 app with Vite bundler", "language": "javascript"},
    {"id": "vue", "name": "Vue 3 + Vite", "type": "vue", "framework": "vite",
     "description": "Vue 3 Composition API with Vite", "language": "javascript"},
    {"id": "django", "name": "Django Project", "type": "django", "framework": "django",
     "description": "Full Django project with ORM and admin", "language": "python"},
    {"id": "node", "name": "Express.js API", "type": "node", "framework": "express",
     "description": "Node.js REST API with Express 4", "language": "javascript"},
    {"id": "nextjs", "name": "Next.js App", "type": "nextjs", "framework": "nextjs",
     "description": "Full-stack Next.js 14 with App Router", "language": "javascript"},
    {"id": "go", "name": "Go HTTP Server", "type": "go", "framework": "stdlib",
     "description": "Go HTTP server with standard library", "language": "go"},
    {"id": "cli", "name": "CLI Tool", "type": "cli", "framework": "click",
     "description": "Python CLI with Click and Rich", "language": "python"},
    {"id": "fullstack", "name": "Fullstack App", "type": "fullstack", "framework": "flask+react",
     "description": "FastAPI backend + React frontend", "language": "python"},
]


@app.get("/api/templates")
def list_templates():
    return TEMPLATES


# ---------------------------------------------------------------------------
# Terminal / execution
# ---------------------------------------------------------------------------

def _run_command(command: str, cwd: str, timeout: int = 30) -> Dict[str, Any]:
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "success": result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Command timed out", "returncode": -1, "success": False}
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "returncode": -1, "success": False}


@app.post("/api/projects/{project_id}/run")
def run_project(project_id: str):
    project = get_project(project_id)
    pd = project_dir(project_id)
    runner = AppRunner()
    detected = runner.detect(str(pd))
    if not detected:
        return {"output": "Could not detect how to run this project.", "success": False}
    fname, cmd = detected
    result = _run_command(cmd, str(pd), timeout=10)
    # Update status
    projects = load_projects()
    for p in projects:
        if p["id"] == project_id:
            p["status"] = "running" if result["success"] else "error"
            p["updated_at"] = datetime.now(timezone.utc).isoformat()
    save_projects(projects)
    return {
        "command": cmd,
        "output": result["stdout"] + result["stderr"],
        "returncode": result["returncode"],
        "success": result["success"],
    }


@app.post("/api/projects/{project_id}/exec")
def exec_command(project_id: str, body: ExecRequest):
    get_project(project_id)
    pd = project_dir(project_id)
    result = _run_command(body.command, str(pd), timeout=body.timeout)
    return {
        "command": body.command,
        "output": result["stdout"] + result["stderr"],
        "returncode": result["returncode"],
        "success": result["success"],
    }


# ---------------------------------------------------------------------------
# Git
# ---------------------------------------------------------------------------

@app.post("/api/projects/{project_id}/git/init")
def git_init(project_id: str):
    get_project(project_id)
    pd = project_dir(project_id)
    try:
        repo = git.Repo.init(str(pd))
        return {"message": "Git repository initialized", "path": str(pd)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/projects/{project_id}/git/commit")
def git_commit(project_id: str, body: GitCommitRequest):
    get_project(project_id)
    pd = project_dir(project_id)
    try:
        repo = git.Repo(str(pd))
        if body.files:
            repo.index.add(body.files)
        else:
            repo.git.add(A=True)
        commit = repo.index.commit(body.message)
        return {"sha": commit.hexsha, "message": body.message}
    except git.exc.InvalidGitRepositoryError:
        raise HTTPException(status_code=400, detail="Not a git repository. Run git/init first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/git/log")
def git_log(project_id: str):
    get_project(project_id)
    pd = project_dir(project_id)
    try:
        repo = git.Repo(str(pd))
        commits = []
        for c in list(repo.iter_commits())[:20]:
            commits.append({
                "sha": c.hexsha[:8],
                "message": c.message.strip(),
                "author": str(c.author),
                "date": c.committed_datetime.isoformat(),
            })
        return {"commits": commits}
    except git.exc.InvalidGitRepositoryError:
        return {"commits": [], "error": "Not a git repository"}
    except Exception as e:
        return {"commits": [], "error": str(e)}


@app.post("/api/projects/{project_id}/git/diff")
def git_diff(project_id: str, body: GitDiffRequest):
    get_project(project_id)
    pd = project_dir(project_id)
    try:
        repo = git.Repo(str(pd))
        diff = repo.git.diff(body.ref)
        return {"diff": diff}
    except Exception as e:
        return {"diff": "", "error": str(e)}


# ---------------------------------------------------------------------------
# Package management
# ---------------------------------------------------------------------------

@app.post("/api/projects/{project_id}/packages/install")
def install_packages(project_id: str, body: PackageInstallRequest):
    get_project(project_id)
    pd = project_dir(project_id)
    packages_str = " ".join(body.packages)
    if body.manager == "pip":
        cmd = f"pip install {packages_str}"
    elif body.manager == "npm":
        cmd = f"npm install {packages_str}"
    elif body.manager == "yarn":
        cmd = f"yarn add {packages_str}"
    else:
        raise HTTPException(status_code=400, detail=f"Unknown package manager: {body.manager}")
    result = _run_command(cmd, str(pd), timeout=120)
    return {
        "packages": body.packages,
        "manager": body.manager,
        "output": result["stdout"] + result["stderr"],
        "success": result["success"],
    }


# ---------------------------------------------------------------------------
# Deploy
# ---------------------------------------------------------------------------

@app.post("/api/projects/{project_id}/deploy")
def create_deploy(project_id: str, body: DeployConfig = Body(default=DeployConfig())):
    project = get_project(project_id)
    pd = project_dir(project_id)

    has_req = (pd / "requirements.txt").exists()
    has_pkg = (pd / "package.json").exists()
    has_go = (pd / "go.mod").exists()

    if has_req:
        dockerfile = f"""FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE {body.port}
CMD ["python", "main.py"]
"""
    elif has_pkg:
        dockerfile = f"""FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE {body.port}
CMD ["npm", "start"]
"""
    elif has_go:
        dockerfile = f"""FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod go.sum* ./
RUN go mod download
COPY . .
RUN go build -o server .
FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/server .
EXPOSE {body.port}
CMD ["./server"]
"""
    else:
        dockerfile = f"""FROM ubuntu:22.04
WORKDIR /app
COPY . .
EXPOSE {body.port}
CMD ["bash", "start.sh"]
"""

    env_lines = "\n".join(f"      - {k}={v}" for k, v in body.env_vars.items())
    compose = f"""version: "3.9"
services:
  {project["name"].lower().replace(" ", "-")}:
    build: .
    ports:
      - "{body.port}:{body.port}"
    restart: unless-stopped
    environment:
{env_lines if env_lines else "      - PORT=" + str(body.port)}
"""
    (pd / "Dockerfile").write_text(dockerfile)
    (pd / "docker-compose.yml").write_text(compose)

    return {
        "dockerfile": dockerfile,
        "docker_compose": compose,
        "port": body.port,
        "files_created": ["Dockerfile", "docker-compose.yml"],
    }


@app.get("/api/projects/{project_id}/deploy")
def get_deploy(project_id: str):
    get_project(project_id)
    pd = project_dir(project_id)
    dockerfile = ""
    compose = ""
    if (pd / "Dockerfile").exists():
        dockerfile = (pd / "Dockerfile").read_text()
    if (pd / "docker-compose.yml").exists():
        compose = (pd / "docker-compose.yml").read_text()
    return {
        "has_dockerfile": bool(dockerfile),
        "has_compose": bool(compose),
        "dockerfile": dockerfile,
        "docker_compose": compose,
    }


# ---------------------------------------------------------------------------
# WebSocket — streaming generation
# ---------------------------------------------------------------------------

@app.websocket("/ws/generate")
async def ws_generate(websocket: WebSocket):
    await websocket.accept()
    gen = LocalCodeGenerator()
    try:
        while True:
            data = await websocket.receive_json()
            prompt = data.get("prompt", "")
            language = data.get("language", "python")
            project_id = data.get("project_id")

            if not prompt:
                await websocket.send_json({"error": "No prompt provided"})
                continue

            await websocket.send_json({"status": "generating", "message": f"Generating {language} code…"})
            await asyncio.sleep(0.05)

            code = gen.generate(prompt, language)

            # Stream word by word
            words = code.split()
            buffer = ""
            for i, word in enumerate(words):
                buffer += word + (" " if i < len(words) - 1 else "")
                if (i + 1) % 8 == 0 or i == len(words) - 1:
                    await websocket.send_json({"type": "chunk", "content": buffer})
                    buffer = ""
                    await asyncio.sleep(0.01)

            # If project_id given, save as generated file
            saved_files = []
            if project_id:
                pd = project_dir(project_id)
                ext_map = {
                    "python": "py", "javascript": "js", "typescript": "ts",
                    "go": "go", "rust": "rs", "bash": "sh",
                }
                ext = ext_map.get(language, "txt")
                fname = f"generated_{uuid.uuid4().hex[:6]}.{ext}"
                (pd / fname).write_text(code)
                saved_files.append(fname)

            await websocket.send_json({
                "type": "done",
                "code": code,
                "language": language,
                "saved_files": saved_files,
            })
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"error": str(e)})
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
