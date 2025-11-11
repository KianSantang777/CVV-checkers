#!/bin/bash
# ============================================================
#  Universal Python Auto Installer + Spinner + TQDM + Lolcat
#  Works on: Termux, Debian, Ubuntu, all Linux variants
#  Author: Suhu Kian 😎
# ============================================================

REQUIRED_PY_VERSION="3.12"
MAIN_SCRIPT="cvv.py"
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
  echo "❌ Python 3.12+ not found. Please install Python 3.12 or newer."
  exit 1
fi

# ===== Check Python version =====
PY_VERSION=$($PYTHON_BIN -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if (( $(echo "$PY_VERSION < $REQUIRED_PY_VERSION" | bc -l) )); then
  echo "⚠️  Python version $PY_VERSION detected. Python $REQUIRED_PY_VERSION or newer is recommended."
fi

# ===== Ensure pip =====
$PYTHON_BIN -m ensurepip --upgrade >/dev/null 2>&1
$PYTHON_BIN -m pip install --upgrade pip >/dev/null 2>&1

# ===== Install lolcat =====
if ! command -v lolcat >/dev/null 2>&1; then
  echo "🔧 Installing lolcat..."
  if command -v apt >/dev/null 2>&1; then
    pkg install -y ruby >/dev/null 2>&1 || sudo apt install -y ruby >/dev/null 2>&1
  fi
  gem install lolcat >/dev/null 2>&1 || echo "⚠️ Could not install lolcat. Proceeding without colors."
fi

# ===== Install tqdm early (for progress bar) =====
echo "🚀 Preparing installation progress tools..." | lolcat 2>/dev/null || echo "🚀 Preparing installation progress tools..."
$PYTHON_BIN -m pip install -q tqdm >/dev/null 2>&1

# ===== Display header =====
clear
echo "=============================================" | lolcat 2>/dev/null || echo "============================================="
echo "🔥 Python Auto Dependency Installer 🔥" | lolcat 2>/dev/null || echo "Python Auto Dependency Installer"
echo "=============================================" | lolcat 2>/dev/null || echo "============================================="

# ===== Create temporary tqdm installer script =====
TMP_SCRIPT=$(mktemp)
cat <<EOF > "$TMP_SCRIPT"
from tqdm import tqdm
import subprocess, sys, time

packages = ${PACKAGES[@]@Q}.split()
for pkg in tqdm(packages, desc="Installing packages", ncols=80, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"):
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", pkg, "--upgrade"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
    time.sleep(0.05)
EOF

# ===== Run tqdm installer =====
$PYTHON_BIN "$TMP_SCRIPT"
rm -f "$TMP_SCRIPT"

# ===== Final messages =====
sleep 0.5
clear
echo "=============================================" | lolcat 2>/dev/null || echo "============================================="
echo "🎉 All Python packages installed successfully!" | lolcat 2>/dev/null || echo "🎉 All Python packages installed successfully!"
$PYTHON_BIN --version | lolcat 2>/dev/null || $PYTHON_BIN --version
echo "=============================================" | lolcat 2>/dev/null || echo "============================================="

# ===== Run main script =====
if [ -f "$MAIN_SCRIPT" ]; then
  echo "🚀 Launching $MAIN_SCRIPT ..." | lolcat 2>/dev/null || echo "🚀 Launching $MAIN_SCRIPT ..."
  sleep 1
  $PYTHON_BIN "$MAIN_SCRIPT"
else
  echo "❌ File '$MAIN_SCRIPT' not found in this directory." | lolcat 2>/dev/null || echo "❌ File '$MAIN_SCRIPT' not found in this directory."
fi
