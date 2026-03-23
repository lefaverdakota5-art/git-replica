"""
App runner — auto-detects app type and runs it.
No external API required.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple


class AppRunner:
    """Auto-detects and runs applications in the current or specified directory."""

    # Ordered list of (file_pattern, run_command_template)
    DETECTORS = [
        # Python
        ("manage.py",           "python manage.py runserver"),
        ("app.py",              "python app.py"),
        ("main.py",             None),           # special-cased below
        ("server.py",           "python server.py"),
        ("run.py",              "python run.py"),
        # Node / JS
        ("package.json",        None),           # special-cased below
        ("server.js",           "node server.js"),
        ("index.js",            "node index.js"),
        # Go
        ("main.go",             "go run ."),
        ("go.mod",              "go run ."),
        # Rust
        ("Cargo.toml",          "cargo run"),
        # Ruby
        ("Gemfile",             "bundle exec ruby app.rb"),
        ("app.rb",              "ruby app.rb"),
    ]

    def detect(self, path: str = ".") -> Optional[Tuple[str, str]]:
        """
        Detect how to run the app in *path*.

        Returns (description, command) or None if undetected.
        """
        p = Path(path)

        for filename, cmd in self.DETECTORS:
            fp = p / filename

            if not fp.exists():
                continue

            if filename == "main.py":
                cmd = self._detect_main_py(fp)
            elif filename == "package.json":
                cmd = self._detect_package_json(fp)

            if cmd:
                return (filename, cmd)

        return None

    # ------------------------------------------------------------------
    # Special cases
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_main_py(filepath: Path) -> str:
        """Check whether main.py uses uvicorn/fastapi or plain python."""
        try:
            src = filepath.read_text()
        except OSError:
            return "python main.py"

        if "uvicorn" in src or "FastAPI" in src or "fastapi" in src:
            # Try to find the app variable
            import re
            m = re.search(r"(\w+)\s*=\s*FastAPI\(", src)
            app_var = m.group(1) if m else "app"
            return f"uvicorn main:{app_var} --reload"
        if "flask" in src.lower() or "Flask" in src:
            return "python main.py"
        return "python main.py"

    @staticmethod
    def _detect_package_json(filepath: Path) -> Optional[str]:
        """Read package.json and find the best run command."""
        import json
        try:
            data = json.loads(filepath.read_text())
        except (OSError, json.JSONDecodeError):
            return "npm start"

        scripts = data.get("scripts", {})

        # Prefer dev scripts
        for key in ("dev", "start", "serve", "run"):
            if key in scripts:
                return f"npm run {key}" if key != "start" else "npm start"

        return "npm start"

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def run(self, path: str = ".", command: Optional[str] = None) -> int:
        """
        Run the app.

        If *command* is provided it is used directly; otherwise auto-detection
        is performed.  Returns the process exit code.
        """
        if command is None:
            detected = self.detect(path)
            if not detected:
                raise RuntimeError(
                    "Could not auto-detect how to run this app. "
                    "Use --command to specify the run command explicitly."
                )
            _, command = detected

        return subprocess.call(command, shell=True, cwd=path)
