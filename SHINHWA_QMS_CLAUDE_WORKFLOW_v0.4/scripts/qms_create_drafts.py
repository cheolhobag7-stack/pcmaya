from pathlib import Path
import csv, shutil, re
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "02_REVIEW"
DRAFT = ROOT / "03_EDIT" / "AUTO_DRAFT"
DRAFT.mkdir(parents=True, exist_ok=True)

def latest_proposals():
    files = sorted(REVIEW.glob("qms_autofix_proposals_*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None

def main():
    prop = latest_proposals()
    if not prop:
        print("수정 제안 파일이 없습니다. 먼저 qms_autofix_proposals.py 실행 필요.")
        return

    with prop.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    manifest = []
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch = DRAFT / f"BATCH_{ts}"
    batch.mkdir(parents=True, exist_ok=True)

    for r in rows:
        rel = r.get("file","")
        if not rel:
            continue
        src = ROOT / rel
        if not src.exists():
            continue
        dst = batch / src.name
        shutil.copy2(src, dst)
        manifest.append({
            "source": str(src.relative_to(ROOT)),
            "draft": str(dst.relative_to(ROOT)),
            "status": r.get("status",""),
            "proposed_actions": r.get("proposed_actions",""),
            "note": "원본 복사본. 자동 내용수정 전 사용자 검토 필요."
        })

    manifest_path = batch / "draft_manifest.csv"
    with manifest_path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["source","draft","status","proposed_actions","note"])
        w.writeheader()
        w.writerows(manifest)

    print(batch)
    print(manifest_path)

if __name__ == "__main__":
    main()
