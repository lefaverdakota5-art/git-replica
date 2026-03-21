"""CLI interface for Git Replica."""

import click
import os
from pathlib import Path
from git_replica.repo_manager import RepoManager
from git_replica.app_generator import AppGenerator


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Git Replica - Personal GitHub and Copilot for making apps."""
    pass


@main.command()
@click.argument('repo_name')
@click.option('--path', default='.', help='Path where to create the repository')
@click.option('--description', default='', help='Repository description')
def init(repo_name, path, description):
    """Initialize a new Git repository."""
    manager = RepoManager()
    try:
        repo_path = manager.create_repo(repo_name, path, description)
        click.echo(f"✓ Created repository: {repo_path}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


@main.command()
@click.argument('app_type', type=click.Choice(['web', 'api', 'cli', 'fullstack']))
@click.argument('app_name')
@click.option('--framework', help='Framework to use (e.g., flask, express, fastapi)')
@click.option('--path', default='.', help='Path where to create the app')
def create(app_type, app_name, framework, path):
    """Create a new application with AI assistance."""
    generator = AppGenerator()
    try:
        app_path = generator.create_app(app_type, app_name, framework, path)
        click.echo(f"✓ Created {app_type} app: {app_path}")
        click.echo(f"✓ Next steps:")
        click.echo(f"  cd {app_name}")
        click.echo(f"  # Follow instructions in README.md")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


@main.command()
def list():
    """List repositories managed by Git Replica."""
    manager = RepoManager()
    repos = manager.list_repos()
    if not repos:
        click.echo("No repositories found.")
    else:
        click.echo("Repositories:")
        for repo in repos:
            click.echo(f"  • {repo}")


@main.command()
@click.argument('prompt')
@click.option('--language', default='python', help='Programming language')
@click.option('--output', help='Output file path')
def generate(prompt, language, output):
    """Generate code using AI assistance."""
    generator = AppGenerator()
    try:
        code = generator.generate_code(prompt, language)
        if output:
            with open(output, 'w') as f:
                f.write(code)
            click.echo(f"✓ Code generated and saved to: {output}")
        else:
            click.echo(code)
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


if __name__ == '__main__':
    main()
