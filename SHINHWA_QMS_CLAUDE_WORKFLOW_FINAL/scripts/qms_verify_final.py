from pathlib import Path
import re, hashlib, csv
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT/"05_FINAL"/"RELEASED"
DIST = ROOT/"05_FINAL"/"DISTRIBUTION"
REVIEW = ROOT/"02_REVIEW"

DOC_RE = re.compile(r"(SH-(QM|QP|WI|FM)-\d{3})", re.I)
REV_RE = re.compile(r"Rev\.\d{2}", re.I)

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    rows = []
    for p in sorted(FINAL.glob("*")):
        if not p.is_file():
            continue
        dm = DOC_RE.search(p.stem)
        rm = REV_RE.search(p.stem)
        rows.append({
            "file": p.name,
            "document_no": dm.group(1).upper() if dm else "",
            "revision": rm.group(0) if rm else "",
            "sha256": sha256(p),
            "size_bytes": p.stat().st_size,
            "status": "PASS" if dm and rm else "HOLD"
        })
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = DIST/f"final_integrity_{ts}.csv"
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["file","document_no","revision","sha256","size_bytes","status"])
        w.writeheader()
        w.writerows(rows)
    print(out)

if __name__ == "__main__":
    main()
