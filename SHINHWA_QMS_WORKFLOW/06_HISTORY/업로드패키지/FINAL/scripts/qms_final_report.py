from pathlib import Path
from datetime import datetime
import csv

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT/"05_FINAL"/"RELEASED"
DIST = ROOT/"05_FINAL"/"DISTRIBUTION"
LOG = ROOT/"99_LOG"

def latest(pattern, base):
    fs = sorted(base.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return fs[0] if fs else None

def main():
    dist = latest("distribution_list_*.csv", DIST)
    integrity = latest("final_integrity_*.csv", DIST)
    out = DIST/f"FINAL_RELEASE_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    lines = ["# SHINHWA QMS FINAL RELEASE REPORT",""]
    if dist and dist.exists():
        with dist.open("r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        lines += [f"- 배포문서 수: {len(rows)}", "", "## 배포 문서"]
        for r in rows:
            lines.append(f"- {r['document_no']} / {r['revision']} / {r['released_file']}")
    else:
        lines += ["- 배포목록 없음"]

    lines += ["", "## 무결성 검사"]
    lines.append(f"- 결과파일: {integrity.name if integrity else '없음'}")
    lines += ["", "## 운영 원칙",
              "- 원본은 보존",
              "- 이전 Rev는 HISTORY 보관",
              "- 배포 전 Gate PASS 필수",
              "- 승인표시 확인 후 FINAL 배포",
              "- 변경이력 및 배포목록 유지"]
    out.write_text("\n".join(lines), encoding="utf-8")
    print(out)

if __name__ == "__main__":
    main()
