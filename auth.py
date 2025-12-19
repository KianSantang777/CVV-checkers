#!/usr/bin/env python3
# ==========================================================
# CVV-Checkers Python Launcher (auth.py)
# Auto-install deps, auto-run, auto-restart
# Compatible: Termux / Linux / Ubuntu / Debian
# Author: Kian Santang
# ==========================================================

import os
import sys
import time
import subprocess
import traceback

RESTART_DELAY = 5

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_PATH = os.path.join(BASE_DIR, "dist", "adsjc.py")
REQ_FILE = os.path.join(BASE_DIR, "requirements.txt")
PYTHON = sys.executable


try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except Exception:
    class _D:
        def __getattr__(self, _): return ""
    Fore = Style = _D()


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    clear()
    print(Fore.CYAN + "===============================================")
    print(Fore.CYAN + "        CVV-CHECKERS PYTHON LAUNCHER            ")
    print(Fore.CYAN + "===============================================")
    print(Fore.YELLOW + f" Python   : {PYTHON}")
    print(Fore.YELLOW + f" BaseDir  : {BASE_DIR}")
    print(Fore.CYAN + "===============================================\n")


def info(msg):
    print(Fore.CYAN + "[INFO] " + Style.BRIGHT + msg)


def success(msg):
    print(Fore.GREEN + "[OK]   " + Style.BRIGHT + msg)


def warn(msg):
    print(Fore.YELLOW + "[WARN] " + Style.BRIGHT + msg)


def error(msg):
    print(Fore.RED + "[ERR]  " + Style.BRIGHT + msg)


def fatal(msg):
    error(msg)
    sys.exit(1)


def detect_env():
    return "termux" if os.path.exists("/data/data/com.termux") else "linux"

ENV = detect_env()


def ensure_pip():
    try:
        subprocess.check_call(
            [PYTHON, "-m", "pip", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except Exception:
        return False


def pip_install(args, silent=True):
    cmd = [PYTHON, "-m", "pip"] + args
    try:
        subprocess.check_call(
            cmd,
            stdout=subprocess.DEVNULL if silent else None,
            stderr=subprocess.DEVNULL if silent else None
        )
        return True
    except Exception:
        return False


def install_requirements():
    if not os.path.isfile(REQ_FILE):
        warn("requirements.txt not found, skipping")
        return

    info("Installing dependencies from requirements.txt")
    ok = pip_install(["install", "--upgrade", "pip"])
    if not ok:
        warn("Failed to upgrade pip")

    if not pip_install(["install", "-r", REQ_FILE], silent=False):
        fatal("Failed to install requirements.txt")

    success("requirements.txt installed successfully")



def validate_files():
    if not os.path.isfile(APP_PATH):
        fatal(f"File not found: {APP_PATH}")

    if not os.access(APP_PATH, os.R_OK):
        fatal("adsjc.py is not readable")

    success("Target script validated")



def run_loop():
    print(Fore.MAGENTA + "\n===============================================")
    print(Fore.MAGENTA + "   Running dist/adsjc.py (AUTO-RESTART ON)     ")
    print(Fore.MAGENTA + "   Press CTRL + C to stop manually             ")
    print(Fore.MAGENTA + "===============================================\n")

    while True:
        try:
            process = subprocess.Popen(
                [PYTHON, APP_PATH],
                cwd=BASE_DIR
            )
            code = process.wait()

            warn(f"adsjc.py exited (code={code})")
            info(f"Restarting in {RESTART_DELAY} seconds...\n")
            time.sleep(RESTART_DELAY)

        except KeyboardInterrupt:
            print()
            success("Stopped by user")
            sys.exit(0)

        except Exception as e:
            error("Runtime crash detected")
            warn(str(e))
            print(traceback.format_exc())
            info(f"Restarting in {RESTART_DELAY} seconds...\n")
            time.sleep(RESTART_DELAY)



def main():
    banner()
    info(f"Environment: {ENV}")

    if not ensure_pip():
        fatal("pip not available. Install python-pip first.")

    install_requirements()
    validate_files()
    run_loop()


if __name__ == "__main__":
    main()
