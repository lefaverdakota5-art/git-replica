# Examples

This directory contains example applications created with Git Replica.

## Quick Start Examples

### 1. Create a Web App

```bash
git-replica create web hello-world
cd hello-world
pip install -r requirements.txt
python app.py
# Visit http://localhost:5000
```

### 2. Create an API

```bash
git-replica create api todo-api
cd todo-api
pip install -r requirements.txt
python main.py
# Visit http://localhost:8000/docs for API documentation
```

### 3. Create a CLI Tool

```bash
git-replica create cli my-tool
cd my-tool
pip install -r requirements.txt
python cli.py hello World
```

## Framework-Specific Examples

### Flask Web App
```bash
git-replica create web my-flask-app --framework flask
```

### Express.js App
```bash
git-replica create web my-express-app --framework express
```

### FastAPI
```bash
git-replica create api my-fastapi --framework fastapi
```

## Advanced Usage

### Initialize and Create in One Go

```bash
# Create a new repository
git-replica init my-project --description "My awesome project"

# Navigate and create an app inside
cd my-project
git-replica create web app --framework flask
```

### Generate Code Snippets

```bash
# Generate a Python function
git-replica generate "create a REST API endpoint for user authentication" --language python --output auth.py

# Generate HTML
git-replica generate "create a contact form" --language html --output contact.html
```
