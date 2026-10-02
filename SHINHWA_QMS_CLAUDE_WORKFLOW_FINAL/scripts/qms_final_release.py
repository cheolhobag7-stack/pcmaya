from pathlib import Path
import csv, shutil, re, json
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT/"02_REVIEW"
APPROVAL_PACKAGES = ROOT/"04_APPROVAL"/"PACKAGES"
FINAL = ROOT/"05_FINAL"/"RELEASED"
DIST = ROOT/"05_FINAL"/"DISTRIBUTION"
HISTORY = ROOT/"06_HISTORY"/"ARCHIVE"
ROLLBACK = ROOT/"06_HISTORY"/"ROLLBACK_BACKUP"
LOG = ROOT/"99_LOG"
RELLOG = LOG/"RELEASE_LOGS"

for d in [FINAL, DIST, HISTORY, ROLLBACK, LOG, RELLOG]:
    d.mkdir(parents=True, exist_ok=True)

DOC_RE = re.compile(r"(SH-(QM|QP|WI|FM)-\d{3})", re.I)
REV_RE = re.compile(r"Rev\.(\d{2})", re.I)

def latest_gate():
    files = sorted(REVIEW.glob("qms_release_gate_*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None

def gate_status(path):
    if not path or not path.exists():
        return "MISSING"
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"## 결과:\s*(PASS|HOLD|FAIL)", text)
    return m.group(1) if m else "UNKNOWN"

def latest_package():
    pkgs = sorted(APPROVAL_PACKAGES.glob("APPROVAL_PACKAGE_*"), key=lambda p: p.stat().st_mtime, reverse=True)
    return pkgs[-1] if pkgs else None

def revision_num(name):
    m = REV_RE.search(name)
    return int(m.group(1)) if m else -1

def archive_existing(new_file):
    dm = DOC_RE.search(new_file.stem)
    if not dm:
        return []
    docno = dm.group(1).upper()
    archived = []
    for old in FINAL.glob("*"):
        if not old.is_file():
            continue
        odm = DOC_RE.search(old.stem)
        if odm and odm.group(1).upper() == docno:
            backup_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{old.name}"
            shutil.copy2(old, ROLLBACK/backup_name)
            shutil.move(str(old), str(HISTORY/old.name))
            archived.append(old.name)
    return archived

def append_revision_history(row):
    path = LOG/"revision_history.csv"
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if not exists or path.stat().st_size == 0:
            w.writerow(["timestamp","document_no","revision","action","source","target","note"])
        w.writerow(row)

def append_workflow(action, status, message):
    path = LOG/"workflow_log.csv"
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if not exists or path.stat().st_size == 0:
            w.writerow(["timestamp","action","status","message"])
        w.writerow([datetime.now().isoformat(timespec="seconds"), action, status, message])

def main():
    gate = latest_gate()
    status = gate_status(gate)
    if status != "PASS":
        print(f"FINAL RELEASE BLOCKED: Release Gate = {status}")
        return

    pkg = latest_package()
    if not pkg:
        print("FINAL RELEASE BLOCKED: 승인대기 패키지가 없습니다.")
        return

    approval_marker = pkg/"APPROVED.txt"
    if not approval_marker.exists():
        print("FINAL RELEASE BLOCKED: 승인표시 파일 APPROVED.txt가 없습니다.")
        print("승인 완료 후 승인대기 패키지 최상위에 APPROVED.txt를 생성하세요.")
        return

    files_dir = pkg/"FILES"
    if not files_dir.exists():
        print("FINAL RELEASE BLOCKED: 승인대기 FILES 폴더가 없습니다.")
        return

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    release_rows = []

    candidates = [p for p in files_dir.rglob("*") if p.is_file() and p.name != "draft_manifest.csv"]
    for src in candidates:
        dm = DOC_RE.search(src.stem)
        rm = REV_RE.search(src.stem)
        if not dm or not rm:
            continue

        docno = dm.group(1).upper()
        rev = f"Rev.{rm.group(1)}"
        archived = archive_existing(src)

        dst = FINAL/src.name
        shutil.copy2(src, dst)

        release_rows.append({
            "document_no": docno,
            "revision": rev,
            "released_file": str(dst.relative_to(ROOT)),
            "archived_previous": "; ".join(archived),
            "release_time": datetime.now().isoformat(timespec="seconds")
        })

        append_revision_history([
            datetime.now().isoformat(timespec="seconds"),
            docno, rev, "FINAL_RELEASE",
            str(src.relative_to(ROOT)),
            str(dst.relative_to(ROOT)),
            "Release Gate PASS + APPROVED.txt 확인 후 배포"
        ])

    release_csv = DIST/f"distribution_list_{ts}.csv"
    with release_csv.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["document_no","revision","released_file","archived_previous","release_time"])
        w.writeheader()
        w.writerows(release_rows)

    release_md = DIST/f"distribution_summary_{ts}.md"
    lines = [
        "# QMS 배포목록",
        "",
        f"- 배포일시: {datetime.now().isoformat(timespec='seconds')}",
        f"- Release Gate: PASS",
        f"- 배포문서 수: {len(release_rows)}",
        "",
        "## 배포 문서"
    ]
    for r in release_rows:
        lines.append(f"- {r['document_no']} / {r['revision']} / {r['released_file']}")
    release_md.write_text("\n".join(lines), encoding="utf-8")

    append_workflow("FINAL_RELEASE", "PASS", f"{len(release_rows)} documents released")
    print(release_csv)
    print(release_md)
    print(f"RELEASED: {len(release_rows)}")

if __name__ == "__main__":
    main()
