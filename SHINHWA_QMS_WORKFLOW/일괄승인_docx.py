"""승인대기의 Word(.docx) 문서를 '승인완료'로 표기하고 승인·배포한다 (일괄승인.py 는 .xlsx 만 처리).
사용: python 일괄승인_docx.py [키워드] [--git]
승인일 2026-09-01(전제, 사용자 지시), 승인자: 이사. 확인 후 '승인' 입력 시에만 진행한다."""
import os, re, subprocess, sys, pathlib
import docx

BASE = pathlib.Path(r"C:\q\SHINHWA_QMS_WORKFLOW")
APPROVER = "이사"
WAIT = BASE / "04_APPROVAL" / "승인대기"
DONE = BASE / "04_APPROVAL" / "승인완료"
EDIT = BASE / "03_EDIT" / "수정완료"
OLD = ["문서상태: 신규양식 초안(미승인)", "문서상태: 개정초안(미승인)", "문서상태: 초안(작성중)"]
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

args = sys.argv[1:]
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


def next_name(p):
    base = re.sub(r"_수정본\d*(_v\d+)?$", "", p.stem)
    nums = []
    for d in (EDIT, WAIT, DONE):
        for q in d.glob(base + "_수정본*" + p.suffix):
            m = re.search(r"_수정본(\d*)", q.stem)
            nums.append(int(m.group(1) or 1))
    return f"{base}_수정본{max(nums or [1]) + 1}{p.suffix}"


def mark(root):
    n = 0
    for p in root.iter(W + "p"):
        ts = list(p.iter(W + "t"))
        if not ts:
            continue
        full = "".join(t.text or "" for t in ts)
        new = full
        for o in OLD:
            new = new.replace(o, "문서상태: 승인완료")
        if new == full and full.strip() == "개정초안(미승인)":
            new = "승인완료"
        if new != full:
            ts[0].text = new
            ts[0].set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            for t in ts[1:]:
                t.text = ""
            n += 1
    return n


targets = sorted(p for p in WAIT.glob("*.docx") if not keys or any(k in p.name for k in keys))
if not targets:
    sys.exit("승인대기에 대상 .docx 가 없습니다.")
plan = [(p, next_name(p)) for p in targets]
print("\n=== 승인 처리 대상(Word) ===")
for p, new in plan:
    print(" -", p.name, "→", new)
print("\n승인일 2026-09-01, 승인자:", APPROVER)
if input("위 문서를 '승인완료'로 표기하고 승인·배포합니다. 진행하려면 '승인' 을 입력: ").strip() != "승인":
    sys.exit("취소했습니다.")

for p, new in plan:
    d = docx.Document(p)
    n = mark(d.element.body)
    for s in d.sections:
        for part in (s.header, s.footer, s.first_page_header, s.first_page_footer):
            try:
                n += mark(part._element)
            except Exception:
                pass
    d.save(EDIT / new)
    print(f"{new}: 문서상태 {n}곳 변경")

run("recheck")
ok = []
for p, new in plan:
    if (WAIT / new).exists():
        ok.append(new)
    else:
        print("!! recheck 통과 못 함(승인대기에 없음), 건너뜀:", new)
if not ok:
    sys.exit("recheck 를 통과한 파일이 없습니다. 02_REVIEW 의 수정필요사항을 확인하세요.")
input(f"recheck 통과 {len(ok)}개. 승인 처리를 계속하려면 Enter, 중단은 Ctrl+C: ")

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

if do_git:
    for cmd in (["git", "add", "-A"], ["git", "commit", "-m", "승인·배포(finalize) Word 문서 처리"],
                ["git", "pull", "--no-rebase", "origin", "claude/shinhwa-qms-workflow-54alyc"],
                ["git", "push", "origin", "claude/shinhwa-qms-workflow-54alyc"]):
        print(">>", " ".join(cmd))
        print(subprocess.run(cmd, cwd=BASE, capture_output=True, text=True,
                             encoding="utf-8", errors="replace").stdout)
