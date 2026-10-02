from pathlib import Path
import re
import csv
import sys
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "01_ORIGINAL"
REVIEW = ROOT / "02_REVIEW"
LOG = ROOT / "99_LOG"

REVIEW.mkdir(exist_ok=True)
LOG.mkdir(exist_ok=True)

DOC_PATTERN = re.compile(
    r"^(SH-(QM|QP|WI|FM)-\d{3}).*?(Rev\.\d{2})",
    re.IGNORECASE
)

ALLOWED_EXT = {".docx", ".xlsx", ".xlsm", ".pdf", ".pptx", ".txt", ".md"}

def classify_file(path: Path):
    result = {
        "file": str(path.relative_to(ROOT)),
        "document_no": "",
        "document_type": "",
        "revision": "",
        "status": "PASS",
        "issues": []
    }

    if path.suffix.lower() not in ALLOWED_EXT:
        result["status"] = "SKIP"
        result["issues"].append("지원하지 않는 확장자")
        return result

    m = DOC_PATTERN.search(path.stem)
    if not m:
        result["status"] = "FAIL"
        result["issues"].append("파일명에서 SH-QM/QP/WI/FM 문서번호 또는 Rev 형식을 찾지 못함")
        return result

    result["document_no"] = m.group(1).upper()
    result["document_type"] = m.group(2).upper()
    result["revision"] = m.group(3)

    if not re.fullmatch(r"Rev\.\d{2}", result["revision"]):
        result["status"] = "FAIL"
        result["issues"].append("Rev 형식 오류")

    if "FINAL" in path.stem.upper() and "APPROVED" not in path.stem.upper():
        result["status"] = "HOLD"
        result["issues"].append("FINAL 표기 문서이나 승인상태를 파일명만으로 확인할 수 없음")

    return result

def main():
    files = [p for p in ORIGINAL.rglob("*") if p.is_file()]
    rows = [classify_file(p) for p in files]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REVIEW / f"qms_review_{timestamp}.csv"

    with report_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["file", "document_no", "document_type", "revision", "status", "issues"])
        for r in rows:
            writer.writerow([
                r["file"],
                r["document_no"],
                r["document_type"],
                r["revision"],
                r["status"],
                " | ".join(r["issues"])
            ])

    passed = sum(r["status"] == "PASS" for r in rows)
    held = sum(r["status"] == "HOLD" for r in rows)
    failed = sum(r["status"] == "FAIL" for r in rows)
    skipped = sum(r["status"] == "SKIP" for r in rows)

    print(f"[QMS REVIEW COMPLETE]")
    print(f"PASS: {passed}")
    print(f"HOLD: {held}")
    print(f"FAIL: {failed}")
    print(f"SKIP: {skipped}")
    print(f"REPORT: {report_path}")

if __name__ == "__main__":
    main()
