from pathlib import Path
import csv
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"13_MANAGEMENT"/"WEEKLY"; OUT.mkdir(parents=True,exist_ok=True)
ACTIONS=ROOT/"12_OUTPUT"/"ACTION_ITEMS"
files=sorted(ACTIONS.glob("action_items_*.csv"),key=lambda p:p.stat().st_mtime,reverse=True)
rows=[]
if files:
    with files[0].open("r",encoding="utf-8-sig",newline="") as f: rows=list(csv.DictReader(f))
ts=datetime.now().strftime("%Y%m%d")
out=OUT/f"weekly_management_{ts}.md"
lines=["# 주간 통합 운영 보고","",f"- 작성일: {datetime.now().date()}","",f"- 미결 조치: {len(rows)}","","## 우선 확인"]
for r in rows[:30]:
    lines.append(f"- [{r.get('status')}] {r.get('target')} :: {r.get('issue')}")
lines+=["","## 운영 체크","- QMS","- LOT 추적","- 안전/위험성평가","- 설비","- 교육","- 생산","- 재고","- 품질"]
out.write_text("\n".join(lines),encoding="utf-8")
print(out)
