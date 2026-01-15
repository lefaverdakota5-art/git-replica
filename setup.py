from setuptools import setup, find_packages

setup(
    name="git-replica",
    version="0.1.0",
    description="Personal GitHub and Copilot for making apps",
    author="lefaverdakota5-art",
    packages=find_packages(),
    install_requires=[
        "gitpython>=3.1.40",
        "openai>=1.0.0",
        "click>=8.1.0",
        "jinja2>=3.1.0",
        "pyyaml>=6.0.0",
    ],
    entry_points={
        "console_scripts": [
            "git-replica=git_replica.cli:main",
        ],
    },
    python_requires=">=3.8",
)
