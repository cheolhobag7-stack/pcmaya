from pathlib import Path
import csv
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]
SOURCES=[ROOT/"02_QMS_REVIEW",ROOT/"12_OUTPUT"/"REPORTS"]
OUT=ROOT/"12_OUTPUT"/"ACTION_ITEMS"; OUT.mkdir(parents=True,exist_ok=True)
actions=[]
for folder in SOURCES:
    for p in folder.glob("*.csv"):
        try:
            with p.open("r",encoding="utf-8-sig",newline="") as f:
                for r in csv.DictReader(f):
                    st=r.get("status","")
                    if st in {"HOLD","FAIL"}:
                        actions.append([
                            p.name,
                            r.get("file") or r.get("document_no") or "",
                            st,
                            r.get("issues") or r.get("missing_fields") or "",
                            "",
                            "",
                            "OPEN"
                        ])
        except: pass
out=OUT/f"action_items_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
with out.open("w",newline="",encoding="utf-8-sig") as f:
    w=csv.writer(f); w.writerow(["source","target","status","issue","owner","due_date","action_status"]); w.writerows(actions)
print(out)
