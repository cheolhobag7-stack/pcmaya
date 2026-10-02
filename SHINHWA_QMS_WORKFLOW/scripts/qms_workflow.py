#!/usr/bin/env python3
"""SHINHWA QMS 문서 워크플로 자동화.

사용법 (SHINHWA_QMS_WORKFLOW 에서):
  python3 scripts/qms_workflow.py run        # 01_ORIGINAL 분류 → 전 항목 검사 → 02_REVIEW / 04_APPROVAL
  python3 scripts/qms_workflow.py recheck    # 03_EDIT/수정완료 재검증
  python3 scripts/qms_workflow.py approve F  # (사람) 04_APPROVAL/승인대기 의 F → 검토완료
  python3 scripts/qms_workflow.py sign F     # (사람) 검토완료 → 승인완료
  python3 scripts/qms_workflow.py gates      # AP-01~04 게이트 양식(FM) 존재 확인
  python3 scripts/qms_workflow.py finalize   # 승인완료 → 05_FINAL + PDF + 배포본 + 06_HISTORY 백업
"""
import csv, json, re, shutil, subprocess, sys, zipfile, datetime as dt
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
D = {k: ROOT / v for k, v in dict(
    cfg="00_CONFIG", orig="01_ORIGINAL", rev="02_REVIEW", edit="03_EDIT", appr="04_APPROVAL",
    final="05_FINAL", hist="06_HISTORY", log="99_LOG").items()}
ERR_DIR = {"문서번호": "문서번호오류", "개정번호": "개정번호오류", "상호참조": "상호참조오류"}
DEFAULT_ERR_DIR = "내용보완필요"
TEXT_EXT = {".docx", ".xlsx", ".txt", ".md", ".csv"}


def cfg(name):
    return yaml.safe_load((D["cfg"] / name).read_text(encoding="utf-8"))

def norm(no):
    """SH- 접두어 제거: SH-FM-066 == FM-066"""
    return re.sub(r"^SH-", "", no) if no else no

def prefix_of(name):
    return re.split(r"[-_ ]", norm(name.upper()))[0]

