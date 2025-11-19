#!/bin/bash
# ============================================================
#  Universal Python Auto Installer + Spinner + TQDM
#  Works on: Termux, Debian, Ubuntu, all Linux variants
#  Author: Suhu Kian
# ============================================================

REQUIRED_PY_VERSION="3.12"
MAIN_SCRIPT="auth.py"
PACKAGES=(
  "requests"
  "aiofiles"
  "distro"
  "websocket-client"
  "aiohttp"
  "asyncio"
  "faker"
  "colorama"
  "pyfiglet"
  "pycryptodome"
  "psutil"
  "urllib3"
  "python-socketio"
  "tqdm"
  "requests[socks]"
  "httpx[http2]"
)

# ===== Spinner function =====
spinner() {
  local pid=$!
  local spin=('⠋' '⠙' '⠸' '⠴' '⠦' '⠇')
  local i=0
  while kill -0 $pid 2>/dev/null; do
    i=$(( (i+1) % ${#spin[@]} ))
    printf "\r${spin[$i]} Installing..."
    sleep 0.1
  done
  printf "\r"
}

# ===== Detect Python =====
PYTHON_BIN=$(command -v python3.12 || command -v python3 || command -v python)
if [ -z "$PYTHON_BIN" ]; then
  echo "Error: Python 3.12+ not found. Please install Python 3.12 or newer."
  exit 1
fi

# ===== Check Python version =====
PY_VERSION=$($PYTHON_BIN -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if (( $(echo "$PY_VERSION < $REQUIRED_PY_VERSION" | bc -l) )); then
  echo "Warning: Python version $PY_VERSION detected. Python $REQUIRED_PY_VERSION or newer is recommended."
fi

# ===== Ensure pip =====
$PYTHON_BIN -m ensurepip --upgrade >/dev/null 2>&1 || {
  echo "Error: Failed to ensure pip installation."
  exit 1
}
$PYTHON_BIN -m pip install --upgrade pip >/dev/null 2>&1 || {
  echo "Error: Failed to upgrade pip."
  exit 1
}

# ===== Install lolcat =====
if ! command -v lolcat >/dev/null 2>&1; then
  echo "Installing lolcat..."
  if command -v apt >/dev/null 2>&1; then
    pkg install -y ruby >/dev/null 2>&1 || sudo apt install -y ruby >/dev/null 2>&1
  fi
  gem install lolcat >/dev/null 2>&1 || echo "Warning: Could not install lolcat. Proceeding without colors."
fi

# ===== Install tqdm early (for progress bar) =====
echo "Preparing installation progress tools..."
if ! $PYTHON_BIN -m pip install -q tqdm >/dev/null 2>&1; then
  echo "Error: Failed to install tqdm."
  exit 1
fi

# ===== Display header =====
clear
echo "============================================="
echo "Python Auto Dependency Installer"
echo "============================================="

# ===== Create temporary tqdm installer script =====
TMP_SCRIPT=$(mktemp)
cat <<EOF > "$TMP_SCRIPT"
from tqdm import tqdm
import subprocess, sys, time

packages = ${PACKAGES[@]@Q}.split()
for pkg in tqdm(packages, desc="Installing packages", ncols=80, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"):
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", pkg, "--upgrade"], check=True)
    except subprocess.CalledProcessError:
        print(f"Warning: Failed to install {pkg}.")
    time.sleep(0.05)
EOF

# ===== Run tqdm installer =====
if ! $PYTHON_BIN "$TMP_SCRIPT"; then
  echo "Error: Failed to run package installation script."
  exit 1
fi
rm -f "$TMP_SCRIPT"

# ===== Final messages =====
sleep 0.5
clear
echo "============================================="
echo "All Python packages installed successfully!"
$PYTHON_BIN --version
echo "============================================="

# ===== Run main script =====
if [ -f "$MAIN_SCRIPT" ]; then
  echo "Launching $MAIN_SCRIPT ..."
  sleep 1
  if ! $PYTHON_BIN "$MAIN_SCRIPT"; then
    echo "Error: Failed to execute $MAIN_SCRIPT."
    exit 1
  fi
else
  echo "Error: File '$MAIN_SCRIPT' not found in this directory."
  exit 1
fi
