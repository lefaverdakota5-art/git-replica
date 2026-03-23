"""CLI interface for Git Replica — powered by Rich."""

import os
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.syntax import Syntax

from git_replica.repo_manager import RepoManager
from git_replica.app_generator import AppGenerator
from git_replica.code_generator import LocalCodeGenerator
from git_replica.completer import CompletionEngine
from git_replica.runner import AppRunner

console = Console()

APP_TYPES = ["web", "api", "cli", "fullstack", "react", "vue", "django", "node", "nextjs", "go"]


@click.group()
@click.version_option(version="0.2.0")
def main():
    """Git Replica — Personal GitHub & Copilot for making apps."""
    pass


@main.command()
@click.argument("repo_name")
@click.option("--path", default=".", help="Path where to create the repository")
@click.option("--description", default="", help="Repository description")
def init(repo_name: str, path: str, description: str):
    """Initialize a new Git repository."""
    manager = RepoManager()
    try:
        repo_path = manager.create_repo(repo_name, path, description)
    except Exception as e:
        console.print(f"[bold red]✗ Error:[/bold red] {e}")
        raise SystemExit(1)
    console.print(Panel(
        f"[bold green]✓ Repository created![/bold green]\n[cyan]Path:[/cyan] {repo_path}",
        title="[bold red]Git Replica — Init[/bold red]", border_style="red",
    ))


@main.command()
@click.argument("app_type", type=click.Choice(APP_TYPES))
@click.argument("app_name")
@click.option("--framework", help="Framework to use")
@click.option("--path", default=".", help="Output path")
def create(app_type: str, app_name: str, framework: Optional[str], path: str):
    """Create a new application from a template."""
    generator = AppGenerator()
    try:
        app_path = generator.create_app(app_type, app_name, framework, path)
    except Exception as e:
        console.print(f"[bold red]✗ Error:[/bold red] {e}")
        raise SystemExit(1)
    console.print(Panel(
        f"[bold green]✓ App created![/bold green]\n[cyan]Type:[/cyan] {app_type}\n"
        f"[cyan]Path:[/cyan] {app_path}\n[yellow]Next:[/yellow] cd {app_name} && cat README.md",
        title="[bold red]Git Replica — Create[/bold red]", border_style="red",
    ))


@main.command(name="list")
def list_repos():
    """List repositories managed by Git Replica."""
    manager = RepoManager()
    repos = manager.list_repos()
    if not repos:
        console.print("[yellow]No repositories found.[/yellow]")
        return
    table = Table(title="[bold red]Repositories[/bold red]", border_style="red")
    table.add_column("#", style="dim", width=4)
    table.add_column("Name", style="bold cyan")
    for i, repo in enumerate(repos, 1):
        table.add_row(str(i), str(repo))
    console.print(table)


@main.command()
@click.argument("prompt")
@click.option("--language", default="python", show_default=True)
@click.option("--output", help="Output file path")
def generate(prompt: str, language: str, output: Optional[str]):
    """Generate code using the local AI engine."""
    code = LocalCodeGenerator().generate(prompt, language)
    if output:
        Path(output).write_text(code)
        console.print(f"[bold green]✓ Saved to:[/bold green] {output}")
    else:
        console.print(Panel(
            Syntax(code, language, theme="monokai", line_numbers=True),
            title=f"[bold red]Generated {language.upper()}[/bold red]", border_style="red",
        ))


@main.command()
@click.argument("path", default=".")
@click.option("--command", help="Override auto-detected run command")
def run(path: str, command: Optional[str]):
    """Auto-detect and run the application in PATH."""
    runner = AppRunner()
    detected = runner.detect(path)
    if detected:
        fname, cmd = detected
        console.print(f"[cyan]Detected:[/cyan] {fname} → [bold]{cmd}[/bold]")
    elif command:
        cmd = command
    else:
        console.print("[bold red]✗[/bold red] Could not detect app. Use --command.")
        raise SystemExit(1)
    try:
        runner.run(path, cmd)
    except Exception as e:
        console.print(f"[bold red]✗ Error:[/bold red] {e}")
        raise SystemExit(1)


