"""
Application generation with AI assistance.
"""

import os
from pathlib import Path
from typing import Optional
import openai

class AppGenerator:
    """Generates applications using templates and AI assistance."""
    
    def __init__(self):
        """Initialize app generator."""
        self.templates_dir = Path(__file__).parent / 'templates'
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def create_app(self, app_type, app_name, framework=None, base_path='.'): 
        """Create a new application based on type."""
        app_path = Path(base_path) / app_name
        
        if app_path.exists():
            raise ValueError(f"Directory {app_path} already exists")
        
        app_path.mkdir(parents=True)
        
        # Determine framework if not specified
        if framework is None:
            framework = self._default_framework(app_type)
        
        # Create app structure based on type
        if app_type == 'web':
            self._create_web_app(app_path, app_name, framework)
        elif app_type == 'api':
            self._create_api_app(app_path, app_name, framework)
        elif app_type == 'cli':
            self._create_cli_app(app_path, app_name, framework)
        elif app_type == 'fullstack':
            self._create_fullstack_app(app_path, app_name, framework)
        
        return str(app_path.absolute())
    
    def _default_framework(self, app_type):
        """Get default framework for app type."""
        defaults = {
            'web': 'flask',
            'api': 'fastapi',
            'cli': 'click',
            'fullstack': 'flask+react'
        }
        return defaults.get(app_type, 'python')
    
    def _create_web_app(self, app_path, app_name, framework):
        """Create a web application."""
        if framework == 'flask':
            self._create_flask_app(app_path, app_name)
        elif framework == 'express':
            self._create_express_app(app_path, app_name)
        else:
            self._create_basic_web_app(app_path, app_name)
    
    def _create_flask_app(self, app_path, app_name):
        """Create a Flask web application."""
        # Create app.py
        app_file = app_path / 'app.py'
        with open(app_file, 'w') as f:
            f.write('''from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', title='Home')

@app.route('/about')
def about():
    return render_template('about.html', title='About')

if __name__ == '__main__':
    app.run(debug=True)
''')
        
        # Create templates directory
        templates_dir = app_path / 'templates'
        templates_dir.mkdir()
        
        base_html = templates_dir / 'base.html'
        with open(base_html, 'w') as f:
            f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - ''' + app_name + '''</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <header>
        <h1>''' + app_name + '''</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/about">About</a>
        </nav>
    </header>
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
''')
        
        index_html = templates_dir / 'index.html'
        with open(index_html, 'w') as f:
            f.write('''{% extends "base.html" %}
{% block content %}
<h2>Welcome to ''' + app_name + '''</h2>
<p>This is a Flask web application created with Git Replica.</p>
{% endblock %}
''')
        
        about_html = templates_dir / 'about.html'
        with open(about_html, 'w') as f:
            f.write('''{% extends "base.html" %}
{% block content %}
<h2>About</h2>
<p>This application was generated using Git Replica.</p>
{% endblock %}
''')
        
        # Create static directory
        static_dir = app_path / 'static'
        static_dir.mkdir()
        
        style_css = static_dir / 'style.css'
        with open(style_css, 'w') as f:
            f.write('''body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f5f5f5;
}

header {
    background-color: #333;
    color: white;
    padding: 1rem;
}

header h1 {
    margin: 0;
}

nav {
    margin-top: 0.5rem;
}

nav a {
    color: white;
    margin-right: 1rem;
    text-decoration: none;
}

nav a:hover {
    text-decoration: underline;
}

main {
    padding: 2rem;
    max-width: 800px;
    margin: 0 auto;
    background-color: white;
}
''')
        
        # Create requirements.txt
        req_file = app_path / 'requirements.txt'
        with open(req_file, 'w') as f:
            f.write('Flask>=2.3.0\n')
        
        # Create README
        self._create_readme(app_path, app_name, 'Flask web application', 
                           'pip install -r requirements.txt\npip install -e .\npython app.py')
    
    def _create_api_app(self, app_path, app_name, framework):
        """Create an API application."""
        if framework == 'fastapi':
            self._create_fastapi_app(app_path, app_name)
        else:
            self._create_basic_api_app(app_path, app_name)
    
    def _create_fastapi_app(self, app_path, app_name):
        """Create a FastAPI application."""
        main_file = app_path / 'main.py'
        with open(main_file, 'w') as f:
            f.write('''from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="''' + app_name + '''")

class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

items = []

