from pathlib import Path
import re, csv
from collections import defaultdict
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
BASES = [ROOT/"01_ORIGINAL", ROOT/"03_EDIT", ROOT/"04_APPROVAL", ROOT/"05_FINAL"]
REVIEW = ROOT/"02_REVIEW"
DOC_RE = re.compile(r"(SH-(QM|QP|WI|FM)-\d{3})", re.I)
REV_RE = re.compile(r"Rev\.(\d{2})", re.I)

def scan():
    by_doc = defaultdict(list)
    for base in BASES:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            dm = DOC_RE.search(p.stem)
            if not dm:
                continue
            rm = REV_RE.search(p.stem)
            by_doc[dm.group(1).upper()].append({
                "path": str(p.relative_to(ROOT)),
                "rev_num": int(rm.group(1)) if rm else -1,
                "rev": f"Rev.{rm.group(1)}" if rm else ""
            })
    return by_doc

def main():
    by_doc = scan()
    rows = []
    for docno, entries in sorted(by_doc.items()):
        revs = defaultdict(list)
        for e in entries:
            revs[e["rev"]].append(e["path"])
        duplicate_revs = [rv for rv, paths in revs.items() if rv and len(paths) > 1]
        latest = max(entries, key=lambda x: x["rev_num"])
        status = "PASS"
        issues = []
        if duplicate_revs:
            status = "HOLD"
            issues.append("동일 Rev 중복 파일: " + ", ".join(duplicate_revs))
        if any(e["rev_num"] < 0 for e in entries):
            status = "HOLD"
            issues.append("Rev 누락 파일 존재")
        rows.append({
            "document_no": docno,
            "latest_rev": latest["rev"],
            "latest_path": latest["path"],
            "copies": len(entries),
            "status": status,
            "issues": " | ".join(issues)
        })

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = REVIEW / f"qms_revision_crosscheck_{ts}.csv"
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["document_no","latest_rev","latest_path","copies","status","issues"])
        w.writeheader()
        w.writerows(rows)
    print(out)

if __name__ == "__main__":
    main()