def now():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(fname, row):
    with open(D["log"] / fname, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(row)

def extract_text(p: Path) -> str:
    """docx/xlsx 는 표준 라이브러리로 텍스트 추출 (외부 패키지 불필요)."""
    ext = p.suffix.lower()
    try:
        if ext == ".docx":
            with zipfile.ZipFile(p) as z:
                names = [n for n in z.namelist() if re.match(r"word/(document|header\d*|footer\d*)\.xml", n)]
                xml = " ".join(z.read(n).decode("utf8", "ignore") for n in names)
            xml = re.sub(r"</w:p>", "\n", xml)
            return re.sub(r"<[^>]+>", "", xml)
        if ext == ".xlsx":
            with zipfile.ZipFile(p) as z:
                parts = [n for n in z.namelist() if n.startswith("xl/sharedStrings") or re.match(r"xl/worksheets/.*\.xml", n)]
                xml = " ".join(z.read(n).decode("utf8", "ignore") for n in parts)
            return re.sub(r"<[^>]+>", " ", xml)
        if ext in {".txt", ".md", ".csv"}:
            return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    return ""   # pdf 등: 본문 검사 불가

def stages_files():
    for stage in ("orig", "rev", "edit", "appr", "final"):
        for p in D[stage].rglob("*"):
            if p.is_file() and p.name != ".gitkeep":
                yield p

def registry(docpat):
    """현재 시스템에 존재하는 문서번호 집합 (상호참조 검사용)."""
    reg = set()
    for p in stages_files():
        reg.update(norm(x) for x in re.findall(docpat, p.name))
    return reg

# ---------------- 1) 자동 분류 ----------------
def classify():
    rules = cfg("qms_rules.yaml")["classify"]
    moved = []
    for p in list(D["orig"].iterdir()):
        if not p.is_file() or p.name == ".gitkeep":
            continue
        typ = rules.get(prefix_of(p.name))
        if not typ:
            log("error_log.csv", [now(), p.name, "분류불가", "파일명 접두어 미등록", "OPEN"])
            dest = D["rev"] / DEFAULT_ERR_DIR; dest.mkdir(exist_ok=True)
            shutil.move(str(p), dest / p.name)
            continue
        (D["orig"] / typ).mkdir(exist_ok=True)
        shutil.move(str(p), D["orig"] / typ / p.name)
        log("workflow_log.csv", [now(), p.name, "", "투입", f"01_ORIGINAL/{typ}", "system", "자동분류"])
        moved.append(D["orig"] / typ / p.name)
    return moved

# ---------------- 2) 검사 ----------------
def validate(p: Path, typ: str):
    """반환: list[(카테고리, 메시지)]"""
    qms, num, cust = cfg("qms_rules.yaml"), cfg("document_number_rules.yaml"), cfg("customer_rules.yaml")
    text = extract_text(p)
    issues = []
    # 문서번호
    m = re.search(num["doc_pattern"], p.name)
    docno = m.group(0) if m else None
    if not docno:
        issues.append(("문서번호", "파일명에서 문서번호를 찾을 수 없음"))
    else:
        pat = num["by_type"].get(typ)
        if pat and not re.match(pat, docno):
            issues.append(("문서번호", f"{docno} 가 {typ} 문서번호 규칙({pat})에 맞지 않음"))
        if text and docno not in text:
            issues.append(("문서번호", f"본문(머리글 포함)에 문서번호 {docno} 가 없음"))
    # Rev
    fm = re.search(num["revision_pattern"], p.name)
    if not fm:
        issues.append(("개정번호", "파일명에 Rev 표기 없음 (예: _Rev.01)"))
    elif text:
        body = set(re.findall(num["revision_pattern"], text))
        if not body:
            issues.append(("개정번호", "본문에 Rev 표기 없음"))
        elif fm.group(1) not in body:
            issues.append(("개정번호", f"파일명 Rev.{fm.group(1)} 와 본문 Rev.{sorted(body)} 불일치"))
    if not text:
        issues.append(("내용보완", "본문 텍스트 추출 불가(PDF/미지원 형식) - 본문 검사 생략, 수동 확인 필요"))
        return docno, issues
    # 회사명/고객사
    if not any(n in text for n in qms["company"]["names"]):
        issues.append(("내용보완", f"회사명({', '.join(qms['company']['names'])}) 미표기"))
    allowed = set(cust.get("customers") or [])
    for c in re.findall(cust["customer_marker"], text):
        if c not in allowed:
            issues.append(("내용보완", f"등록되지 않은 고객사 '{c}' (customer_rules.yaml)"))
    # QP-WI-FM 상호참조
    reg = registry(num["doc_pattern"])
    for ref in sorted({norm(x) for x in re.findall(num["doc_pattern"], text)} - {norm(docno)}):
        if ref not in reg:
            issues.append(("상호참조", f"참조 문서 {ref} 가 시스템에 존재하지 않음"))
    # 필수 항목 + ISO/IATF
    for s in qms["required_sections"].get(typ, []):
        if s not in text:
            issues.append(("내용보완", f"필수 항목 '{s}' 누락"))
    for chk in qms["standards_check"].get(typ, []):
        if chk.get("applies_to_prefix") and docno and not docno.startswith(chk["applies_to_prefix"]):
            continue
        if not any(k in text for k in chk["any_of"]):
            issues.append(("내용보완", f"{chk['clause']}: {'/'.join(chk['any_of'])} 중 하나 필요"))
    # 보존기간
    r = qms["retention"]
    if typ in r["required_for"]:
        mm = re.search(r"보존기간\s*[:：]?\s*(\S+)", text)
        if not mm:
            issues.append(("내용보완", "보존기간 미표기"))
        elif not any(mm.group(1).startswith(a) for a in r["allowed"]):
            issues.append(("내용보완", f"보존기간 '{mm.group(1)}' 허용값 아님 {r['allowed']}"))
    # 결재/승인
    missing = [l for l in qms["approval_labels"] if l not in text]
    if missing:
        issues.append(("내용보완", f"결재란 항목 누락: {', '.join(missing)}"))
    return docno, issues

def route(p: Path, typ: str):
    docno, issues = validate(p, typ)
    name = docno or p.stem
    if issues:
        cats = {c for c, _ in issues}
        folder = next((ERR_DIR[c] for c in ERR_DIR if c in cats), DEFAULT_ERR_DIR)
        report = D["rev"] / "자동검토결과" / f"{p.stem}_검토결과.json"
        report.write_text(json.dumps({"file": p.name, "checked": now(),
            "issues": [{"category": c, "message": m} for c, m in issues]}, ensure_ascii=False, indent=2), encoding="utf-8")
        dest = D["rev"] / folder
        shutil.copy2(p, dest / p.name)
        for c, m in issues:
            log("error_log.csv", [now(), name, c, m, "OPEN"])
        log("workflow_log.csv", [now(), name, "", p.parent.name, f"02_REVIEW/{folder}", "system", f"{len(issues)}건 문제"])
        print(f"[REVIEW ] {p.name}: {len(issues)}건 → 02_REVIEW/{folder}")
    else:
        dest = D["appr"] / "승인대기"
        shutil.copy2(p, dest / p.name)
        log("workflow_log.csv", [now(), name, "", p.parent.name, "04_APPROVAL/승인대기", "system", "검사통과"])
        print(f"[PASS   ] {p.name} → 04_APPROVAL/승인대기")
    return not issues

def run():
    classify()
    for typ_dir in sorted(d for d in D["orig"].iterdir() if d.is_dir()):
        typ = typ_dir.name
        for p in sorted(typ_dir.iterdir()):
            if p.is_file() and p.name != ".gitkeep" and p.suffix.lower() in (TEXT_EXT | {".pdf"}):
                done = D["appr"] / "승인대기" / p.name
                rev = list((D["rev"]).glob(f"*/{p.name}"))
                if done.exists() or rev:   # 이미 처리됨
                    continue
                route(p, typ)

def recheck():
    """03_EDIT/수정완료 → 재검증 → 통과 시 04_APPROVAL, 실패 시 02_REVIEW 로 되돌림."""
    for p in sorted((D["edit"] / "수정완료").iterdir()):
        if not p.is_file() or p.name == ".gitkeep":
            continue
        typ = cfg("qms_rules.yaml")["classify"].get(prefix_of(p.name))
        for old in D["rev"].glob(f"*/{p.name}"):   # 이전 검토본 정리
            old.unlink()
        if route(p, typ or ""):
            shutil.move(str(p), D["hist"] / "이전버전" / f"{p.stem}_수정본_{dt.datetime.now():%Y%m%d%H%M%S}{p.suffix}")
        else:
            p.unlink()

def gates():
    """승인 게이트(AP) 충족 여부: 필요한 양식(FM)이 시스템에 있는지 확인."""
    reg = registry(cfg("document_number_rules.yaml")["doc_pattern"])
    for ap, g in cfg("gate_rules.yaml")["gate"].items():
        forms = g.get("forms") or [g.get("form")]
        miss = [f for f in forms if norm(f) not in reg]
        print(f"{ap} [{g['status']}] " + ("충족" if not miss else f"미비: {', '.join(miss)}"))

def advance(name, src, dst, who_note):
    s = D["appr"] / src / name
    if not s.exists():
        sys.exit(f"{s} 없음")
    shutil.move(str(s), D["appr"] / dst / name)
    log("workflow_log.csv", [now(), name, "", f"04_APPROVAL/{src}", f"04_APPROVAL/{dst}", "human", who_note])
    print(f"{name}: {src} → {dst}")

# ---------------- 최종 처리 ----------------
def to_pdf(src: Path, outdir: Path):
    if src.suffix.lower() == ".pdf":
        shutil.copy2(src, outdir / src.name); return outdir / src.name
    if not shutil.which("soffice"):
        print("  ! soffice 없음: PDF 변환 생략"); return None
    r = subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(outdir), str(src)],
                       capture_output=True, text=True, timeout=180)
    out = outdir / (src.stem + ".pdf")
    if not out.exists():
        print("  ! PDF 변환 실패:", (r.stderr or r.stdout).strip()[-200:])
        return None
    return out

