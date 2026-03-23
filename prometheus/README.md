# Prometheus — Ultimate Dev Platform

> Build faster than thought. 100% local AI. No external APIs.

## Quick Start

```bash
cd prometheus
./start.sh
```

Then open:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Manual Start

### Backend
```bash
cd prometheus/backend
pip install -r requirements.txt
# from repo root:
PYTHONPATH=. uvicorn prometheus.backend.main:app --reload --port 8000
```

### Frontend
```bash
cd prometheus/frontend
npm install
npm run dev
```

## Features

- **AI Code Generation** — LocalCodeGenerator, zero external APIs
- **Monaco Editor** — Full VS Code editor in browser
- **WebSocket Streaming** — Real-time code generation
- **10+ App Templates** — FastAPI, React, Vue, Django, Go, Node.js, Next.js…
- **Git Integration** — init, commit, log, diff via GitPython
- **Package Manager** — pip/npm install from browser
- **Deploy** — Auto-generate Dockerfile + docker-compose
- **Terminal** — Execute shell commands in project dir
- **Cyberpunk UI** — Royal Red, Gold, Black Neon theme

## Architecture

```
prometheus/
├── backend/
│   ├── main.py          # FastAPI, all endpoints
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/       # Landing, Builder, Projects, SystemControl
│   │   ├── components/  # NavBar, FileTree, StatusBadge, Terminal
│   │   ├── api.js       # API client
│   │   └── index.css    # Cyberpunk theme
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
├── start.sh
└── README.md
```

## License

MIT
