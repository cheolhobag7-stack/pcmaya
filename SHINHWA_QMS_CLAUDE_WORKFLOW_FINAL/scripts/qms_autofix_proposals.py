from pathlib import Path
import csv, re, shutil
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "02_REVIEW"
ORIGINAL = ROOT / "01_ORIGINAL"
DRAFT = ROOT / "03_EDIT" / "AUTO_DRAFT"
DRAFT.mkdir(parents=True, exist_ok=True)

def latest_review():
    files = sorted(REVIEW.glob("qms_content_review_*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None

def safe_name(s):
    return re.sub(r'[\\/:*?"<>|]+', "_", s)

def main():
    review = latest_review()
    if not review:
        print("최신 qms_content_review CSV가 없습니다. 먼저 /qms-review 또는 /qms-full-audit 실행 필요.")
        return

    with review.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    proposal_csv = REVIEW / f"qms_autofix_proposals_{ts}.csv"

    proposals = []
    for r in rows:
        if r.get("status") not in {"HOLD", "FAIL"}:
            continue
        issues = r.get("issues", "")
        actions = []
        if "SH 접두어 미적용 참조" in issues:
            actions.append("QM/QP/WI/FM 참조에 SH- 접두어 적용 검토")
        if "삭제 지시 문구 발견" in issues:
            actions.append("삭제 지시 문구 제거")
        if "회사명 본문 확인 필요" in issues:
            actions.append("(주)신화에이치앤티 표기 확인/보완")
        if "파일명/본문 Rev 불일치" in issues:
            actions.append("파일명과 본문 Rev 일치화")
        if "파일명/본문 문서번호 불일치" in issues:
            actions.append("파일명과 본문 문서번호 일치화")
        if "실제 파일 미존재 참조" in issues:
            actions.append("참조문서 번호 존재 여부 확인 후 수정 또는 누락문서 등록")

        proposals.append({
            "file": r.get("file",""),
            "status": r.get("status",""),
            "issues": issues,
            "proposed_actions": " | ".join(actions) if actions else "수동 검토 필요",
            "auto_edit_allowed": "NO"
        })

    with proposal_csv.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["file","status","issues","proposed_actions","auto_edit_allowed"])
        w.writeheader()
        w.writerows(proposals)

    print(proposal_csv)

if __name__ == "__main__":
    main()
