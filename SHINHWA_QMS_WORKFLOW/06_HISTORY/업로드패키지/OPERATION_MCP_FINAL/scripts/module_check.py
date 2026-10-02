from pathlib import Path
import csv,yaml,sys
from datetime import datetime
from common_extract import extract_text

ROOT=Path(__file__).resolve().parents[1]
CFG=yaml.safe_load((ROOT/"00_CONFIG"/"integrated_rules.yaml").read_text(encoding="utf-8"))
OUT=ROOT/"12_OUTPUT"/"REPORTS"; OUT.mkdir(parents=True,exist_ok=True)
MAP={
"lot":("lot_traceability",ROOT/"11_INPUT"/"LOT"),
"safety":("safety_risk",ROOT/"11_INPUT"/"SAFETY"),
"equipment":("equipment_trial",ROOT/"11_INPUT"/"EQUIPMENT"),
"training":("training",ROOT/"11_INPUT"/"TRAINING"),
"production":("production",ROOT/"11_INPUT"/"PRODUCTION"),
"inventory":("inventory",ROOT/"11_INPUT"/"INVENTORY"),
"quality":("quality",ROOT/"11_INPUT"/"QUALITY")}

def main(key):
    cfg_key,folder=MAP[key]
    required=CFG["integrated_modules"][cfg_key]["required_fields"]
    rows=[]
    for p in folder.rglob("*"):
        if not p.is_file(): continue
        try:
            text=extract_text(p)
            missing=[x for x in required if x.lower() not in text.lower()]
            st="PASS" if not missing else "HOLD"
            rows.append([str(p.relative_to(ROOT)),key,st,"; ".join(missing)])
        except Exception as e:
            rows.append([str(p.relative_to(ROOT)),key,"FAIL",str(e)])
    ts=datetime.now().strftime("%Y%m%d_%H%M%S")
    out=OUT/f"{key}_check_{ts}.csv"
    with out.open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.writer(f); w.writerow(["file","module","status","missing_fields"]); w.writerows(rows)
    print(out)

if __name__=="__main__":
    if len(sys.argv)<2 or sys.argv[1] not in MAP:
        print("usage: module_check.py [lot|safety|equipment|training|production|inventory|quality]")
    else:
        main(sys.argv[1])