@main.command()
@click.option("--file", "file_path", help="Source file")
@click.option("--line", default=0, help="Cursor line (0-indexed)")
@click.option("--language", default="python", show_default=True)
@click.argument("code", required=False, default="")
def complete(file_path: Optional[str], line: int, language: str, code: str):
    """Get code completions using the local completion engine."""
    engine = CompletionEngine()
    if file_path:
        src = Path(file_path).read_text()
        ext = Path(file_path).suffix.lstrip(".")
        language = ext if ext else language
        lines = src.splitlines()
        cursor_line = min(line, len(lines) - 1) if lines else 0
        code_before = "\n".join(lines[:cursor_line + 1])
        current_line = lines[cursor_line] if lines else ""
    else:
        code_before = code
        current_line = code.splitlines()[-1] if code else ""
    completions = engine.complete(code_before, current_line, language)
    if not completions:
        console.print("[yellow]No completions found.[/yellow]")
        return
    table = Table(title="[bold red]Completions[/bold red]", border_style="red")
    table.add_column("Label", style="bold cyan")
    table.add_column("Kind", style="yellow")
    table.add_column("Detail", style="dim")
    for c in completions[:20]:
        table.add_row(c.label, c.kind, c.detail)
    console.print(table)


@main.command()
def new():
    """Interactive wizard to create a new project."""
    console.print(Panel("[bold red]New Project Wizard[/bold red]", border_style="red"))
    app_name = click.prompt("Project name")
    app_type = click.prompt("App type", type=click.Choice(APP_TYPES), default="api")
    framework = click.prompt("Framework (blank = default)", default="")
    path = click.prompt("Output path", default=".")
    generator = AppGenerator()
    try:
        app_path = generator.create_app(app_type, app_name, framework or None, path)
        console.print(f"[bold green]✓ Created:[/bold green] {app_path}")
    except Exception as e:
        console.print(f"[bold red]✗ Error:[/bold red] {e}")
        raise SystemExit(1)


@main.command()
@click.argument("kind", type=click.Choice(["function", "class", "api", "test"]))
@click.argument("name")
@click.option("--language", default="python", show_default=True)
@click.option("--output", help="Output file")
def scaffold(kind: str, name: str, language: str, output: Optional[str]):
    """Scaffold a component: function, class, api, test."""
    prompts = {
        "function": f"function named {name}",
        "class":    f"class named {name}",
        "api":      f"api endpoint for {name}",
        "test":     f"test for {name}",
    }
    code = LocalCodeGenerator().generate(prompts[kind], language)
    if output:
        Path(output).write_text(code)
        console.print(f"[bold green]✓ Saved to:[/bold green] {output}")
    else:
        console.print(Panel(
            Syntax(code, language, theme="monokai", line_numbers=True),
            title=f"[bold red]Scaffold {kind}: {name}[/bold red]", border_style="red",
        ))


@main.command()
@click.argument("path", default=".")
@click.option("--name", help="Service name")
@click.option("--port", default=8000, show_default=True)
def deploy(path: str, name: Optional[str], port: int):
    """Generate Dockerfile + docker-compose.yml for the project."""
    p = Path(path)
    service_name = name or p.resolve().name

    if (p / "requirements.txt").exists():
        dockerfile = f'''FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE {port}
CMD ["python", "main.py"]
'''
    elif (p / "package.json").exists():
        dockerfile = f'''FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE {port}
CMD ["npm", "start"]
'''
    elif (p / "go.mod").exists():
        dockerfile = f'''FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod go.sum* ./
RUN go mod download
COPY . .
RUN go build -o server .
FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/server .
EXPOSE {port}
CMD ["./server"]
'''
    else:
        dockerfile = f'''FROM ubuntu:22.04
WORKDIR /app
COPY . .
EXPOSE {port}
CMD ["bash", "start.sh"]
'''
    compose = f'''version: "3.9"
services:
  {service_name}:
    build: .
    ports:
      - "{port}:{port}"
    restart: unless-stopped
'''
    (p / "Dockerfile").write_text(dockerfile)
    (p / "docker-compose.yml").write_text(compose)

    table = Table(title="[bold red]Deploy Files[/bold red]", border_style="red")
    table.add_column("File", style="cyan")
    table.add_column("Status", style="green")
    table.add_row("Dockerfile", "✓ created")
    table.add_row("docker-compose.yml", "✓ created")
    console.print(table)
    console.print("\n[yellow]To deploy:[/yellow] docker compose up --build")


if __name__ == "__main__":
    main()
