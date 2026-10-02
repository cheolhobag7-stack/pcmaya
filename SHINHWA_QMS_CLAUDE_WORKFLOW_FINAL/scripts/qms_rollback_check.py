from pathlib import Path
import shutil, re
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT/"05_FINAL"/"RELEASED"
HISTORY = ROOT/"06_HISTORY"/"ARCHIVE"
ROLLBACK = ROOT/"06_HISTORY"/"ROLLBACK_BACKUP"

def main():
    backups = sorted(ROLLBACK.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not backups:
        print("롤백 백업이 없습니다.")
        return
    print("롤백은 자동 실행하지 않습니다.")
    print("가장 최근 백업 후보:")
    for p in backups[:10]:
        print("-", p.name)
    print("필요 시 해당 파일을 검토 후 수동 복원하세요.")

if __name__ == "__main__":
    main()
