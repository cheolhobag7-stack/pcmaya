from pathlib import Path
import csv, re
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT/"02_REVIEW"
APPROVAL = ROOT/"04_APPROVAL"
FINAL = ROOT/"05_FINAL"

def latest(pattern):
    files = sorted(REVIEW.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None

def read_rows(path):
    if not path:
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def main():
    content = read_rows(latest("qms_content_review_*.csv"))
    revisions = read_rows(latest("qms_revision_crosscheck_*.csv"))
    register = read_rows(latest("qms_register_compare_*.csv"))

    blockers = []
    holds = []
    for label, rows in [("본문점검", content), ("Rev점검", revisions), ("대장대조", register)]:
        for r in rows:
            st = r.get("status","")
            target = r.get("file") or r.get("document_no") or ""
            issue = r.get("issues","")
            if st == "FAIL":
                blockers.append(f"{label}: {target} :: {issue}")
            elif st == "HOLD":
                holds.append(f"{label}: {target} :: {issue}")

    status = "PASS"
    if blockers:
        status = "FAIL"
    elif holds:
        status = "HOLD"

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = REVIEW/f"qms_release_gate_{ts}.md"
    lines = [
        "# QMS FINAL Release Gate",
        "",
        f"## 결과: {status}",
        "",
        f"- FAIL 항목: {len(blockers)}",
        f"- HOLD 항목: {len(holds)}",
        "",
        "## FAIL"
    ]
    lines.extend([f"- {x}" for x in blockers] or ["- 없음"])
    lines += ["", "## HOLD"]
    lines.extend([f"- {x}" for x in holds] or ["- 없음"])
    lines += ["", "## 판정 기준",
              "- FAIL이 하나라도 있으면 FINAL 배포 금지",
              "- FAIL은 없고 HOLD가 있으면 승인/확인 후 재검사",
              "- 모두 PASS일 때만 FINAL 배포 후보"]
    out.write_text("\n".join(lines), encoding="utf-8")
    print(out)
    print(status)

if __name__ == "__main__":
    main()
