#!/usr/bin/env bash
# Prometheus + Git Replica Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/lefaverdakota5-art/git-replica/main/install.sh | bash
set -euo pipefail

REPO_URL="https://github.com/lefaverdakota5-art/git-replica.git"
INSTALL_DIR="${INSTALL_DIR:-$HOME/.git-replica-src}"
MIN_PY_MAJOR=3
MIN_PY_MINOR=8

# ── colors ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; BRIGHT_RED='\033[1;31m'
GOLD='\033[0;33m'; BRIGHT_GOLD='\033[1;33m'
CYAN='\033[0;36m'; WHITE='\033[1;37m'
DIM='\033[2m'; BOLD='\033[1m'; NC='\033[0m'

info()    { echo -e "${CYAN}▸${NC}  $*"; }
success() { echo -e "${BRIGHT_GOLD}✔${NC}  $*"; }
warn()    { echo -e "${GOLD}⚠${NC}  $*" >&2; }
error()   { echo -e "${BRIGHT_RED}✖${NC}  $*" >&2; exit 1; }
step()    { echo -e "\n${BOLD}${RED}══${NC}${WHITE} $* ${RED}══${NC}"; }

banner() {
    echo -e "${BRIGHT_RED}"
    cat << 'EOF'
  ██████╗ ██████╗  ██████╗ ███╗   ███╗███████╗████████╗██╗  ██╗███████╗██╗   ██╗███████╗
  ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔════╝╚══██╔══╝██║  ██║██╔════╝██║   ██║██╔════╝
  ██████╔╝██████╔╝██║   ██║██╔████╔██║█████╗     ██║   ███████║█████╗  ██║   ██║███████╗
  ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔══╝     ██║   ██╔══██║██╔══╝  ██║   ██║╚════██║
  ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║███████╗   ██║   ██║  ██║███████╗╚██████╔╝███████║
  ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚══════╝
EOF
    echo -e "${NC}"
    echo -e "  ${GOLD}The Ultimate Full-Stack Development Platform${NC}"
    echo -e "  ${DIM}Better than Replit · Vercel · Railway · Cursor · Copilot${NC}"
    echo -e "  ${DIM}100% offline · No API keys required · Fully open source${NC}\n"
}

# ── prerequisite checks ──────────────────────────────────────────────────────
check_python() {
    local found=""
    for cmd in python3 python; do
        if command -v "$cmd" &>/dev/null; then
            local maj min
            maj=$("$cmd" -c 'import sys; print(sys.version_info.major)')
            min=$("$cmd" -c 'import sys; print(sys.version_info.minor)')
            if [[ "$maj" -ge "$MIN_PY_MAJOR" && "$min" -ge "$MIN_PY_MINOR" ]]; then
                found="$cmd"; break
            fi
        fi
    done
    [[ -z "$found" ]] && error "Python ${MIN_PY_MAJOR}.${MIN_PY_MINOR}+ required. Install from https://python.org"
    echo "$found"
}

check_node() {
    if command -v node &>/dev/null; then
        local ver
        ver=$(node -e 'process.stdout.write(process.version.slice(1).split(".")[0])')
        if [[ "$ver" -ge 18 ]]; then
            echo "node"; return
        fi
        warn "Node.js 18+ recommended (found v$ver). Prometheus web UI may not build."
    else
        warn "Node.js not found. Prometheus web UI will not be available."
        warn "Install from https://nodejs.org"
    fi
    echo ""
}

check_git() {
    command -v git &>/dev/null || error "git is required. Install from https://git-scm.com"
}

# ── install steps ─────────────────────────────────────────────────────────────
clone_or_update() {
    if [[ -d "$INSTALL_DIR/.git" ]]; then
        info "Updating existing installation..."
        git -C "$INSTALL_DIR" pull --quiet --ff-only
    else
        info "Cloning Prometheus / Git Replica..."
        git clone --depth=1 "$REPO_URL" "$INSTALL_DIR" --quiet
    fi
    success "Source code ready at $INSTALL_DIR"
}

install_python_pkg() {
    local python="$1"
    info "Installing git-replica Python package..."
    "$python" -m pip install --quiet --upgrade pip
    "$python" -m pip install --quiet -e "$INSTALL_DIR"
    success "git-replica v$("$python" -c 'import git_replica; print(git_replica.__version__)')" installed
}

install_prometheus_backend() {
    local python="$1"
    local backend="$INSTALL_DIR/prometheus/backend"
    if [[ -f "$backend/requirements.txt" ]]; then
        info "Installing Prometheus backend dependencies..."
        "$python" -m pip install --quiet -r "$backend/requirements.txt"
        success "Prometheus backend dependencies installed"
    fi
}

