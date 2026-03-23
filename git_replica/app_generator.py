"""
Application generation — local templates, no external APIs.
"""

import json
import os
from pathlib import Path
from typing import Optional

from git_replica.code_generator import LocalCodeGenerator


class AppGenerator:
    """Generates applications using templates. No external APIs required."""

    def __init__(self):
        self.templates_dir = Path(__file__).parent / "templates"

    def create_app(self, app_type: str, app_name: str, framework: Optional[str] = None, base_path: str = ".") -> str:
        """Create a new application based on type."""
        app_path = Path(base_path) / app_name
        if app_path.exists():
            raise ValueError(f"Directory {app_path} already exists")
        app_path.mkdir(parents=True)

        if framework is None:
            framework = self._default_framework(app_type)

        dispatch = {
            "web":       self._create_web_app,
            "api":       self._create_api_app,
            "cli":       self._create_cli_app,
            "fullstack": self._create_fullstack_app,
            "react":     self._create_react_app,
            "vue":       self._create_vue_app,
            "django":    self._create_django_app,
            "node":      self._create_node_app,
            "nextjs":    self._create_nextjs_app,
            "go":        self._create_go_app,
        }
        fn = dispatch.get(app_type)
        if fn is None:
            raise ValueError(f"Unknown app type: {app_type}")
        fn(app_path, app_name, framework)
        return str(app_path.absolute())

    def generate_code(self, prompt: str, language: str = "python") -> str:
        """Generate code based on prompt — fully local."""
        return LocalCodeGenerator().generate(prompt, language)

    def _default_framework(self, app_type: str) -> str:
        defaults = {
            "web":       "flask",
            "api":       "fastapi",
            "cli":       "click",
            "fullstack": "flask+react",
            "react":     "vite",
            "vue":       "vite",
            "django":    "django",
            "node":      "express",
            "nextjs":    "nextjs",
            "go":        "stdlib",
        }
        return defaults.get(app_type, "python")

    # ------------------------------------------------------------------
    # Existing types
    # ------------------------------------------------------------------

    def _create_web_app(self, app_path: Path, app_name: str, framework: str):
        if framework == "express":
            self._create_express_app(app_path, app_name)
        else:
            self._create_flask_app(app_path, app_name)

    def _create_api_app(self, app_path: Path, app_name: str, framework: str):
        self._create_fastapi_app(app_path, app_name)

    def _create_cli_app(self, app_path: Path, app_name: str, framework: str):
        self._w(app_path / "cli.py", f'''import click

@click.group()
@click.version_option(version="0.1.0")
def cli():
    """{app_name} - A CLI tool."""
    pass

@cli.command()
@click.argument("name")
def hello(name):
    """Say hello."""
    click.echo(f"Hello, {{name}}!")

if __name__ == "__main__":
    cli()
''')
        self._w(app_path / "requirements.txt", "click>=8.1.0\n")
        self._readme(app_path, app_name, "CLI application", "pip install -r requirements.txt\npython cli.py --help")

    def _create_fullstack_app(self, app_path: Path, app_name: str, framework: str):
        backend = app_path / "backend"
        backend.mkdir()
        self._create_fastapi_app(backend, app_name)
        frontend = app_path / "frontend"
        frontend.mkdir()
        self._w(frontend / "index.html", f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>{app_name}</title></head>
<body><h1>{app_name}</h1><p>Backend: FastAPI (backend/main.py)</p></body></html>
''')
        self._readme(app_path, app_name, "Fullstack application",
                     "cd backend && pip install -r requirements.txt && python main.py")

    # ------------------------------------------------------------------
    # New types
    # ------------------------------------------------------------------

    def _create_react_app(self, app_path: Path, app_name: str, framework: str):
        pkg = {
            "name": app_name, "version": "0.1.0", "private": True,
            "scripts": {"dev": "vite", "build": "vite build", "preview": "vite preview"},
            "dependencies": {"react": "^18.2.0", "react-dom": "^18.2.0"},
            "devDependencies": {"@vitejs/plugin-react": "^4.2.0", "vite": "^5.0.0"},
        }
        self._w(app_path / "package.json", json.dumps(pkg, indent=2) + "\n")
        self._w(app_path / "vite.config.js",
                'import { defineConfig } from "vite";\nimport react from "@vitejs/plugin-react";\n'
                'export default defineConfig({ plugins: [react()] });\n')
        self._w(app_path / "index.html", f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"/><title>{app_name}</title></head>
<body><div id="root"></div><script type="module" src="/src/main.jsx"></script></body></html>
''')
        src = app_path / "src"
        src.mkdir()
        self._w(src / "main.jsx", 'import React from "react";\nimport ReactDOM from "react-dom/client";\n'
                'import App from "./App";\nimport "./index.css";\n'
                'ReactDOM.createRoot(document.getElementById("root")).render(<React.StrictMode><App /></React.StrictMode>);\n')
        self._w(src / "App.jsx", f'import React from "react";\nexport default function App() {{\n'
                f'  return <div><h1>{app_name}</h1><p>Edit src/App.jsx to get started.</p></div>;\n}}\n')
        self._w(src / "index.css", "body { margin: 0; font-family: sans-serif; }\n")
        self._readme(app_path, app_name, "React + Vite app", "npm install\nnpm run dev")

    def _create_vue_app(self, app_path: Path, app_name: str, framework: str):
        pkg = {
            "name": app_name, "version": "0.1.0",
            "scripts": {"dev": "vite", "build": "vite build"},
            "dependencies": {"vue": "^3.3.0"},
            "devDependencies": {"@vitejs/plugin-vue": "^4.5.0", "vite": "^5.0.0"},
        }
        self._w(app_path / "package.json", json.dumps(pkg, indent=2) + "\n")
        self._w(app_path / "vite.config.js",
                'import { defineConfig } from "vite";\nimport vue from "@vitejs/plugin-vue";\n'
                'export default defineConfig({ plugins: [vue()] });\n')
        self._w(app_path / "index.html", f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"/><title>{app_name}</title></head>
<body><div id="app"></div><script type="module" src="/src/main.js"></script></body></html>
''')
        src = app_path / "src"
        src.mkdir()
        self._w(src / "main.js", 'import { createApp } from "vue";\nimport App from "./App.vue";\ncreateApp(App).mount("#app");\n')
        self._w(src / "App.vue", f'<template><div><h1>{app_name}</h1><p>Edit src/App.vue.</p></div></template>\n'
                '<script>\nexport default { name: "App" };\n</script>\n')
        self._readme(app_path, app_name, "Vue 3 + Vite app", "npm install\nnpm run dev")

    def _create_django_app(self, app_path: Path, app_name: str, framework: str):
        safe = app_name.replace("-", "_")
        proj = app_path / safe
        proj.mkdir()
        self._w(proj / "__init__.py", "")
        self._w(proj / "settings.py", f'''from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "django-insecure-changeme"
DEBUG = True
ALLOWED_HOSTS = ["*"]
INSTALLED_APPS = [
    "django.contrib.admin","django.contrib.auth","django.contrib.contenttypes",
    "django.contrib.sessions","django.contrib.messages","django.contrib.staticfiles",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "{safe}.urls"
TEMPLATES = [{{"BACKEND":"django.template.backends.django.DjangoTemplates",
               "DIRS":[],"APP_DIRS":True,
               "OPTIONS":{{"context_processors":[
                   "django.template.context_processors.debug",
                   "django.template.context_processors.request",
                   "django.contrib.auth.context_processors.auth",
                   "django.contrib.messages.context_processors.messages",
               ]}}}}]
DATABASES = {{"default":{{"ENGINE":"django.db.backends.sqlite3","NAME":BASE_DIR/"db.sqlite3"}}}}
STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
''')
        self._w(proj / "urls.py", f'''from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [path("admin/", admin.site.urls), path("", views.home, name="home")]
''')
        self._w(proj / "views.py", 'from django.http import HttpResponse\ndef home(request):\n    return HttpResponse("<h1>Hello from Django!</h1>")\n')
        self._w(app_path / "manage.py", f'''#!/usr/bin/env python
import os, sys
def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{safe}.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
if __name__ == "__main__":
    main()
''')
        self._w(app_path / "requirements.txt", "Django>=4.2.0\n")
        self._readme(app_path, app_name, "Django project",
                     "pip install -r requirements.txt\npython manage.py migrate\npython manage.py runserver")

    def _create_node_app(self, app_path: Path, app_name: str, framework: str):
        pkg = {
            "name": app_name, "version": "1.0.0", "main": "server.js",
            "scripts": {"start": "node server.js", "dev": "nodemon server.js"},
            "dependencies": {"express": "^4.18.0"},
            "devDependencies": {"nodemon": "^3.0.0"},
        }
        self._w(app_path / "package.json", json.dumps(pkg, indent=2) + "\n")
        self._w(app_path / "server.js", f'''const express = require("express");
const app = express();
const port = process.env.PORT || 3000;
app.use(express.json());
app.get("/", (req, res) => res.json({{ message: "Welcome to {app_name}!" }}));
app.get("/api/items", (req, res) => res.json({{ items: [] }}));
app.listen(port, () => console.log(`{app_name} running on http://localhost:${{port}}`));
''')
        routes = app_path / "routes"
        routes.mkdir()
        self._w(routes / "index.js", 'const express = require("express");\nconst router = express.Router();\nrouter.get("/", (req, res) => res.json({ status: "ok" }));\nmodule.exports = router;\n')
        self._readme(app_path, app_name, "Express.js server", "npm install\nnpm start")

    def _create_nextjs_app(self, app_path: Path, app_name: str, framework: str):
        pkg = {
            "name": app_name, "version": "0.1.0", "private": True,
            "scripts": {"dev": "next dev", "build": "next build", "start": "next start"},
            "dependencies": {"next": "^14.0.0", "react": "^18.2.0", "react-dom": "^18.2.0"},
        }
        self._w(app_path / "package.json", json.dumps(pkg, indent=2) + "\n")
        pages = app_path / "pages"
        pages.mkdir()
        api_dir = pages / "api"
        api_dir.mkdir()
        self._w(pages / "index.js", f'export default function Home() {{\n  return <main><h1>{app_name}</h1><p>Edit pages/index.js to get started.</p></main>;\n}}\n')
        self._w(api_dir / "hello.js", 'export default function handler(req, res) {\n  res.status(200).json({ message: "Hello from Next.js API!" });\n}\n')
        self._readme(app_path, app_name, "Next.js app", "npm install\nnpm run dev")

    def _create_go_app(self, app_path: Path, app_name: str, framework: str):
        safe = app_name.replace("-", "_")
        self._w(app_path / "go.mod", f'module {app_name}\n\ngo 1.21\n')
        self._w(app_path / "main.go", f'''package main

import (
\t"encoding/json"
\t"fmt"
\t"log"
\t"net/http"
)

func main() {{
\thttp.HandleFunc("/", homeHandler)
\thttp.HandleFunc("/api/health", healthHandler)
\tfmt.Println("{app_name} running on http://localhost:8080")
\tlog.Fatal(http.ListenAndServe(":8080", nil))
}}

func homeHandler(w http.ResponseWriter, r *http.Request) {{
\tw.Header().Set("Content-Type", "application/json")
\tjson.NewEncoder(w).Encode(map[string]string{{"message": "Welcome to {app_name}!"}})
}}

func healthHandler(w http.ResponseWriter, r *http.Request) {{
\tw.Header().Set("Content-Type", "application/json")
\tjson.NewEncoder(w).Encode(map[string]string{{"status": "ok"}})
}}
''')
        handlers = app_path / "handlers"
        handlers.mkdir()
        self._w(handlers / f"{safe}.go", f'''package handlers

import (
\t"encoding/json"
\t"net/http"
)

type Response struct {{
\tMessage string `json:"message"`
}}

func Index(w http.ResponseWriter, r *http.Request) {{
\tw.Header().Set("Content-Type", "application/json")
\tjson.NewEncoder(w).Encode(Response{{Message: "Handler OK"}})
}}
''')
        models = app_path / "models"
        models.mkdir()
        self._w(models / "model.go", 'package models\n\ntype Item struct {\n\tID   int    `json:"id"`\n\tName string `json:"name"`\n}\n')
        self._readme(app_path, app_name, "Go HTTP server", "go run .")

    # ------------------------------------------------------------------
    # Framework helpers
    # ------------------------------------------------------------------

    def _create_flask_app(self, app_path: Path, app_name: str):
        self._w(app_path / "app.py", f'''from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html", title="Home")

@app.route("/about")
def about():
    return render_template("about.html", title="About")

if __name__ == "__main__":
    app.run(debug=True)
''')
        tmpl = app_path / "templates"
        tmpl.mkdir()
        self._w(tmpl / "base.html", f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>{{{{ title }}}} - {app_name}</title>
<link rel="stylesheet" href="{{{{ url_for("static", filename="style.css") }}}}">
</head><body>
<header><h1>{app_name}</h1>
<nav><a href="/">Home</a> <a href="/about">About</a></nav></header>
<main>{{% block content %}}{{% endblock %}}</main>
</body></html>
''')
        self._w(tmpl / "index.html", f'{{% extends "base.html" %}}\n{{% block content %}}<h2>Welcome to {app_name}</h2>{{% endblock %}}\n')
        self._w(tmpl / "about.html", f'{{% extends "base.html" %}}\n{{% block content %}}<h2>About</h2>{{% endblock %}}\n')
        static = app_path / "static"
        static.mkdir()
        self._w(static / "style.css", "body { font-family: Arial, sans-serif; margin: 0; }\n")
        self._w(app_path / "requirements.txt", "Flask>=2.3.0\n")
        self._readme(app_path, app_name, "Flask web application",
                     "pip install -r requirements.txt\npython app.py")

    def _create_fastapi_app(self, app_path: Path, app_name: str):
        self._w(app_path / "main.py", f'''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="{app_name}")

class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

items: List[Item] = []

@app.get("/")
def read_root():
    return {{"message": "Welcome to {app_name}"}}

@app.get("/items", response_model=List[Item])
def get_items():
    return items

@app.post("/items", response_model=Item)
def create_item(item: Item):
    items.append(item)
    return item

@app.get("/items/{{item_id}}", response_model=Item)
def get_item(item_id: int):
    for item in items:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''')
        self._w(app_path / "requirements.txt", "fastapi>=0.104.0\nuvicorn>=0.24.0\npydantic>=2.0.0\n")
        self._readme(app_path, app_name, "FastAPI REST API",
                     "pip install -r requirements.txt\npython main.py")

    def _create_express_app(self, app_path: Path, app_name: str):
        self._create_node_app(app_path, app_name, "express")

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def _w(self, path: Path, content: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def _readme(self, app_path: Path, app_name: str, description: str, run_cmds: str):
        self._w(app_path / "README.md", f'''# {app_name}

{description} — generated with Git Replica.

## Getting Started

```bash
{run_cmds}
```

## License

MIT
''')
