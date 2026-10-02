from pathlib import Path
import shutil,sys
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]
TYPES={"internal":"INTERNAL","customer":"CUSTOMER","certification":"CERTIFICATION"}
if len(sys.argv)<2 or sys.argv[1] not in TYPES:
    print("usage: make_audit_package.py [internal|customer|certification]"); raise SystemExit(1)
kind=TYPES[sys.argv[1]]
base=ROOT/"14_AUDIT"/kind
pkg=base/f"AUDIT_PACKAGE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
pkg.mkdir(parents=True,exist_ok=True)
for src_dir,name in [
    (ROOT/"02_QMS_REVIEW","QMS_REVIEW"),
    (ROOT/"12_OUTPUT"/"REPORTS","MODULE_REPORTS"),
    (ROOT/"12_OUTPUT"/"ACTION_ITEMS","ACTION_ITEMS"),
    (ROOT/"13_MANAGEMENT"/"WEEKLY","WEEKLY"),
    (ROOT/"13_MANAGEMENT"/"MONTHLY","MONTHLY"),
]:
    dst=pkg/name
    dst.mkdir(exist_ok=True)
    for p in sorted(src_dir.glob("*"))[-10:]:
        if p.is_file(): shutil.copy2(p,dst/p.name)
(pkg/"AUDIT_README.md").write_text(f"""# {kind} AUDIT PACKAGE

생성일: {datetime.now().isoformat(timespec='seconds')}

포함:
- QMS 최신 검토결과
- 통합 운영 점검결과
- 미결 조치사항
- 주간/월간 관리보고

실제 심사 제출 전 최신성 및 승인상태를 확인하세요.
""",encoding="utf-8")
print(pkg)
