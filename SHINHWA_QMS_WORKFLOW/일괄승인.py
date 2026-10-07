import openpyxl, subprocess, sys, pathlib

BASE = pathlib.Path(r"C:\q\SHINHWA_QMS_WORKFLOW")
APPROVER = "이사"
JOBS = [
    ("SH-FM-071_부적합품관련관리기록_Rev00_수정본3.xlsx", "SH-FM-071_부적합품관련관리기록_Rev00_수정본4.xlsx"),
    ("SH-FM-101-121_현장작성양식_Rev03_수정본8.xlsx", "SH-FM-101-121_현장작성양식_Rev03_수정본9.xlsx"),
]
OLD = ["문서상태: 신규양식 초안(미승인)", "문서상태: 개정초안(미승인)"]


def run(*args):
    print(">>", " ".join(args))
    subprocess.run([sys.executable, str(BASE / "scripts" / "qms_workflow.py"), *args], cwd=BASE)


def find_source(name):
    for d in (BASE / "04_APPROVAL" / "승인대기", BASE / "03_EDIT" / "수정완료"):
        p = d / name
        if p.exists():
            return p
    raise SystemExit("원본 파일을 찾을 수 없습니다: " + name)


for src, dst in JOBS:
    wb = openpyxl.load_workbook(find_source(src))
    n = 0
    for ws in wb:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str):
                    for o in OLD:
                        if o in c.value:
                            c.value = c.value.replace(o, "문서상태: 승인완료")
                            n += 1
    wb.save(BASE / "03_EDIT" / "수정완료" / dst)
    print(dst + ": 문서상태 " + str(n) + "곳 변경")

run("recheck")
input("recheck 결과가 모두 종합 판정 PASS 인지 확인한 뒤 Enter (아니면 Ctrl+C): ")

for _, dst in JOBS:
    run("approve", dst)
    run("sign", dst, APPROVER)
    run("finalize", dst)
run("integrity")
run("finalreport")