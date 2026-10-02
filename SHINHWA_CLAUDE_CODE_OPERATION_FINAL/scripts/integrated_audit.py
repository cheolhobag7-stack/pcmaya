from pathlib import Path
import subprocess,sys,csv
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"12_OUTPUT"/"REPORTS"; OUT.mkdir(parents=True,exist_ok=True)
rows=[]
scripts=[("QMS",[sys.executable,str(ROOT/"scripts"/"qms_audit.py")])]
for m in ["lot","safety","equipment","training","production","inventory","quality"]:
    scripts.append((m.upper(),[sys.executable,str(ROOT/"scripts"/"module_check.py"),m]))
for area,cmd in scripts:
    p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
    rows.append([area,"PASS" if p.returncode==0 else "FAIL",(p.stdout or p.stderr).strip()])
ts=datetime.now().strftime("%Y%m%d_%H%M%S")
out=OUT/f"integrated_audit_{ts}.csv"
with out.open("w",newline="",encoding="utf-8-sig") as f:
    w=csv.writer(f); w.writerow(["area","run_status","result"]); w.writerows(rows)
print(out)
