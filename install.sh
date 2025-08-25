#!/bin/bash
set -e

# =====================================================
# Aromance Project - Installation Script (Final)
# =====================================================

# Helper functions
info()    { echo "[INFO] $1"; }
success() { echo "[OK]   $1"; }
warn()    { echo "[WARN] $1"; }

# Update system
info "Updating system packages..."
sudo apt update && sudo apt upgrade -y
success "System updated."

# Install basic dependencies
info "Installing basic dependencies..."
sudo apt install -y \
    curl wget git build-essential pkg-config \
    libssl-dev libclang-dev cmake \
    python3 python3-pip python3-venv \
    ca-certificates gnupg lsb-release
success "Basic dependencies installed."

# Check Python version
PYTHON_VERSION=$(python3 -V 2>&1 | awk '{print $2}')
REQUIRED_PYTHON="3.12"
if [[ "$PYTHON_VERSION" < "$REQUIRED_PYTHON" ]]; then
    warn "Python version is $PYTHON_VERSION, but >=3.12 is recommended."
fi

# Install Node.js v20.x
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    if [[ $NODE_VERSION == v20.* ]]; then
        info "Node.js already installed: $NODE_VERSION"
    else
        warn "Node.js version is $NODE_VERSION, upgrading to v20..."
        sudo apt remove -y nodejs
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt install -y nodejs
    fi
else
    info "Installing Node.js v20..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt install -y nodejs
fi
success "Node.js: $(node -v), npm: $(npm -v)"

# Install Rust
if command -v rustc &> /dev/null; then
    info "Rust already installed: $(rustc --version)"
else
    info "Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source $HOME/.cargo/env
fi
success "Rust: $(rustc --version)"

# Ensure wasm32 target for ICP canisters
info "Adding Rust target wasm32-unknown-unknown..."
rustup target add wasm32-unknown-unknown || true
success "Rust target wasm32-unknown-unknown ready."

# Install DFX (lock version 0.24.3)
DFX_VERSION="0.24.3"
if command -v dfx &> /dev/null; then
    info "DFX already installed: $(dfx --version)"
else
    info "Installing DFX $DFX_VERSION..."
    sh -ci "$(curl -fsSL https://internetcomputer.org/install.sh)" -- $DFX_VERSION
    export PATH="$HOME/bin:$PATH"
fi
success "DFX: $(dfx --version)"

# Setup Python environment
if [[ ! -d "fetchai_env" ]]; then
    info "Creating Python virtual environment..."
    python3 -m venv fetchai_env
fi
source fetchai_env/bin/activate
pip install --upgrade pip
pip install uagents cosmpy requests asyncio httpx
success "Python environment ready."

# Install root dependencies
info "Installing root dependencies..."
npm install
success "Root dependencies installed."

# Install frontend dependencies
info "Installing frontend dependencies..."
cd src/aromance_frontend
rm -rf node_modules package-lock.json
npm ci || npm install
# Ensure react + react-dom installed
npm install react react-dom
cd ../..
success "Frontend dependencies installed."

# Build Rust backend
info "Building Rust backend..."
cargo build --workspace
success "Rust backend built."

# Ensure .env exists
if [[ ! -f ".env" ]]; then
    info "Creating default .env file..."
    echo "DFX_NETWORK=local" > .env
fi

success "Installation complete."