@app.get("/")
def read_root():
    return {"message": "Welcome to ''' + app_name + '''"}

@app.get("/items", response_model=List[Item])
def get_items():
    return items

@app.post("/items", response_model=Item)
def create_item(item: Item):
    items.append(item)
    return item

@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    from fastapi import HTTPException
    for item in items:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''')
        
        req_file = app_path / 'requirements.txt'
        with open(req_file, 'w') as f:
            f.write('fastapi>=0.104.0\nuvicorn>=0.24.0\npydantic>=2.0.0\n')
        
        self._create_readme(app_path, app_name, 'FastAPI REST API',
                           'pip install -r requirements.txt\npython main.py')
    
    def _create_cli_app(self, app_path, app_name, framework):
        """Create a CLI application."""
        cli_file = app_path / 'cli.py'
        with open(cli_file, 'w') as f:
            f.write('''import click

@click.group()
@click.version_option(version="0.1.0")
def cli():
    """''' + app_name + ''' - A CLI tool created with Git Replica."""
    pass

@cli.command()
@click.argument('name')
def hello(name):
    """Say hello to someone."""
    click.echo(f"Hello, {name}!")

@cli.command()
@click.option('--count', default=1, help='Number of greetings')
def greet(count):
    """Greet multiple times."""
    for i in range(count):
        click.echo(f"Greeting #{i+1}")

if __name__ == '__main__':
    cli()
''')
        
        req_file = app_path / 'requirements.txt'
        with open(req_file, 'w') as f:
            f.write('click>=8.1.0\n')
        
        self._create_readme(app_path, app_name, 'CLI application',
                           'pip install -r requirements.txt\npython cli.py --help')
    
    def _create_fullstack_app(self, app_path, app_name, framework):
        """Create a fullstack application."""
        # Backend
        backend_dir = app_path / 'backend'
        backend_dir.mkdir()
        self._create_fastapi_app(backend_dir, app_name)
        
        # Frontend placeholder
        frontend_dir = app_path / 'frontend'
        frontend_dir.mkdir()
        
        index_html = frontend_dir / 'index.html'
        with open(index_html, 'w') as f:
            f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>''' + app_name + '''</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        h1 { color: #333; }
        .container { background: #f5f5f5; padding: 20px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>''' + app_name + '''</h1>
    <div class="container">
        <p>This is a fullstack application created with Git Replica.</p>
        <p>Backend: FastAPI (backend/main.py)</p>
        <p>Frontend: HTML/CSS/JavaScript</p>
    </div>
</body>
</html>
''')
        
        self._create_readme(app_path, app_name, 'Fullstack application',
                           'cd backend && pip install -r requirements.txt && python main.py\n# Open frontend/index.html in browser')
    
    def _create_basic_web_app(self, app_path, app_name):
        """Create a basic web app."""
        self._create_flask_app(app_path, app_name)
    
    def _create_basic_api_app(self, app_path, app_name):
        """Create a basic API app."""
        self._create_fastapi_app(app_path, app_name)
    
    def _create_express_app(self, app_path, app_name):
        """Create an Express.js app."""
        server_file = app_path / 'server.js'
        with open(server_file, 'w') as f:
            f.write('''const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
    res.send('Hello from ''' + app_name + '''!');
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
''')
        
        package_json = app_path / 'package.json'
        with open(package_json, 'w') as f:
            f.write('''{
  "name": "''' + app_name + '''",
  "version": "1.0.0",
  "description": "Express.js app created with Git Replica",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.0"
  }
}
''')
        
        self._create_readme(app_path, app_name, 'Express.js web application',
                           'npm install\nnpm start')
    
    def _create_readme(self, app_path, app_name, description, run_commands):
        """Create README for the app."""
        readme_file = app_path / 'README.md'
        with open(readme_file, 'w') as f:
            f.write(f'''# {app_name}

{description}

Created with Git Replica - your personal GitHub and Copilot for making apps.

## Getting Started

```bash
{run_commands}
```

## Features

- Auto-generated project structure
- Ready-to-use templates
- Best practices included

## License

MIT
''')
    
    def generate_code(self, prompt, language='python'):
        """Generate code based on prompt using OpenAI."""
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        system_prompt = f"You are a code generator. Generate {language} code based on the user's prompt. Provide only the code, no explanations."
        user_prompt = f"Generate {language} code for: {prompt}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Failed to generate code: {e}")
