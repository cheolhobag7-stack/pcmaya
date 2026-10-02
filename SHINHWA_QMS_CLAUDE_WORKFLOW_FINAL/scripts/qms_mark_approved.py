from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT/"04_APPROVAL"/"PACKAGES"

def main():
    pkgs = sorted(PACKAGES.glob("APPROVAL_PACKAGE_*"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not pkgs:
        print("승인대기 패키지가 없습니다.")
        return
    pkg = pkgs[-1]
    marker = pkg/"APPROVED.txt"
    if marker.exists():
        print(marker)
        return
    marker.write_text(
        "APPROVED\n"
        f"approved_at={datetime.now().isoformat(timespec='seconds')}\n"
        "note=사용자가 승인 완료를 확인한 후 생성된 표시파일\n",
        encoding="utf-8"
    )
    print(marker)

if __name__ == "__main__":
    main()
