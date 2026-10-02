from pathlib import Path
import shutil
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"16_BACKUP"; OUT.mkdir(parents=True,exist_ok=True)
name=OUT/f"SHINHWA_BACKUP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.make_archive(str(name),"zip",ROOT,logger=None)
print(str(name)+".zip")
