"""Tests for Git Replica."""

import os
import pytest
import tempfile
import shutil
from pathlib import Path
from git_replica.repo_manager import RepoManager
from git_replica.app_generator import AppGenerator


class TestRepoManager:
    """Test repository management functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / '.git-replica'
        self.manager = RepoManager(config_dir=self.config_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_create_repo(self):
        """Test creating a new repository."""
        repo_path = self.manager.create_repo('test-repo', self.temp_dir, 'Test repository')
        
        assert os.path.exists(repo_path)
        assert os.path.exists(os.path.join(repo_path, '.git'))
        assert os.path.exists(os.path.join(repo_path, 'README.md'))
        assert os.path.exists(os.path.join(repo_path, '.gitignore'))
    
    def test_list_repos(self):
        """Test listing repositories."""
        self.manager.create_repo('repo1', self.temp_dir)
        self.manager.create_repo('repo2', self.temp_dir)
        
        repos = self.manager.list_repos()
        assert len(repos) == 2
    
    def test_duplicate_repo(self):
        """Test creating duplicate repository raises error."""
        self.manager.create_repo('test-repo', self.temp_dir)
        
        with pytest.raises(ValueError):
            self.manager.create_repo('test-repo', self.temp_dir)


class TestAppGenerator:
    """Test application generation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = AppGenerator()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_create_web_app(self):
        """Test creating a web application."""
        app_path = self.generator.create_app('web', 'test-web', 'flask', self.temp_dir)
        
        assert os.path.exists(app_path)
        assert os.path.exists(os.path.join(app_path, 'app.py'))
        assert os.path.exists(os.path.join(app_path, 'requirements.txt'))
        assert os.path.exists(os.path.join(app_path, 'templates'))
        assert os.path.exists(os.path.join(app_path, 'static'))
    
    def test_create_api_app(self):
        """Test creating an API application."""
        app_path = self.generator.create_app('api', 'test-api', 'fastapi', self.temp_dir)
        
        assert os.path.exists(app_path)
        assert os.path.exists(os.path.join(app_path, 'main.py'))
        assert os.path.exists(os.path.join(app_path, 'requirements.txt'))
    
    def test_create_cli_app(self):
        """Test creating a CLI application."""
        app_path = self.generator.create_app('cli', 'test-cli', 'click', self.temp_dir)
        
        assert os.path.exists(app_path)
        assert os.path.exists(os.path.join(app_path, 'cli.py'))
        assert os.path.exists(os.path.join(app_path, 'requirements.txt'))
    
    def test_generate_code_python(self):
        """Test code generation for Python."""
        code = self.generator.generate_code('test function', 'python')
        
        assert 'def main():' in code
        assert 'python' in code.lower() or 'generated' in code.lower()
    
    def test_generate_code_javascript(self):
        """Test code generation for JavaScript."""
        code = self.generator.generate_code('test function', 'javascript')
        
        assert 'function main()' in code
        assert 'console.log' in code
