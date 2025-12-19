#!/usr/bin/env python3
import os, runpy, sys
BASE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(BASE, "runtime", "_main.py")
if not os.path.exists(MAIN):
    sys.exit("runtime missing")
runpy.run_path(MAIN, run_name="__main__")
