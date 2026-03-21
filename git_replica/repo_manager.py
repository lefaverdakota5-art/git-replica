"""Repository management utilities."""

import os
import git
from pathlib import Path
import json


class RepoManager:
    """Manages Git repositories."""
    
    def __init__(self, config_dir=None):
        """Initialize repository manager."""
        if config_dir is None:
            config_dir = Path.home() / '.git-replica'
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.repos_file = self.config_dir / 'repos.json'
        self._load_repos()
    
    def _load_repos(self):
        """Load repository list from config."""
        if self.repos_file.exists():
            with open(self.repos_file, 'r') as f:
                self.repos = json.load(f)
        else:
            self.repos = {}
    
    def _save_repos(self):
        """Save repository list to config."""
        with open(self.repos_file, 'w') as f:
            json.dump(self.repos, f, indent=2)
    
    def create_repo(self, name, base_path='.', description=''):
        """Create a new Git repository."""
        repo_path = Path(base_path) / name
        
        if repo_path.exists():
            raise ValueError(f"Directory {repo_path} already exists")
        
        # Create directory and initialize Git
        repo_path.mkdir(parents=True)
        repo = git.Repo.init(repo_path)
        
        # Create initial files
        readme_path = repo_path / 'README.md'
        with open(readme_path, 'w') as f:
            f.write(f"# {name}\n\n")
            if description:
                f.write(f"{description}\n\n")
            f.write("Created with Git Replica\n")
        
        gitignore_path = repo_path / '.gitignore'
        with open(gitignore_path, 'w') as f:
            f.write("# Common ignore patterns\n")
            f.write("__pycache__/\n")
            f.write("*.pyc\n")
            f.write(".DS_Store\n")
            f.write("node_modules/\n")
            f.write(".env\n")
            f.write("*.log\n")
        
        # Initial commit
        repo.index.add(['README.md', '.gitignore'])
        repo.index.commit("Initial commit")
        
        # Save to config
        self.repos[name] = {
            'path': str(repo_path.absolute()),
            'description': description
        }
        self._save_repos()
        
        return str(repo_path.absolute())
    
    def list_repos(self):
        """List all managed repositories."""
        return [f"{name} ({info['path']})" for name, info in self.repos.items()]
    
    def get_repo(self, name):
        """Get repository information."""
        return self.repos.get(name)
