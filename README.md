# Git Replica

Your personal GitHub and Copilot for making apps! 🚀

Git Replica is a command-line tool that combines Git repository management with AI-assisted application generation, making it easy to create and manage your development projects.

## Features

- **Repository Management**: Initialize and manage Git repositories with ease
- **App Generation**: Create web apps, APIs, CLI tools, and fullstack applications
- **Multiple Frameworks**: Support for Flask, FastAPI, Express.js, and more
- **Code Generation**: Generate code snippets using AI assistance (template-based)
- **Best Practices**: Generated apps follow industry best practices

## Installation

```bash
# Clone this repository
git clone https://github.com/lefaverdakota5-art/git-replica.git
cd git-replica

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Usage

### Initialize a New Repository

```bash
git-replica init my-project --description "My awesome project"
```

### Create Applications

#### Web Application (Flask)
```bash
git-replica create web my-web-app
cd my-web-app
pip install -r requirements.txt
python app.py
```

#### REST API (FastAPI)
```bash
git-replica create api my-api
cd my-api
pip install -r requirements.txt
python main.py
```

#### CLI Tool
```bash
git-replica create cli my-cli-tool
cd my-cli-tool
pip install -r requirements.txt
python cli.py --help
```

#### Fullstack Application
```bash
git-replica create fullstack my-fullstack-app
cd my-fullstack-app
# Backend
cd backend && pip install -r requirements.txt && python main.py
# Frontend: Open frontend/index.html in browser
```

### Generate Code

```bash
# Generate Python code
git-replica generate "create a function to calculate fibonacci" --language python

# Save to file
git-replica generate "create a REST endpoint" --language python --output api.py
```

### List Repositories

```bash
git-replica list --all
```

## Supported App Types

- **web**: Web applications (Flask, Express)
- **api**: REST APIs (FastAPI, Flask)
- **cli**: Command-line tools (Click)
- **fullstack**: Full-stack applications (FastAPI + HTML/JS)

## Supported Frameworks

- Python: Flask, FastAPI, Click
- JavaScript: Express.js
- More coming soon!

## Requirements

- Python 3.8+
- Git
- See `requirements.txt` for Python dependencies

## Development

```bash
# Install in development mode
pip install -e .

# Run tests (if available)
python -m pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for your personal and commercial projects.

## About

Created with the vision of having a personal development assistant that combines the power of Git repository management with intelligent app scaffolding and code generation.
