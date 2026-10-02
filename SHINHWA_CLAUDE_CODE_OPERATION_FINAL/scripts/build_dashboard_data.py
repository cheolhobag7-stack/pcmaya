from pathlib import Path
import csv,json
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"12_OUTPUT"/"DASHBOARD_DATA"; OUT.mkdir(parents=True,exist_ok=True)
summary={"generated_at":datetime.now().isoformat(timespec="seconds"),"areas":{}}
for folder in [ROOT/"02_QMS_REVIEW",ROOT/"12_OUTPUT"/"REPORTS"]:
    for p in folder.glob("*.csv"):
        try:
            with p.open("r",encoding="utf-8-sig",newline="") as f:
                rows=list(csv.DictReader(f))
            pass_n=sum(r.get("status")=="PASS" for r in rows)
            hold_n=sum(r.get("status")=="HOLD" for r in rows)
            fail_n=sum(r.get("status")=="FAIL" for r in rows)
            summary["areas"][p.stem]={"pass":pass_n,"hold":hold_n,"fail":fail_n,"rows":len(rows)}
        except: pass
out=OUT/f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
out.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
print(out)