def finalize():
    num = cfg("document_number_rules.yaml")
    for p in sorted((D["appr"] / "승인완료").iterdir()):
        if not p.is_file() or p.name == ".gitkeep":
            continue
        docno = (re.search(num["doc_pattern"], p.name) or [p.stem])[0] if re.search(num["doc_pattern"], p.name) else p.stem
        rev = (re.search(num["revision_pattern"], p.name) or [None, ""])[1]
        sub = "EXCEL" if p.suffix.lower() in (".xlsx", ".xls", ".csv") else "WORD"
        # 같은 문서번호의 기존 최종본 → 06_HISTORY/이전버전
        old_rev = ""
        for old in list((D["final"] / sub).glob(f"{docno}_*")) + list((D["final"] / sub).glob(f"{docno}.*")):
            om = re.search(num["revision_pattern"], old.name)
            old_rev = om.group(1) if om else ""
            (D["hist"] / "이전버전" / docno).mkdir(parents=True, exist_ok=True)
            shutil.move(str(old), D["hist"] / "이전버전" / docno / old.name)
            for oldpdf in (D["final"] / "PDF").glob(f"{old.stem}.pdf"):
                shutil.move(str(oldpdf), D["hist"] / "이전버전" / docno / oldpdf.name)
        shutil.copy2(p, D["final"] / sub / p.name)
        pdf = to_pdf(p, D["final"] / "PDF")
        if pdf:
            stamp = f"{dt.date.today():%Y%m%d}"
            shutil.copy2(pdf, D["final"] / "배포본" / f"{pdf.stem}_배포본_{stamp}.pdf")
        # 백업 (원본 그대로)
        bdir = D["hist"] / "변경이력" / docno; bdir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, bdir / f"{dt.datetime.now():%Y%m%d%H%M%S}_{p.name}")
        log("revision_history.csv", [dt.date.today(), docno, old_rev, rev, "승인 후 최종 발행", "", "승인완료"])
        log("workflow_log.csv", [now(), docno, rev, "04_APPROVAL/승인완료", "05_FINAL", "system",
                                 "PDF/배포본 생성" if pdf else "PDF 변환 실패"])
        p.unlink()
        print(f"[FINAL  ] {p.name} → 05_FINAL/{sub}, PDF{'+배포본' if pdf else ' 없음'}, 06_HISTORY 백업")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "run": run()
    elif cmd == "recheck": recheck()
    elif cmd == "approve" and len(sys.argv) > 2: advance(sys.argv[2], "승인대기", "검토완료", "검토 완료")
    elif cmd == "sign" and len(sys.argv) > 2: advance(sys.argv[2], "검토완료", "승인완료", "승인")
    elif cmd == "finalize": finalize()
    elif cmd == "gates": gates()
    else: print(__doc__)