build_prometheus_frontend() {
    local node_cmd="$1"
    local frontend="$INSTALL_DIR/prometheus/frontend"
    if [[ -z "$node_cmd" || ! -d "$frontend" ]]; then
        warn "Skipping frontend build (Node not available or frontend not found)"
        return
    fi
    if [[ -d "$frontend/dist" ]]; then
        success "Prometheus frontend already built (dist/ present)"
        return
    fi
    info "Installing frontend dependencies (this may take a minute)..."
    (cd "$frontend" && npm install --silent)
    info "Building Prometheus frontend..."
    (cd "$frontend" && npm run build --silent)
    success "Prometheus frontend built → $frontend/dist"
}

create_launcher() {
    local python="$1"
    local bin_dir="$HOME/.local/bin"
    mkdir -p "$bin_dir"

    # prometheus launcher
    cat > "$bin_dir/prometheus-dev" << LAUNCHER
#!/usr/bin/env bash
# Prometheus Development Platform launcher
set -euo pipefail
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$INSTALL_DIR"
BACKEND="\$INSTALL_DIR/prometheus/backend/main.py"
FRONTEND="\$INSTALL_DIR/prometheus/frontend"

if [[ ! -f "\$BACKEND" ]]; then
  echo "Error: Prometheus not found at \$INSTALL_DIR" >&2; exit 1
fi

trap 'kill \$(jobs -p) 2>/dev/null; echo "Prometheus stopped."' EXIT INT TERM

echo ""
echo "  🔥 Starting Prometheus..."
echo "  Backend  → http://localhost:8000"
echo "  Frontend → http://localhost:5173  (or serve dist/ via backend)"
echo ""

# Start backend
$python -m uvicorn prometheus.backend.main:app --host 127.0.0.1 --port 8000 --app-dir "\$INSTALL_DIR" &
BACKEND_PID=\$!

# Start frontend dev server if dist/ not present
if [[ -d "\$FRONTEND/dist" ]]; then
  echo "  Using pre-built frontend (open http://localhost:8000)"
else
  (cd "\$FRONTEND" && npm run dev) &
fi

wait \$BACKEND_PID
LAUNCHER
    chmod +x "$bin_dir/prometheus-dev"
    success "Launcher created: $bin_dir/prometheus-dev"
}

verify_path() {
    local bin_dir="$HOME/.local/bin"
    if echo "$PATH" | grep -q "$bin_dir"; then
        success "PATH already includes $bin_dir"
    else
        warn "$bin_dir is not in your PATH."
        echo ""
        echo -e "  ${GOLD}Add this to your ~/.bashrc or ~/.zshrc:${NC}"
        echo -e "  ${DIM}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
        echo ""
        echo "  Then run: source ~/.bashrc"
    fi
}

# ── main ─────────────────────────────────────────────────────────────────────
main() {
    banner

    step "Checking Prerequisites"
    check_git && success "git found"
    PYTHON=$(check_python)
    success "Python found: $($PYTHON --version)"
    NODE=$(check_node)
    [[ -n "$NODE" ]] && success "Node.js found: $(node --version)"

    step "Downloading Prometheus"
    clone_or_update

    step "Installing Python Package"
    install_python_pkg "$PYTHON"

    step "Installing Prometheus Backend"
    install_prometheus_backend "$PYTHON"

    step "Building Prometheus Frontend"
    build_prometheus_frontend "$NODE"

    step "Creating Launcher"
    create_launcher "$PYTHON"

    step "Verifying PATH"
    verify_path

    echo ""
    echo -e "${BRIGHT_RED}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BRIGHT_RED}║${NC}   ${BRIGHT_GOLD}🔥 PROMETHEUS INSTALLATION COMPLETE${NC}                       ${BRIGHT_RED}║${NC}"
    echo -e "${BRIGHT_RED}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${BOLD}Start the platform:${NC}"
    echo -e "  ${GOLD}  prometheus-dev${NC}               # Launch full web UI"
    echo ""
    echo -e "  ${BOLD}CLI commands:${NC}"
    echo -e "  ${GOLD}  git-replica new${NC}              # Interactive wizard"
    echo -e "  ${GOLD}  git-replica create react my-app${NC}"
    echo -e "  ${GOLD}  git-replica create api  my-api${NC}"
    echo -e "  ${GOLD}  git-replica run${NC}              # Auto-detect & run"
    echo -e "  ${GOLD}  git-replica complete --file app.py${NC}"
    echo -e "  ${GOLD}  git-replica generate \"fibonacci\" --language python${NC}"
    echo ""
    echo -e "  ${DIM}Docs: $INSTALL_DIR/README.md${NC}"
    echo ""
}

main "$@"
