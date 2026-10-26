import os, re, subprocess, sys, pathlib, zipfile
import openpyxl

BASE = pathlib.Path(r"C:\q\SHINHWA_QMS_WORKFLOW")
APPROVER = "이사"
WAIT = BASE / "04_APPROVAL" / "승인대기"
DONE = BASE / "04_APPROVAL" / "승인완료"
EDIT = BASE / "03_EDIT" / "수정완료"
OLD = ["문서상태: 신규양식 초안(미승인)", "문서상태: 개정초안(미승인)", "문서상태: 초안(작성중)"]
UNFINISHED = "확정 필요"

args = sys.argv[1:]
force = "--force" in args
do_git = "--git" in args
keys = [a for a in args if not a.startswith("--")]

env = dict(os.environ, PYTHONIOENCODING="utf-8")


def run(*a):
    print(">>", " ".join(a))
    r = subprocess.run([sys.executable, str(BASE / "scripts" / "qms_workflow.py"), *a],
                       cwd=BASE, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env)
    out = (r.stdout or "") + (r.stderr or "")
    print(out)
    return out


_ENCODERS = (
    lambda t: t,
    lambda t: "".join(f"&#{ord(c)};" if ord(c) > 127 else c for c in t),
    lambda t: "".join(f"&#x{ord(c):x};" if ord(c) > 127 else c for c in t),
    lambda t: "".join(f"&#x{ord(c):X};" if ord(c) > 127 else c for c in t),
)


def mark_approved_zip(src, dst):
    """xlsx 압축 파일 안의 문자열만 바꿔 저장한다(사진·도형 등 다른 부분은 그대로 복사).
    openpyxl 로 저장하면 사진이 빠질 수 있어 이 방식을 먼저 쓴다. 바꾼 횟수를 돌려준다."""
    n = 0
    with zipfile.ZipFile(src) as zi, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
        for item in zi.infolist():
            data = zi.read(item.filename)
            if item.filename.startswith("xl/") and item.filename.endswith(".xml") \
                    and "/media/" not in item.filename:
                text = data.decode("utf-8")
                for o in OLD:
                    # 글자가 그대로이거나 &#숫자; 로 저장된 두 경우 모두 처리
                    for enc in _ENCODERS:
                        k = text.count(enc(o))
                        if k:
                            text = text.replace(enc(o), enc("문서상태: 승인완료"))
                            n += k
                data = text.encode("utf-8")
            zo.writestr(item, data)
    return n


def count_old(p):
    wb = openpyxl.load_workbook(p)
    return sum(1 for ws in wb for row in ws.iter_rows() for c in row
               if isinstance(c.value, str) for o in OLD if o in c.value)


def next_name(p):
    base = re.sub(r"_수정본\d*(_v\d+)?$", "", p.stem)
    nums = []
    for d in (EDIT, WAIT, DONE):
        for q in d.glob(base + "_수정본*" + p.suffix):
            m = re.search(r"_수정본(\d*)", q.stem)
            nums.append(int(m.group(1) or 1))
    return f"{base}_수정본{max(nums or [1]) + 1}{p.suffix}"


targets = sorted(p for p in WAIT.glob("*.xlsx")
                 if not keys or any(k in p.name for k in keys))
if not targets:
    sys.exit("승인대기에 대상 .xlsx 가 없습니다.")

plan, skipped = [], []
for p in targets:
    wb = openpyxl.load_workbook(p)
    n_un = sum(1 for ws in wb for row in ws.iter_rows() for c in row
               if isinstance(c.value, str) and UNFINISHED in c.value)
    if n_un and not force:
        skipped.append((p.name, f"'확정 필요' {n_un}곳 남음"))
        continue
    plan.append((p, next_name(p)))

print("\n=== 승인 처리 대상 ===")
for p, new in plan:
    print(" -", p.name, "→", new)
if skipped:
    print("\n=== 건너뜀(미완성) ===")
    for n, why in skipped:
        print(" -", n, ":", why)
if not plan:
    sys.exit("처리할 파일이 없습니다. (미완성 양식을 승인하려면 --force)")

print("\n승인일 2026-09-01, 승인자:", APPROVER)
if input("위 문서를 '승인완료'로 표기하고 승인·배포합니다. 진행하려면 '승인' 을 입력: ").strip() != "승인":
    sys.exit("취소했습니다.")

# 1) 승인완료 표기 후 새 이름으로 저장 (사진·도형 보존을 위해 압축 파일 안에서 직접 바꾼다)
for p, new in plan:
    expected = count_old(p)
    n = mark_approved_zip(p, EDIT / new)
    if n != expected:
        # 셀 값으로 읽은 횟수와 다르면 안전하게 기존 방식으로 저장(사진이 빠질 수 있음)
        print(f"!! {new}: 압축 안 치환 {n}곳 ≠ 셀 {expected}곳 → openpyxl 방식으로 저장(사진 확인 필요)")
        wb = openpyxl.load_workbook(p)
        n = 0
        for ws in wb:
            for row in ws.iter_rows():
                for c in row:
                    if isinstance(c.value, str):
                        for o in OLD:
                            if o in c.value:
                                c.value = c.value.replace(o, "문서상태: 승인완료")
                                n += 1
        wb.save(EDIT / new)
    print(f"{new}: 문서상태 {n}곳 변경")

# 2) 재검증
run("recheck")
ok = []
for p, new in plan:
    if (WAIT / new).exists():
        ok.append(new)
    else:
        print("!! recheck 통과 못 함(승인대기에 없음), 건너뜀:", new)
if not ok:
    sys.exit("recheck 를 통과한 파일이 없습니다. 02_REVIEW 의 수정필요사항을 확인하세요.")
if input(f"recheck 통과 {len(ok)}개. 승인 처리를 계속하려면 Enter, 중단은 Ctrl+C: ") is None:
    pass

# 3) 승인 처리
results = []
for new in ok:
    run("approve", new)
    run("sign", new, APPROVER)
    out = run("finalize", new)
    results.append((new, "[FINAL" in out))
run("integrity")
run("finalreport")

print("\n=== 결과 ===")
for n, good in results:
    print(" ", "배포 완료" if good else "!! 확인 필요", n)
print("건너뜀:", len(skipped), "개")

if do_git:
    for cmd in (["git", "add", "-A"],
                ["git", "commit", "-m", "승인·배포(finalize) 일괄 처리"],
                ["git", "pull", "--no-rebase", "origin", "claude/shinhwa-qms-workflow-54alyc"],
                ["git", "push", "origin", "claude/shinhwa-qms-workflow-54alyc"]):
        print(">>", " ".join(cmd))
        print(subprocess.run(cmd, cwd=BASE, capture_output=True, text=True,
                             encoding="utf-8", errors="replace").stdout)