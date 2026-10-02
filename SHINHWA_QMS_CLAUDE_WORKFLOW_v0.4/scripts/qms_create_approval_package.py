from pathlib import Path
import shutil, csv
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
APPROVAL = ROOT / "04_APPROVAL" / "PACKAGES"
REVIEW = ROOT / "02_REVIEW"
DRAFT_ROOT = ROOT / "03_EDIT" / "AUTO_DRAFT"
APPROVAL.mkdir(parents=True, exist_ok=True)

def latest(pattern, base):
    files = sorted(base.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None

def main():
    draft_batches = sorted(DRAFT_ROOT.glob("BATCH_*"))
    if not draft_batches:
        print("AUTO_DRAFT 배치가 없습니다.")
        return
    draft = draft_batches[-1]
    gate = latest("qms_release_gate_*.md", REVIEW)
    proposals = latest("qms_autofix_proposals_*.csv", REVIEW)
    diff_summary = latest("diff_summary_*.csv", REVIEW/"DIFF")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    pkg = APPROVAL / f"APPROVAL_PACKAGE_{ts}"
    pkg.mkdir(parents=True, exist_ok=True)

    files_dir = pkg / "FILES"
    shutil.copytree(draft, files_dir)

    if gate: shutil.copy2(gate, pkg / gate.name)
    if proposals: shutil.copy2(proposals, pkg / proposals.name)
    if diff_summary: shutil.copy2(diff_summary, pkg / diff_summary.name)

    readme = pkg / "APPROVAL_README.md"
    readme.write_text(
        "# 승인대기 패키지\n\n"
        "이 패키지는 자동 검토 결과를 바탕으로 생성된 승인대기용 작업본입니다.\n\n"
        "## 승인 전 확인\n"
        "- 원본과 수정초안 비교\n"
        "- 문서번호 및 Rev 확인\n"
        "- 승인자/승인일 확인\n"
        "- HOLD/FAIL 항목 해소 여부 확인\n"
        "- FINAL 이동 전 Release Gate 재실행\n\n"
        "자동 생성된 초안은 승인 완료 전 배포본으로 사용하지 않습니다.\n",
        encoding="utf-8"
    )
    print(pkg)

if __name__ == "__main__":
    main()
