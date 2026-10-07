#!/usr/bin/env python3
"""(주)신화에이치앤티 QMS 문서관리 자동화 (ISO 9001:2015 / IATF 16949:2016).

사용법 (SHINHWA_QMS_WORKFLOW 에서):
  python3 scripts/qms_workflow.py run [--rereview]  # (--rereview: 이미 검토한 파일도 새 보고서로 다시 검토)
  # 01_ORIGINAL 분류 → 17개 항목 검토 → 02_REVIEW(+수정후보) / 04_APPROVAL
  python3 scripts/qms_workflow.py recheck    # 03_EDIT/수정완료 재검증
  python3 scripts/qms_workflow.py approve F  # (사람) 승인대기 → 검토완료
  python3 scripts/qms_workflow.py sign F     # (사람) 검토완료 → 승인완료
  python3 scripts/qms_workflow.py diff 수정본 [원본]  # 원본↔수정본 DIFF → 03_EDIT/DIFF/ (원본 생략 시 자동 탐색)
  python3 scripts/qms_workflow.py package F  # 04_APPROVAL/PACKAGES 승인 패키지 생성(Gate/검토요약/DIFF/체크리스트)
  python3 scripts/qms_workflow.py fmregister # 양식 워크북의 신규 FM 번호를 FM Master 새 파일에 등록(원본 유지, openpyxl 필요)
  python3 scripts/qms_workflow.py fulloperation   # 전체 운영(QMS 사이클→통합 점검→조치사항→대시보드→주간 보고, 승인 직전까지)
  python3 scripts/qms_workflow.py inputsync <로컬폴더> [--apply] [--match 키워드1,키워드2]   # 현장 파일을 모듈별로 11_INPUT 에 복사(기본 미리보기, 원본 읽기만)
  python3 scripts/qms_workflow.py makelight   # PC 용 가벼운 ZIP(LIGHT_PACKAGE/SHINHWA_QMS_LIGHT.zip) 생성
  python3 scripts/qms_workflow.py dupscan <폴더> [--only A,B]   # 최상위 폴더 간 중복 조사(이름+크기, 읽기 전용)
  (drivescan/organizeplan/inputsync 공통 옵션: --only 폴더A,폴더B  --exclude 폴더C  ← 최상위 폴더 이름)
  python3 scripts/qms_workflow.py drivescan <폴더>   # 분류 키워드 조정용 현황 조사(읽기 전용, 이름만 집계)
  python3 scripts/qms_workflow.py foldertree <루트>                       # 정리용 표준 폴더 구조 생성
  python3 scripts/qms_workflow.py organizeplan <원본폴더> <루트> [--apply]  # 파일을 표준 구조로 복사 계획(기본 미리보기, 원본 유지)
  python3 scripts/qms_workflow.py mcphealth | mcpsafestart   # MCP 상태·보안 점검(읽기 전용) / 점검 후 전체 운영
  python3 scripts/qms_workflow.py qmsaudit | integratedaudit | modulecheck <lot|safety|equipment|training|production|inventory|quality>
  python3 scripts/qms_workflow.py collectactions | dashboarddata | weeklyreport | monthlyreport
  python3 scripts/qms_workflow.py auditpackage <internal|customer|certification> | customerresponse | backupworkspace
  python3 scripts/qms_workflow.py sqdrafts [우선순위]  # SQ 필요서류 양식 초안(기본 '높음') → 03_EDIT/AUTO_DRAFT/SQ_*_초안/
  python3 scripts/qms_workflow.py sqnumber   # SQ안 FM번호 → 정식 SH-FM 번호 배정(대응표·SQ 사본·FM Master 새 파일)
  python3 scripts/qms_workflow.py sqaudit    # SQ mark 필요서류 리스트 ↔ 문서체계 대조 → 07_AUDIT/고객심사/
  python3 scripts/qms_workflow.py fullcycle  # 승인 직전까지 전체 사이클(감사→AUTO_DRAFT→재감사→Gate→패키지). 승인/배포는 사람이
  python3 scripts/qms_workflow.py fullaudit  # 전체 자동감사(신규 검색→점검→상호참조→대장→Release Gate)
  python3 scripts/qms_workflow.py releasegate # 종합 Release Gate(PASS/HOLD/FAIL) → 02_REVIEW/qms_release_gate.md
  python3 scripts/qms_workflow.py ledger     # 문서관리대장 ↔ 실제 파일 대조 → 02_REVIEW/qms_ledger_check.md
  python3 scripts/qms_workflow.py gatecheck  # 04_APPROVAL 문서의 FINAL 배포 전 Gate(G1~G8) 표
  python3 scripts/qms_workflow.py crosscheck # QM/QP/WI/FM 상호참조 종합 점검 → 02_REVIEW/qms_crosscheck_summary.md
  python3 scripts/qms_workflow.py scan       # 신규 문서 검색
  python3 scripts/qms_workflow.py status     # 04_APPROVAL 문서별 FINAL 가능 여부
  python3 scripts/qms_workflow.py gates      # AP-01~04 게이트 양식 존재 확인
  python3 scripts/qms_workflow.py finalreport # 릴리스 현황 + 무결성 → 05_FINAL/DISTRIBUTION/FINAL_RELEASE_REPORT_*.md
  python3 scripts/qms_workflow.py rollbackcheck # 롤백 백업 후보 목록(자동 복원 없음)
  python3 scripts/qms_workflow.py integrity  # 05_FINAL/RELEASED 전체 SHA-256 무결성 검사
  python3 scripts/qms_workflow.py finalize   # 승인완료 재검증 → 05_FINAL + PDF + 배포본 + 06_HISTORY
  python3 scripts/qms_workflow.py splitpdf F # 양식 워크북(xlsx)을 시트(양식)별 PDF 로 분리(LibreOffice 필요; 승인·릴리스본만 배포용, 그 외는 '미승인_' 미리보기)

절대 규칙(코드로 강제):
  - 원본은 삭제/덮어쓰기 하지 않는다. 단계 이동은 모두 '복사'이며, 기존 파일과 이름이 겹치면 _vN 으로 새로 저장한다.
    (01_ORIGINAL 루트에 투입된 파일을 유형 폴더로 정리하는 것만 같은 01_ORIGINAL 안의 이동이다.)
  - 수정본/수정후보는 항상 새 파일(03_EDIT/수정중)이며 모든 생성은 revision_history.csv 에 기록한다.
  - 문서번호 오류가 하나라도 있으면 FINAL 이동 금지. 검토 이슈가 있으면 FINAL 이동 금지.
  - 승인(문서상태=승인완료 + 사람의 sign) 전 문서는 배포본을 만들지 않는다.
  - 폐기 문서 참조는 오류. 확정되지 않은 값은 임의로 만들지 않고 '[확인 필요]'로 표시한다.
"""
import collections, csv, hashlib, html, os, json, re, shutil, subprocess, sys, zipfile, datetime as dt
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
D = {k: ROOT / v for k, v in dict(
    cfg="00_CONFIG", orig="01_ORIGINAL", rev="02_REVIEW", edit="03_EDIT", appr="04_APPROVAL",
    final="05_FINAL", hist="06_HISTORY", log="99_LOG").items()}
ERR_DIR = {"문서번호": "문서번호오류", "개정번호": "개정번호오류", "상호참조": "상호참조오류"}
DEFAULT_ERR_DIR = "내용보완필요"
TEXT_EXT = {".docx", ".xlsx", ".txt", ".md", ".csv"}
UNCONFIRMED = "[확인 필요]"
AUX_DIRS = [D["edit"] / "AUTO_DRAFT", D["edit"] / "DIFF", D["appr"] / "PACKAGES", D["final"] / "RELEASED", D["final"] / "DISTRIBUTION"]   # 문서 레지스트리/중복검사에서 제외
MASTER = "MASTER_REF"   # SH_ 로 시작하는 관리자료(대장/마스터/계획) 분류 폴더


# ---------------- 공통 ----------------
def cfg(name):
    return yaml.safe_load((D["cfg"] / name).read_text(encoding="utf-8"))

def now():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def norm(no):
    """SH- 접두어 제거: SH-FM-066 == FM-066"""
    return re.sub(r"^SH-", "", no) if no else no

def prefix_of(name):
    return re.split(r"[-_ ]", norm(name.upper()))[0]

def log(fname, row):
    with open(D["log"] / fname, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(row)

def sha(p: Path):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def find_identical(src: Path, dest_dir: Path, name=None):
    """dest_dir 에 같은 이름(또는 _v2, _v3 …)으로 이미 저장된 '내용이 같은' 파일이 있으면 그 경로, 없으면 None."""
    name = name or src.name
    dest, n = dest_dir / name, 2
    while dest.exists():
        if dest.stat().st_size == src.stat().st_size and dest.read_bytes() == src.read_bytes():
            return dest
        dest = dest_dir / f"{Path(name).stem}_v{n}{Path(name).suffix}"
        n += 1
    return None

def safe_copy(src: Path, dest_dir: Path, name=None) -> Path:
    """절대 덮어쓰지 않는 복사. 동일 내용이 이미 있으면 그 경로 반환, 다르면 _vN."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    name = name or src.name
    dest = dest_dir / name
    n = 2
    while dest.exists():
        if dest.read_bytes() == src.read_bytes():
            return dest
        dest = dest_dir / f"{Path(name).stem}_v{n}{Path(name).suffix}"
        n += 1
    shutil.copy2(src, dest)
    return dest

def processed():
    f = D["log"] / "processed_hashes.txt"
    return set(f.read_text().split()) if f.exists() else set()

def mark_processed(h):
    with open(D["log"] / "processed_hashes.txt", "a") as f:
        f.write(h + "\n")

def extract_text(p: Path) -> str:
    """docx/xlsx 는 표준 라이브러리로 텍스트 추출 (외부 패키지 불필요)."""
    ext = p.suffix.lower()
    try:
        if ext == ".docx":
            with zipfile.ZipFile(p) as z:
                names = [n for n in z.namelist() if re.match(r"word/(document|header\d*|footer\d*)\.xml", n)]
                xml = " ".join(z.read(n).decode("utf8", "ignore") for n in names)
            xml = re.sub(r"</w:p>", "\n", xml)
            return html.unescape(re.sub(r"<[^>]+>", "", xml))
        if ext == ".xlsx":
            with zipfile.ZipFile(p) as z:
                parts = [n for n in z.namelist() if n.startswith("xl/sharedStrings") or re.match(r"xl/worksheets/.*\.xml", n)]
                xml = " ".join(z.read(n).decode("utf8", "ignore") for n in parts)
            return html.unescape(re.sub(r"<[^>]+>", " ", xml))
        if ext in {".txt", ".md", ".csv"}:
            return p.read_text(encoding="utf-8", errors="ignore")
        if ext == ".xls":                      # 구형 엑셀: xlrd 가 설치돼 있으면 읽고, 없으면 읽을 수 없음으로 둔다
            try:
                import xlrd
            except ImportError:
                return ""
            wb = xlrd.open_workbook(str(p), on_demand=True)
            out = []
            for sh in wb.sheets():
                for r in range(sh.nrows):
                    out.extend(str(c) for c in sh.row_values(r) if c not in ("", None))
                wb.unload_sheet(sh.name)
            return " ".join(out)
        if ext == ".pdf":
            return pdf_text(p)
    except Exception:
        return ""
    return ""

def unique_path(path: Path) -> Path:
    """기존 파일을 덮어쓰지 않도록 _vN 경로 반환."""
    n, out = 2, path
    while out.exists():
        out = path.with_name(f"{path.stem}_v{n}{path.suffix}")
        n += 1
    return out

_XL_CACHE = {}
def xlsx_sheets(p: Path):
    """{시트명: 텍스트} (shared strings 해석, 표준 라이브러리만 사용)."""
    key = (str(p), p.stat().st_size)
    if key in _XL_CACHE:
        return _XL_CACHE[key]
    import xml.etree.ElementTree as ET
    ln = lambda t: t.rsplit("}", 1)[-1]
    out = {}
    try:
        with zipfile.ZipFile(p) as z:
            names = set(z.namelist())
            ss = []
            if "xl/sharedStrings.xml" in names:
                for si in ET.fromstring(z.read("xl/sharedStrings.xml")):
                    if ln(si.tag) == "si":
                        ss.append("".join(t.text or "" for t in si.iter() if ln(t.tag) == "t"))
            rid2t = {}
            if "xl/_rels/workbook.xml.rels" in names:
                for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels")):
                    rid2t[r.get("Id")] = r.get("Target")
            ridk = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
            for i, sh in enumerate([e for e in ET.fromstring(z.read("xl/workbook.xml")).iter() if ln(e.tag) == "sheet"], 1):
                tgt = (rid2t.get(sh.get(ridk)) or f"worksheets/sheet{i}.xml").lstrip("/")
                tgt = tgt if tgt.startswith("xl/") else "xl/" + tgt
                if tgt not in names:
                    continue
                rows = []
                for row in ET.fromstring(z.read(tgt)).iter():
                    if ln(row.tag) != "row":
                        continue
                    cells = []
                    for c in row:
                        v = next((x for x in c if ln(x.tag) == "v"), None)
                        if c.get("t") == "s" and v is not None and v.text is not None:
                            cells.append(ss[int(v.text)])
                        elif c.get("t") == "inlineStr":
                            cells.append("".join(t.text or "" for t in c.iter() if ln(t.tag) == "t"))
                        elif v is not None and v.text:
                            cells.append(v.text)
                    if cells:
                        rows.append(" ".join(cells))
                out[sh.get("name")] = "\n".join(rows)
    except Exception:
        out = {}
    _XL_CACHE[key] = out
    return out

def split_units(p: Path):
    """여러 양식이 한 파일에 든 워크북 → [(문서번호, 시트텍스트)]. 양식 시트가 2개 미만이면 빈 리스트."""
    if p.suffix.lower() != ".xlsx":
        return []
    full = cfg("document_number_rules.yaml")["unit_sheet_pattern"]
    units = [(n.strip(), t) for n, t in xlsx_sheets(p).items() if re.fullmatch(full, n.strip())]
    return units if len(units) >= 2 else []

def expected_range(name):
    """파일명 'SH-FM-066-069_078-080_094_096_...' → {'SH-FM-066', ...}. 해석 불가 시 빈 집합."""
    toks = name.split("_")
    m = re.match(r"^((?:SH-)?[A-Z]+-)(\d{2,3})(?:-(\d{2,3}))?$", toks[0])
    if not m:
        return set()
    pre, ids = m.group(1), [(m.group(2), m.group(3))]
    for t in toks[1:]:
        mm = re.fullmatch(r"(\d{2,3})(?:-(\d{2,3}))?", t)
        if not mm:
            break
        ids.append((mm.group(1), mm.group(2)))
    out = set()
    for a, b in ids:
        for n in range(int(a), int(b or a) + 1):
            out.add(f"{pre}{n:0{len(a)}d}")
    return out

def pdf_text(p: Path) -> str:
    """PDF 본문: pdftotext(poppler) 우선, 없으면 pypdf(선택 설치). 스캔본(이미지)은 빈 문자열."""
    if shutil.which("pdftotext"):
        r = subprocess.run(["pdftotext", "-layout", str(p), "-"], capture_output=True, timeout=120)
        if r.returncode == 0 and r.stdout.decode("utf-8", "ignore").strip():
            return r.stdout.decode("utf-8", "ignore")
    try:
        from pypdf import PdfReader
        t = "\n\f".join((pg.extract_text() or "") for pg in PdfReader(str(p)).pages)
        return t if t.strip() else ""
    except Exception:
        return ""

def page_toc_flags(p: Path, text: str):
    """(페이지번호 있음, 목차 있음)"""
    if p.suffix.lower() == ".docx":
        try:
            with zipfile.ZipFile(p) as z:
                xml = " ".join(z.read(n).decode("utf8", "ignore") for n in z.namelist()
                               if re.match(r"word/(document|header\d*|footer\d*)\.xml", n))
            page = bool(re.search(r"(instrText[^>]*>\s*PAGE\b|w:instr=\"\s*PAGE\b)", xml)) or bool(PAGE_TXT.search(text))
            toc = bool(re.search(r"instrText[^>]*>\s*TOC\b", xml)) or "목차" in text
            return page, toc
        except Exception:
            pass
    return bool(PAGE_TXT.search(text)), "목차" in text

PAGE_TXT = re.compile(r"(Page\s*\d+\s*(of|/)\s*\d+|\d+\s*/\s*\d+\s*(쪽|페이지|page)|페이지\s*:?\s*\d+)", re.I)


# ---------------- 레지스트리 ----------------
def stage_files(stages=("orig", "rev", "edit", "appr", "final")):
    for st in stages:
        for p in D[st].rglob("*"):
            if p.is_file() and p.name != ".gitkeep" and not any(x in p.parents for x in AUX_DIRS):
                yield p

def registry(docpat):
    """시스템에 존재하는 (폐기 아닌) 문서번호 집합 (상호참조 검사용)."""
    reg = set()
    for p in stage_files():
        reg.update(norm(x) for x in re.findall(docpat, p.name))
        for sheet_no, _ in split_units(p):   # 양식 워크북의 시트(=양식) 번호
            reg.add(norm(sheet_no))
        if "문서관리대장" in p.name or "FM_Master" in p.name:   # 대장/마스터에 등재된 번호도 존재하는 문서로 인정
            reg.update(norm(x) for x in re.findall(docpat, extract_text(p)))
    return reg

def expand_ids(entries):
    """'FM-030~039' → FM-030..FM-039, 단일 번호는 그대로."""
    out = set()
    for e in entries or []:
        m = re.match(r"^((?:SH-)?[A-Z]+-)(\d+)~(\d+)", str(e))
        if m:
            w = len(m.group(2))
            out.update(norm(f"{m.group(1)}{n:0{w}d}") for n in range(int(m.group(2)), int(m.group(3)) + 1))
        else:
            out.add(norm(str(e).split()[0]))
    return out

def obsolete_set(docpat):
    c = cfg("qms_rules.yaml")
    obs = expand_ids(c.get("obsolete_docs")) | expand_ids(c.get("prohibited_references"))
    for p in (D["hist"] / "폐기문서").rglob("*"):
        if p.is_file() and p.name != ".gitkeep":
            obs.update(norm(x) for x in re.findall(docpat, p.name))
    return obs

def duplicates(docpat, p: Path, docno, rev):
    """같은 문서번호+Rev 가 서로 다른 파일명으로 존재하는지 (파이프라인 단계 복사본은 같은 이름이므로 제외)."""
    me = norm(docno)
    others = set()
    for q in stage_files():
        if q.name == p.name or q.suffix.lower() not in (TEXT_EXT | {".pdf"}) \
                or D["rev"] / "자동검토결과" in q.parents or D["edit"] / "수정중" in q.parents:
            continue   # 보고서·수정후보는 문서가 아님
        m = re.search(docpat, q.name)
        r = re.search(cfg("document_number_rules.yaml")["revision_pattern"], q.name)
        stem_name = re.sub(r"(_DRAFT|_수정본\d*|_수정후보.*|_v\d+)+$", "", q.stem)
        if m and norm(m.group(0)) == me and (r.group(1) if r else None) == rev \
                and stem_name != re.sub(r"(_DRAFT|_수정본\d*|_v\d+)+$", "", p.stem):
            others.add(q.name)
    return sorted(others)


# ---------------- 검토 (17개 항목) ----------------
def validate(p: Path, typ: str, final_stage=False, unit=None):
    """반환 (docno, [(카테고리, 메시지, 수정제안)])"""
    qms, num, cust = cfg("qms_rules.yaml"), cfg("document_number_rules.yaml"), cfg("customer_rules.yaml")
    text = unit[1] if unit else extract_text(p)
    issues = []
    add = lambda c, m, f="": issues.append((c, m, f))

    # (1) 문서번호
    m = re.search(num["doc_pattern"], unit[0] if unit else p.name)
    docno = m.group(0) if m else None
    if not docno:
        add("문서번호", "파일명에서 문서번호를 찾을 수 없음", f"파일명 앞에 문서번호 부여 {UNCONFIRMED}")
    else:
        pat = num["by_type"].get(typ)
        if pat and not re.match(pat, docno):
            fix = f"SH-{docno} 로 접두어 보완 (번호 자체는 {UNCONFIRMED})" if not docno.startswith("SH-") else f"규칙 {pat} 에 맞게 번호 확인 {UNCONFIRMED}"
            add("문서번호", f"{docno} 가 {typ} 문서번호 규칙({pat})에 맞지 않음", fix)
        if text:
            if docno not in text:
                add("문서번호", f"본문(머리글 포함)에 문서번호 {docno} 가 없음", f"본문 머리글에 {docno} 표기")
            fld = re.search(r"문서번호\s*[:：]\s*(\S+)", text)
            if fld and norm(fld.group(1)) != norm(docno):
                add("문서번호", f"문서번호 불일치: 파일명 {docno} ≠ 본문 {fld.group(1)}", f"어느 쪽이 맞는지 확정 필요 {UNCONFIRMED}")

    # (4) Rev
    fm = re.search(num["revision_pattern"], p.name)
    rev = fm.group(1) if fm else None
    if not fm:
        add("개정번호", "파일명에 Rev 표기 없음", f"파일명에 _Rev.NN 추가 (초기 문서는 {num['initial_revision']})")
    elif text:
        body = set(re.findall(num["revision_pattern"], text))
        if not body:
            add("개정번호", "본문에 Rev 표기 없음", f"본문에 Rev.{rev} 표기")
        elif rev not in body:
            add("개정번호", f"파일명 Rev.{rev} 와 본문 Rev.{sorted(body)} 불일치", f"올바른 Rev 확정 필요 {UNCONFIRMED}")

    if not text:
        add("확인필요", "본문 텍스트 추출 불가(스캔형 PDF/미지원 형식) - 자동판정 불가, 수동 확인 필요(HOLD)")
        return docno, issues, False

    # (2) 회사명
    if not any(n in text for n in qms["company"]["names"]):
        add("내용보완", f"회사명 미표기 ({', '.join(qms['company']['names'])})", f"회사명 {qms['company']['name']} 표기")

    # (3) 문서명
    nm = re.match(r"^(?:SH-)?[A-Za-z]+(?:-[\w]+)*?_(.+?)_Rev", p.name) if docno and not unit else None
    title = nm.group(1) if nm else None
    if unit:
        pass   # 양식(시트) 단위는 파일명 문서명 대신 시트 자체를 검토
    elif not title:
        add("내용보완", "파일명에서 문서명을 찾을 수 없음 (형식: 문서번호_문서명_Rev.NN)", f"문서명 {UNCONFIRMED}")
    elif title not in text:
        add("내용보완", f"본문에 문서명 '{title}' 없음", "본문 제목과 파일명 문서명 일치 필요")

    # 승인 상태 표지: '문서상태: 승인완료' 필드 또는 머리글의 ACTIVE/APPROVED/승인완료 표기 (양식 헤더)
    st = re.search(rf"{qms['document_status']['field']}\s*[:：]\s*(\S+)", text)
    status = st.group(1) if st else None
    mk = re.search(qms["document_status"]["header_marker"], text[:600])
    approved = status in qms["document_status"]["approved_values"] or bool(mk)

    # (5) 제정/개정일: 승인(ACTIVE 등) 표기가 있거나 FINAL 단계에서만 필수. 사용승인 전 양식은 날짜 미기재 허용
    df = qms["date_fields"]
    key = df["initial"] if rev == "00" else df["revised"]
    date_required = approved or final_stage or not qms["date_fields"].get("optional_before_approval", False)
    dm = re.search(rf"{key}\s*[:：]?\s*(\d{{4}})[.\-/]\s?(\d{{1,2}})[.\-/]\s?(\d{{1,2}})", text) if rev is not None else None
    if rev is not None:
        if not dm and not date_required:
            pass   # 승인 전 양식: 제정일 공란 허용
        elif not dm:
            add("내용보완", f"{key} 미표기 또는 날짜 형식 오류 (YYYY-MM-DD)", f"{key} 기재 {UNCONFIRMED}")
        else:
            try:
                d = dt.date(int(dm[1]), int(dm[2]), int(dm[3]))
                if d > dt.date.today():
                    add("내용보완", f"{key} {d} 가 미래 날짜", f"{key} 확인 {UNCONFIRMED}")
            except ValueError:
                add("내용보완", f"{key} 날짜가 유효하지 않음", f"{key} 확인 {UNCONFIRMED}")

    # (6) 작성/검토/승인 상태
    labels = list(qms["approval_labels"])
    if unit:
        # 양식별 결재 방식: 목록(안내) 시트의 '결재 방식'(예: 작성·확인 / 작성·검토·승인)을 따른다.
        ctx = unit[2] if len(unit) > 2 else ""
        sm = None
        for line in ctx.splitlines():
            if re.search(rf"(?:SH-)?{re.escape(norm(docno or ''))}(?!\d)", line):
                sm = re.search(r"작성((?:[·/](?:검토|확인|승인))*)\s+Rev\.?\d{2}", line) or sm
        if sm:
            labels = ["작성"] + re.findall(r"검토|확인|승인", sm.group(1))
        elif mk and qms["approval_by_header_marker"].get("skip_label_check"):
            labels = []   # 대장/집계표형 양식: 개별 결재란 없이 ACTIVE(공식 게이트 승인)로 관리
    missing = [l for l in labels if l not in text]
    if missing:
        add("내용보완", f"결재란 항목 누락: {', '.join(missing)}", f"결재란({'/'.join(labels)}) 보완")
    if final_stage and not approved:
        add("내용보완", f"문서상태가 승인완료가 아님 ({status or '미표기'}) - FINAL/배포 불가", "승인 절차 완료 후 문서상태 갱신")

    # (7)(16) 상호참조 / 폐기 문서 참조
    reg, obs = registry(num["doc_pattern"]), obsolete_set(num["doc_pattern"])
    refs = {norm(x) for x in re.findall(num["doc_pattern"], text)} - {norm(docno)}
    exempt = norm(docno or "") in {norm(x) for x in qms.get("prohibited_reference_exceptions", [])}
    for ref in sorted(refs):
        if ref in obs and exempt:
            continue   # 예외 문서(예: 구형 번호 대조 계획표)는 폐기/참조금지 번호 참조를 허용
        if ref in obs:
            add("상호참조", f"폐기/참조금지 문서 {ref} 를 참조함", "대체 문서로 교체 (대체 문서번호 " + UNCONFIRMED + ")")
        elif ref not in reg:
            add("상호참조", f"참조 문서 {ref} 가 시스템에 존재하지 않음", "참조 문서번호 확인 또는 해당 문서 등록")

    # 필수 항목 / (8)(9) ISO·IATF 요구사항
    for s in qms["required_sections"].get(typ, []):
        if s not in text:
            add("내용보완", f"필수 항목 '{s}' 누락", f"'{s}' 항목 작성")
    for chk in qms["standards_check"].get(typ, []):
        if chk.get("applies_to_prefix") and docno and not norm(docno).startswith(chk["applies_to_prefix"]):
            continue
        if not any(k in text for k in chk["any_of"]):
            add("내용보완", f"{chk['clause']}: {'/'.join(chk['any_of'])} 중 하나 필요", "해당 요구사항 반영")

    # (10) APQP/PPAP/PFMEA/CP/SPC/MSA 연계 (양식 시트는 목록 시트에 적힌 연계 QP도 인정)
    link_refs = set(refs)
    if unit and len(unit) > 2:
        for line in unit[2].splitlines():
            if re.search(rf"(?:SH-)?{re.escape(norm(docno or ''))}(?!\d)", line):
                link_refs |= {norm(x) for x in re.findall(num["doc_pattern"], line)} - {norm(docno)}
    for tool, kws in qms["core_tools"].items():
        if any(k in text for k in kws):
            want = (qms.get("core_tool_docs") or {}).get(tool)
            if want and norm(want) not in link_refs:
                add("상호참조", f"{tool} 언급 - 연계 문서 {want} 참조 없음", f"{want} 참조 추가")
            elif not want and not link_refs:
                add("내용보완", f"{tool} 언급 - 연계 문서번호 미명시", f"연계 QP/WI/FM 번호 명시 {UNCONFIRMED}")

    # (11) 보존기간
    r = qms["retention"]
    spans = [text[m.end():m.end() + 25] for m in re.finditer("보존기간", text)]
    if typ in r.get("allow_blank_for", []):
        # 양식 단계: 보존기간 공란/미표기 허용. 허용값이 아닌 '구체적 값'(예: 7년)을 적었을 때만 오류.
        for sp in spans:
            val = re.match(r"\s*[:：은는을를]?\s*(\d+\s*년|영구)", sp)
            if val and not any(val.group(1).replace(" ", "").startswith(a) for a in r["allowed"]):
                add("내용보완", f"보존기간 '{val.group(1)}' 허용값 아님 {r['allowed']}", "허용값 중 선택")
    elif typ in r["required_for"]:
        if not spans:
            add("내용보완", "보존기간 미표기", f"보존기간 기재 (허용값 {r['allowed']})")
        elif not any(a in sp for sp in spans for a in r["allowed"]):
            add("내용보완", f"보존기간 값 미확정 (본문: '보존기간{spans[0].strip()[:20]}')", f"허용값 중 확정 {r['allowed']} {UNCONFIRMED}")

    # (12) 고객사 요구사항
    allowed = set(cust.get("customers") or [])
    for c in re.findall(cust["customer_marker"], text):
        if c not in allowed:
            add("내용보완", f"등록되지 않은 고객사 '{c}' (customer_rules.yaml)", "고객사 등록 여부 확인")
    if typ in qms["csr_required_for"] and not re.search(r"고객 특정 요구사항|CSR", text):
        add("내용보완", "IATF 고객 특정 요구사항(CSR) 언급 없음", f"{qms['main_customer']} CSR 반영")

    # 삭제 지시 문구 (FAIL)
    found = [ph for ph in qms.get("prohibited_phrases", []) if ph in text]
    if found:
        add("내용보완", "삭제 지시 문구 발견: " + " / ".join(found), "해당 문구 삭제 후 새 수정본 작성")
    # SH 접두어 미적용 참조 (HOLD)
    legacy = sorted({m.upper() for m in re.findall(r"(?<![A-Za-z0-9-])(?:QM|QP|WI|FM)-\d{3}\b", text, re.I)})
    legacy = [x for x in legacy if x != norm(docno or "")]
    if legacy:
        add("확인필요", f"SH 접두어 미적용 참조 확인: {', '.join(legacy[:20])}{' 외 %d건' % (len(legacy) - 20) if len(legacy) > 20 else ''}",
            "SH- 접두어 적용 여부 확인 " + UNCONFIRMED)

    # (13) LOT 추적성
    lt = qms["lot_traceability"]
    if lt["keyword"] in text:
        need = qms["lot_traceability_retention"], qms["lot_trace_target_time"]
        if not any(x in text for x in lt.get("retention_patterns", [need[0]])):
            add("내용보완", f"LOT 추적 기록 보존기간 {need[0]} 미명시", f"보존기간 {need[0]} 명시")
        if not any(x in text for x in lt.get("target_patterns", [need[1]])):
            add("내용보완", f"LOT 추적 목표시간 {need[1]} 미명시", f"목표시간 {need[1]} 명시")

    # (14) 페이지 번호와 목차
    page, toc = page_toc_flags(p, text)
    if typ in qms["page_number_required_for"] and not page:
        add("내용보완", "페이지 번호 없음", "머리글/바닥글에 Page X of Y 삽입")
    if typ in qms["toc_required_for"] and not toc:
        add("내용보완", "목차 없음", "목차 삽입")

    # (15) 중복 문서
    if docno and rev is not None and not unit:
        dup = duplicates(num["doc_pattern"], p, docno, rev)
        if dup:
            add("내용보완", f"동일 문서번호/Rev 중복 문서: {', '.join(dup)}", "중복 제거 또는 번호/Rev 정정 (자동 삭제하지 않음)")
    return docno, issues, approved


# ---------------- 라우팅 ----------------
def write_candidate(p: Path, docno, issues):
    """수정 필요사항 추출 → 03_EDIT/AUTO_DRAFT 에 (1) 수정필요사항 목록 (2) 편집용 초안 사본(_DRAFT)을 새 파일로 생성.
    원본은 건드리지 않으며, 확정되지 않은 값은 임의로 채우지 않는다(초안 사본은 원본과 동일, 사람이 수정)."""
    ts = dt.datetime.now().strftime("%Y%m%d%H%M%S")
    out = D["edit"] / "AUTO_DRAFT" / f"{p.stem}_수정필요사항_{ts}.md"
    safe_copy(p, D["edit"] / "AUTO_DRAFT", f"{p.stem}_DRAFT{p.suffix}")
    lines = [f"# 수정후보: {p.name}", f"- 생성: {now()}", f"- 원본: {p} (변경 없음)",
             f"- 자동 수정: 금지 (auto_edit_allowed=NO) — 사람이 `_DRAFT` 사본을 직접 수정",
             f"- 주의: '{UNCONFIRMED}' 표시는 담당자 확정 전에는 임의 값을 넣지 않음", "", "| # | 분류 | 문제 | 수정 제안 |", "|---|---|---|---|"]
    for i, (c, m, f) in enumerate(issues, 1):
        lines.append(f"| {i} | {c} | {m} | {f or '-'} |")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    rv = (re.search(cfg("document_number_rules.yaml")["revision_pattern"], p.name) or [None, ""])[1]
    log("revision_history.csv", [dt.date.today(), docno or p.stem, rv, "", f"AUTO_DRAFT 생성(수정 필요 {len(issues)}건, 미확정): {out.name}", "system", ""])
    return out

def doc_lines(p: Path):
    """DIFF 용 줄 단위 텍스트 (xlsx 는 시트별 구분)."""
    if p.suffix.lower() == ".xlsx":
        out = []
        for name, t in xlsx_sheets(p).items():
            out.append(f"[SHEET:{name}]")
            out += t.splitlines()
        return out
    return extract_text(p).splitlines()

def find_original(p: Path):
    """수정본 → 원본(01_ORIGINAL) 찾기: 접미어(_DRAFT/_수정본/_vN) 제거한 이름 일치 → 같은 문서번호."""
    base = re.sub(r"(_DRAFT|_수정본\d*|_v\d+)+$", "", p.stem)
    cands = [q for q in D["orig"].rglob("*") if q.is_file() and q.name != ".gitkeep" and q.suffix.lower() == p.suffix.lower()]
    for q in cands:
        if q.stem == base:
            return q
    num = cfg("document_number_rules.yaml")
    m = re.search(num["doc_pattern"], p.name)
    same = [q for q in cands if m and (re.search(num["doc_pattern"], q.name) or [None])[0] == m.group(0)]
    return sorted(same)[-1] if same else None

def make_diff(orig: Path, revised: Path):
    """원본 ↔ 수정본 DIFF → 03_EDIT/DIFF/*.md (unified diff). revision_history 에 기록."""
    import difflib
    a, b = doc_lines(orig), doc_lines(revised)
    ud = list(difflib.unified_diff(a, b, fromfile=f"원본 {orig.name}", tofile=f"수정본 {revised.name}", lineterm="", n=1))
    add = sum(1 for l in ud if l.startswith("+") and not l.startswith("+++"))
    dele = sum(1 for l in ud if l.startswith("-") and not l.startswith("---"))
    out = unique_path(D["edit"] / "DIFF" / f"{revised.stem}__vs__{orig.stem}.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(ud) if ud else "(텍스트 차이 없음)"
    out.write_text(f"# DIFF: 원본 ↔ 수정본\n- 원본: {orig.relative_to(ROOT)}\n- 수정본: {revised.name}\n- 생성: {now()}\n- 변경 줄: +{add} / -{dele}\n\n```diff\n{body}\n```\n", encoding="utf-8")
    num = cfg("document_number_rules.yaml")
    m = re.search(num["doc_pattern"], revised.name)
    log("revision_history.csv", [dt.date.today(), norm(m.group(0)) if m else revised.stem, (re.search(num["revision_pattern"], orig.name) or [None, ""])[1],
                                  (re.search(num["revision_pattern"], revised.name) or [None, ""])[1], f"원본↔수정본 DIFF 생성 +{add}/-{dele}: {out.name}", "system", ""])
    print(f"[DIFF   ] {orig.name} ↔ {revised.name}: +{add} / -{dele} → {out.relative_to(ROOT)}")
    return out

def diff_cmd(a, b=None):
    """diff <원본> <수정본>  (경로 또는 파일명).  수정본만 주면 원본을 자동으로 찾는다."""
    def find(x):
        pp = Path(x)
        if pp.exists():
            return pp
        hits = [q for q in ROOT.rglob(x) if q.is_file()]
        return hits[0] if hits else sys.exit(f"{x} 없음")
    if b is None:
        rv = find(a)
        og = find_original(rv)
        if not og:
            sys.exit("원본을 찾을 수 없음")
        return make_diff(og, rv)
    return make_diff(find(a), find(b))

# ---------------- 승인 패키지 ----------------
def build_package(p: Path, typ: str, folder="승인대기"):
    """Release Gate 결과 + 검토요약 + DIFF + 문서 사본 + 결재 체크리스트 → 04_APPROVAL/PACKAGES/<문서>/"""
    pk, n = D["appr"] / "PACKAGES" / p.stem, 2
    while pk.exists():
        pk = D["appr"] / "PACKAGES" / f"{p.stem}_v{n}"
        n += 1
    pk.mkdir(parents=True)
    shutil.copy2(p, pk / p.name)
    latest = {}   # 같은 요약의 여러 재실행본 중 최신본만 포함
    for f in (D["rev"] / "자동검토결과").glob(f"{p.stem}*_요약*.md"):
        key = re.sub(r"_v\d+(?=\.md$)", "", f.name)
        if key not in latest or f.stat().st_mtime >= latest[key].stat().st_mtime:
            latest[key] = f
    sd = pk / "검토요약"
    sd.mkdir()
    for key, f in sorted(latest.items()):
        shutil.copy2(f, sd / key)
    for f in sorted((D["edit"] / "DIFF").glob(f"{p.stem}__vs__*.md")):
        shutil.copy2(f, pk / f"DIFF_{f.name}")
    g = gate_check(p, folder)
    ok = all(x[1] != "FAIL" for x in g)
    lines = [f"# Release Gate: {p.name}", f"- 판정: {'PASS' if ok else 'FAIL/HOLD'} (G8 '사람 승인'은 승인 전에는 FAIL 이 정상)", "", "| Gate | 결과 | 비고 |", "|---|---|---|"]
    lines += [f"| {a} | {b} | {c} |" for a, b, c in g]
    (pk / "Release_Gate.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    q = cfg("qms_rules.yaml")
    (pk / "승인체크리스트.md").write_text("\n".join([
        f"# 승인 체크리스트: {p.name}", f"- 패키지 생성: {now()}", "",
        "## 확인 항목", "- [ ] Release Gate 의 FAIL/HOLD 항목을 확인했다", "- [ ] 원본 ↔ 수정본 DIFF 를 확인했다 (있는 경우)",
        "- [ ] 문서번호/Rev/문서명이 맞다", "- [ ] 문서관리대장·FM Master 등재가 맞다", "",
        "## 결재 (성명·서명·일자는 사람이 기재)",
        f"- 작성: [확인 필요]  서명: ________  일자: ________",
        f"- 검토(품질책임자): {q.get('quality_manager', UNCONFIRMED)}  서명: ________  일자: ________",
        f"- 승인: [확인 필요]  서명: ________  일자: ________",
        f"- 고객 승인 담당(필요 시): {q.get('customer_approver', UNCONFIRMED)}", ""]), encoding="utf-8")
    (pk / "STATUS.md").write_text(f"# 패키지 상태\n- {now()} 생성 ({folder})\n", encoding="utf-8")
    log("workflow_log.csv", [now(), p.stem, "", f"04_APPROVAL/{folder}", f"04_APPROVAL/PACKAGES/{pk.name}", "system", "승인 패키지 생성"])
    print(f"[PACKAGE] {p.name} → 04_APPROVAL/PACKAGES/{pk.name}  (Gate {'PASS' if ok else 'FAIL/HOLD'})")
    return pk

def package_cmd(name):
    for sub in ("승인대기", "검토완료", "승인완료"):
        f = D["appr"] / sub / name
        if f.exists():
            typ = cfg("qms_rules.yaml")["classify"].get(prefix_of(f.name), "")
            return build_package(f, typ, sub)
    sys.exit(f"{name} 이(가) 04_APPROVAL 에 없음")

def approval_state(text: str) -> str:
    """승인상태 자동판정: ACTIVE / APPROVED / DRAFT(승인 전) / UNKNOWN."""
    qms = cfg("qms_rules.yaml")
    st = re.search(rf"{qms['document_status']['field']}\s*[:：]\s*(\S+)", text)
    if st:
        v = st.group(1)
        return "APPROVED" if v in ("승인완료", "APPROVED") else ("ACTIVE" if v == "ACTIVE" else f"DRAFT({v})")
    mk = re.search(qms["document_status"]["header_marker"], text[:600])
    if mk:
        return "ACTIVE" if mk.group(0) == "ACTIVE" else "APPROVED"
    if re.search(r"사용승인 전|승인 전|작성중|DRAFT", text[:1500]):
        return "DRAFT(승인 전)"
    return "UNKNOWN"

def check(p: Path, typ: str, final_stage=False):
    """워크북이면 양식(시트)별로 쪼개 검토. 반환 (docno, issues, approved, units)
    units = [(unit_docno, unit_issues, unit_approved, unit_text)] (분할 검토가 아니면 빈 리스트)."""
    units = split_units(p)
    if not units:
        d, i, a = validate(p, typ, final_stage)
        return d, i, a, []
    results, issues = [], []
    want = {norm(x) for x in expected_range(p.name)}
    have = {norm(n) for n, _ in units}
    for miss in sorted(want - have):
        issues.append(("문서번호", f"파일명 범위의 {miss} 양식 시트가 없음", "시트 추가 또는 파일명 범위 정정 " + UNCONFIRMED))
    for extra in sorted(have - want) if want else []:
        issues.append(("문서번호", f"파일명 범위에 없는 양식 시트 {extra}", "파일명 범위 정정 " + UNCONFIRMED))
    unit_names = {n for n, _ in units}
    ctx = "\n".join(t for n, t in xlsx_sheets(p).items() if n.strip() not in unit_names)
    for name, text in units:
        d, i, a = validate(p, typ, final_stage, unit=(name, text, ctx))
        results.append((name, i, a, text))
        issues += [(c, f"[{name}] {m}", f) for c, m, f in i]
    return p.stem, issues, all(a for _, _, a, _ in results), results

def summary_table(p: Path, docno, issues, approved, stage="검토", text=None, label=None, quiet=False):
    """검사 | 결과 | 조치 요약표 (markdown). 문서별로 02_REVIEW/자동검토결과 에 저장."""
    num, qms = cfg("document_number_rules.yaml"), cfg("qms_rules.yaml")
    text = text if text is not None else extract_text(p)
    def hit(cat=None, kw=None):
        return [m for c, m, _ in issues if (cat is None or c == cat) and (kw is None or any(k in m for k in kw))]
    rows = []
    def row(name, bad, ok_note="-", bad_note=""):
        rows.append((name, "FAIL" if bad else "PASS", bad_note if bad else ok_note))
    row("문서번호", hit("문서번호"), bad_note="; ".join(hit("문서번호"))[:80])
    row("Rev", hit("개정번호"), bad_note="; ".join(hit("개정번호"))[:80])
    row("회사명", hit(kw=["회사명"]), bad_note="회사명 표기")
    row("고객사", hit(kw=["고객사", "CSR"]), bad_note="; ".join(hit(kw=["고객사", "CSR"]))[:80])
    refs = sorted({norm(x) for m in hit("상호참조") for x in re.findall(num["doc_pattern"], m)})
    row("QP-WI-FM 연계", hit("상호참조"), bad_note=(", ".join(refs) + " 참조 확인") if refs else "연계 확인")
    ret = re.search(r"보존기간\s*[:：]?\s*(\S+)", text)
    allowed_ret = qms["retention"]["allowed"]
    has_val = any(a in text[m.end():m.end() + 25] for m in re.finditer("보존기간", text) for a in allowed_ret)
    ok_ret = (ret.group(1) if has_val and ret else "공란 (양식 단계 허용)") if "보존기간" in text or not has_val else "해당 없음"
    row("보존기간", hit(kw=["보존기간"]) and not hit(kw=["LOT"]), ok_note=ok_ret, bad_note="; ".join(hit(kw=["보존기간"]))[:80])
    lot = qms["lot_traceability"]["keyword"] in text
    if lot:
        row("LOT 추적 목표", hit(kw=["LOT 추적"]), ok_note=qms["lot_trace_target_time"], bad_note="; ".join(hit(kw=["LOT 추적"]))[:80])
    else:
        rows.append(("LOT 추적 목표", "N/A", "LOT 추적 언급 없음"))
    st = re.search(rf"{qms['document_status']['field']}\s*[:：]\s*(\S+)", text)
    rows.append(("승인상태", "PASS" if approved else "HOLD", approval_state(text) if approved else f"승인 전 ({approval_state(text)})"))
    ph = hit(kw=["삭제 지시"])
    hold_msgs = hit("확인필요")
    row("삭제 지시 문구", ph, bad_note="; ".join(ph)[:80])
    if hold_msgs:
        rows.append(("확인 필요 항목", "HOLD", "; ".join(hold_msgs)[:80]))
    others = [m for c, m, _ in issues if m not in sum([hit("문서번호"), hit("개정번호"), hit("상호참조"), ph, hold_msgs, hit(kw=["회사명", "고객사", "CSR", "보존기간", "LOT 추적"])], [])]
    if others:
        rows.append(("기타 검사", "FAIL", f"{len(others)}건 (상세: 자동검토결과 JSON)"))
    fails = [r for r in rows if r[1] == "FAIL"]
    verdict = "FAIL" if fails else ("PASS" if approved and not hold_msgs else "HOLD")
    rows.append(("종합 판정", verdict, {"FAIL": "수정 필요", "HOLD": "확인 또는 승인 필요", "PASS": "승인 및 배포 가능"}[verdict]))
    if fails:
        mv = ("불가", "검사 FAIL 해결 후 재검증")
    elif hold_msgs or not approved:
        mv = ("불가", "확인 필요 항목 해소 및 승인 완료 후 이동" if hold_msgs else "승인 완료 후 이동")
    else:
        mv = ("가능", "04_APPROVAL/승인완료 → finalize")
    rows.append(("FINAL 이동", mv[0], mv[1]))
    md = f"### {label or p.name} ({docno or '문서번호 미확인'}) — {stage}\n\n| 검사 | 결과 | 조치 |\n|---|---|---|\n" + "\n".join(f"| {a} | {b} | {c} |" for a, b, c in rows) + "\n"
    rep = D["rev"] / "자동검토결과"; rep.mkdir(exist_ok=True)
    out = unique_path(rep / (f"{p.stem}__{docno}_요약.md" if label else f"{p.stem}_요약.md"))
    out.write_text(md, encoding="utf-8")
    if quiet:
        print(f"  ▸ {docno}: {verdict}" + (f" ({len(issues)}건)" if issues else "") + f"  FINAL {mv[0]}")
    else:
        print(md)

def route(p: Path, typ: str):
    """검토 후 02_REVIEW 또는 04_APPROVAL/승인대기 로 '복사'. 반환: 통과 여부"""
    docno, issues, approved, units = check(p, typ)
    name = docno or p.stem
    if units:
        print(f"[WORKBOOK] {p.name}: 양식 시트 {len(units)}개를 양식별로 검토")
        for ud, ui, ua, ut in units:
            summary_table(p, ud, ui, ua, text=ut, label=f"{p.name} ▸ {ud}", quiet=True)
    else:
        summary_table(p, docno, issues, approved)
    if issues:
        cats = {c for c, _, _ in issues}
        folder = next((ERR_DIR[c] for c in ERR_DIR if c in cats), DEFAULT_ERR_DIR)
        rep = D["rev"] / "자동검토결과"; rep.mkdir(exist_ok=True)
        unique_path(rep / f"{p.stem}_검토결과.json").write_text(json.dumps({
            "file": p.name, "checked": now(), "sha256": sha(p),
            "units": [u[0] for u in units],
            "issues": [{"category": c, "message": m, "suggestion": f} for c, m, f in issues]},
            ensure_ascii=False, indent=2), encoding="utf-8")
        safe_copy(p, D["rev"] / folder)
        cand = write_candidate(p, docno, issues)
        for c, m, _ in issues:
            log("error_log.csv", [now(), name, c, m, "OPEN"])
        log("workflow_log.csv", [now(), name, "", p.parent.name, f"02_REVIEW/{folder}", "system", f"{len(issues)}건 문제, 수정후보 {cand.name}"])
        print(f"[REVIEW ] {p.name}: {len(issues)}건 → 02_REVIEW/{folder} (AUTO_DRAFT: 03_EDIT/AUTO_DRAFT/{cand.name})")
    else:
        base = re.sub(r"(_DRAFT|_수정본\d*|_v\d+)+$", "", p.stem)
        for old in (D["appr"] / "승인대기").glob(f"{base}*{p.suffix}"):   # 같은 문서의 이전 승인대기본은 삭제하지 않고 이력으로 이동
            if old.name != p.name and re.sub(r"(_DRAFT|_수정본\d*|_v\d+)+$", "", old.stem) == base:
                dst = unique_path(D["hist"] / "이전버전" / base / f"{old.stem}__superseded{old.suffix}")
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(old), dst)
                log("workflow_log.csv", [now(), base, "", "04_APPROVAL/승인대기", f"06_HISTORY/이전버전/{base}", "system", f"수정본 {p.name} 로 대체된 이전 승인대기본 이동"])
        ap = safe_copy(p, D["appr"] / "승인대기")
        log("workflow_log.csv", [now(), name, "", p.parent.name, "04_APPROVAL/승인대기", "system",
                                 "검사통과 (문서상태 승인완료 표기됨)" if approved else "검사통과 (승인 전: 배포 불가)"])
        print(f"[PASS   ] {p.name} → 04_APPROVAL/승인대기")
        build_package(ap, typ, "승인대기")
    mark_processed(sha(p))
    return not issues

def classify():
    rules, done = cfg("qms_rules.yaml")["classify"], processed()
    for p in sorted(D["orig"].iterdir()):
        if not p.is_file() or p.name == ".gitkeep":
            continue
        typ = rules.get(prefix_of(p.name))
        if typ == MASTER:   # 관리자료(대장/마스터/계획): 승인 흐름 없이 등록만
            dest = D["orig"] / typ
            dest.mkdir(exist_ok=True)
            if (dest / p.name).exists():
                print(f"[SKIP   ] {p.name}: 01_ORIGINAL/{typ} 에 같은 이름 존재 → 덮어쓰지 않음")
                continue
            h = sha(p)
            shutil.move(str(p), dest / p.name)
            log("workflow_log.csv", [now(), p.name, "", "투입", f"01_ORIGINAL/{typ}", "system", "관리자료 등록(승인 흐름 없음, 상호참조 기준으로 사용)"])
            if h in done:   # 이전에 '분류불가'로 기록된 건 종결 처리
                log("error_log.csv", [now(), p.name, "분류불가", "관리자료로 재분류", "CLOSED"])
            else:
                mark_processed(h)
            print(f"[MASTER ] {p.name} → 01_ORIGINAL/{typ} (관리자료)")
            continue
        if not typ:
            if sha(p) not in done:
                log("error_log.csv", [now(), p.name, "분류불가", "파일명 접두어 미등록", "OPEN"])
                safe_copy(p, D["rev"] / DEFAULT_ERR_DIR)
                mark_processed(sha(p))
                print(f"[REVIEW ] {p.name}: 분류 불가 → 02_REVIEW/{DEFAULT_ERR_DIR} (원본은 01_ORIGINAL 에 유지)")
            continue
        dest = D["orig"] / typ
        dest.mkdir(exist_ok=True)
        if (dest / p.name).exists():   # 덮어쓰기 금지
            print(f"[SKIP   ] {p.name}: 01_ORIGINAL/{typ} 에 같은 이름 존재 → 덮어쓰지 않음")
            continue
        shutil.move(str(p), dest / p.name)   # 같은 01_ORIGINAL 내 정리 이동
        log("workflow_log.csv", [now(), p.name, "", "투입", f"01_ORIGINAL/{typ}", "system", "자동분류"])

def run(rereview=False):
    classify()
    done = set() if rereview else processed()
    for typ_dir in sorted(d for d in D["orig"].iterdir() if d.is_dir() and d.name != MASTER):
        for p in sorted(typ_dir.iterdir()):
            if p.is_file() and p.name != ".gitkeep" and p.suffix.lower() in (TEXT_EXT | {".pdf"}) and sha(p) not in done:
                route(p, typ_dir.name)

def recheck():
    """03_EDIT/수정완료 재검증 (파일은 지우지 않고 복사)."""
    done = processed()
    for p in sorted((D["edit"] / "수정완료").iterdir()):
        if not p.is_file() or p.name == ".gitkeep" or sha(p) in done:
            continue
        typ = cfg("qms_rules.yaml")["classify"].get(prefix_of(p.name), "")
        og = find_original(p)
        if og and og.resolve() != p.resolve():
            make_diff(og, p)   # 원본 ↔ 수정본 DIFF (재점검 전)
        else:
            print(f"[DIFF   ] {p.name}: 대응하는 원본을 찾지 못해 DIFF 생략")
        route(p, typ)

def crosscheck():
    """QM/QP/WI/FM 상호참조 종합 점검 → 02_REVIEW/qms_crosscheck_summary.md
    존재하지 않는 참조 FAIL / SH 접두어 없는 참조 HOLD / 동일 문서번호 복수 Rev 표시."""
    num = cfg("document_number_rules.yaml")
    reg, obs = registry(num["doc_pattern"]), obsolete_set(num["doc_pattern"])
    revs, lines = {}, []
    for q in sorted(stage_files(("orig", "edit", "appr", "final"))):
        m = re.search(num["doc_pattern"], q.name)
        r = re.search(num["revision_pattern"], q.name)
        if m and r:
            revs.setdefault(norm(m.group(0)), set()).add(r.group(1))
    rows = []
    for p in sorted(D["orig"].rglob("*")):
        if not p.is_file() or p.name == ".gitkeep" or MASTER in p.parts or p.suffix.lower() not in TEXT_EXT:
            continue
        units = split_units(p)
        for name, text in (units or [(p.name, extract_text(p))]):
            own = norm((re.search(num["doc_pattern"], name) or [""])[0])
            refs = {norm(x) for x in re.findall(num["doc_pattern"], text)} - {own}
            legacy = {m.upper() for m in re.findall(r"(?<![A-Za-z0-9-])(?:QM|QP|WI|FM)-\d{3}\b", text, re.I)} - {own}
            exc = own in {norm(x) for x in cfg("qms_rules.yaml").get("prohibited_reference_exceptions", [])}
            fail = sorted(r for r in refs if (r not in obs or not exc) and (r not in reg or r in obs))
            rows.append((p.name, name if units else "", "FAIL" if fail else ("HOLD" if legacy else "PASS"),
                         fail, sorted(legacy)))
    lines = ["# QMS 상호참조 점검 요약", f"- 생성: {now()}", "",
             "| 문서 | 시트(양식) | 판정 | 존재/폐기 오류 참조 | SH 접두어 미적용 참조 |", "|---|---|---|---|---|"]
    for f, u, v, fl, lg in rows:
        lines.append(f"| {f} | {u or '-'} | {v} | {', '.join(fl)[:150] or '-'} | {', '.join(lg)[:150] or '-'} |")
    # 문서번호별 최신 Rev / 중복 Rev / Rev 누락
    latest_rows = []
    for q in sorted(stage_files(("orig", "edit", "appr", "final"))):
        if MASTER in q.parts or q.suffix.lower() not in (TEXT_EXT | {".pdf"}) or D["rev"] in q.parents or D["edit"] / "수정중" in q.parents:
            continue
        m = re.search(num["doc_pattern"], q.name)
        r = re.search(num["revision_pattern"], q.name)
        if m and not re.search(r"-\d{2,3}-\d{2,3}$", m.group(0)):
            latest_rows.append((norm(m.group(0)), int(r.group(1)) if r else -1, q.name, q.parent.name))
    by = {}
    for no, rv, nm, st in latest_rows:
        by.setdefault(no, []).append((rv, nm, st))
    lines += ["", "## 문서번호별 최신 Rev 후보 / 중복 Rev / Rev 누락", "", "| 문서번호 | 최신 Rev | 파일 수 | 판정 | 비고 |", "|---|---|---|---|---|"]
    rev_rows = []
    for no, v in sorted(by.items()):
        revs_ = [x[0] for x in v]
        dupr = sorted({r for r in revs_ if r >= 0 and revs_.count(r) > 1 and len({re.sub(r"(_DRAFT|_수정본\d*|_v\d+)+$", "", Path(x[1]).stem) for x in v if x[0] == r}) > 1})
        note = ([f"동일 Rev 중복 파일: Rev.{', Rev.'.join(f'{d:02d}' for d in dupr)}"] if dupr else []) + (["Rev 누락 파일 존재"] if -1 in revs_ else [])
        stt = "HOLD" if note else "PASS"
        rev_rows.append((no, stt))
        lines.append(f"| {no} | {'Rev.%02d' % max(revs_) if max(revs_) >= 0 else '-'} | {len(v)} | {stt} | {' / '.join(note) or '-'} |")
    if not by:
        lines.append("| (개별 문서 파일 없음) | | | | |")
    rows += [(no, "", st_, [], []) for no, st_ in rev_rows if st_ == "HOLD"]
    multi = {k: sorted(v) for k, v in revs.items() if len(v) > 1}
    lines += ["", "## 동일 문서번호의 복수 Rev (최신 Rev 후보)"]
    lines += [f"- {k}: Rev.{', Rev.'.join(v)} → 최신 후보 Rev.{v[-1]}" for k, v in sorted(multi.items())] or ["- 없음"]
    out = unique_path(D["rev"] / "qms_crosscheck_summary.md")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    cnt = {k: sum(r[2] == k for r in rows) for k in ("PASS", "HOLD", "FAIL")}
    print(f"[CROSSCHECK] PASS {cnt['PASS']} / HOLD {cnt['HOLD']} / FAIL {cnt['FAIL']} → {out.relative_to(ROOT)}")
    return rows

LEDGER_RX2 = re.compile(r"^(SH-(QM|QP|WI|FM)-\d{3})\s+(.+?)\s+(Rev\.\d{2})\b")   # 간이 대장 형식: 문서번호 문서명 Rev ...
LEDGER_RX = re.compile(r"^(\d+)\s+(QM|QP|WI|FM)\s+(SH-(?:QM|QP|WI|FM)-\d{3})\s+(.+?)\s+(Rev\.\d{2})\s+(\d{5})\s+(\d{5})")

def master_files(keyword):
    """관리자료 폴더(01_ORIGINAL/MASTER_REF)와 00_CONFIG 에서 검색 ('샘플' 파일은 제외)."""
    return [q for d in (D["orig"] / MASTER, D["cfg"]) for q in sorted(d.glob("*"))
            if q.is_file() and keyword in q.name and "샘플" not in q.name and q.suffix.lower() in (".xlsx", ".xlsm", ".docx")]

def latest_master(keyword):
    """같은 종류 관리자료가 원본/수정본으로 여러 개면 가장 최근 파일만 사용(중복 등재 방지)."""
    fs = master_files(keyword)
    return [max(fs, key=lambda f: f.stat().st_mtime)] if fs else []

def ledger_entries():
    """문서관리대장(01_문서관리대장 시트) → [(번호, 구분, 문서번호, 문서명, Rev)]. 대장이 없으면 빈 리스트."""
    out = []
    for f in latest_master("문서관리대장"):
        sheets = xlsx_sheets(f)
        sheet = next((t for n, t in sheets.items() if n.startswith("01_")), None)
        for line in (sheet if sheet is not None else "\n".join(sheets.values())).splitlines():
            m = LEDGER_RX.match(line.strip())
            if m:
                out.append((m[1], m[2], m[3], m[4].strip(), m[5]))
                continue
            m = LEDGER_RX2.match(line.strip())
            if m:
                out.append(("", m[2], m[1], m[3].strip(), m[4]))
    return out

def controlled_ids():
    """대장 등재 번호 + FM Master 등재 번호 (정식 관리 대상)."""
    ids = {norm(e[2]) for e in ledger_entries()}
    for f in master_files("FM_Master"):
        ids |= {norm(x) for x in re.findall(cfg("document_number_rules.yaml")["doc_pattern"], extract_text(f))}
    return ids

def fm_master_ids():
    ids = set()
    for f in master_files("FM_Master"):
        ids |= set(re.findall(r"SH-FM-\d{3}", extract_text(f)))
    return ids

def ledger_check():
    """문서관리대장 ↔ 실제 파일/통합문서 대조 → 02_REVIEW/qms_ledger_check.md"""
    num = cfg("document_number_rules.yaml")
    ents = ledger_entries()
    if not ents:
        print("[LEDGER] 문서관리대장을 찾지 못함 (01_ORIGINAL/MASTER_REF 또는 00_CONFIG, 파일명에 '문서관리대장' 포함)"); return [], []
    lines = ["# 문서관리대장 ↔ 실제 파일 대조", f"- 생성: {now()}", f"- 대장 등재 {len(ents)}건", ""]
    # 실제 문서 원천: 개별 파일(파일명 번호) + 통합문서 본문
    src_text, src_rev = {}, {}
    for f in latest_master("통합문서"):
        src_text[f.name] = extract_text(f)
        r = re.search(num["revision_pattern"], f.name)
        src_rev[f.name] = f"Rev.{r.group(1)}" if r else None
    indiv = {}
    for q in stage_files(("orig", "edit", "appr", "final")):
        if MASTER in q.parts or q.suffix.lower() not in (TEXT_EXT | {".pdf"}):
            continue
        m = re.search(num["doc_pattern"], q.name)
        r = re.search(num["revision_pattern"], q.name)
        if m:
            indiv.setdefault(norm(m.group(0)), set()).add(f"Rev.{r.group(1)}" if r else None)
    rows, dup = [], [k for k, v in collections.Counter(e[2] for e in ents).items() if v > 1]
    for no, kind, doc, name, rev in ents:
        found = [f for f, t in src_text.items() if doc in t]
        status, note = "PASS", ""
        if norm(doc) in indiv:
            revs = indiv[norm(doc)]
            status, note = ("PASS", "개별 파일") if rev in revs else ("FAIL", f"Rev 불일치: 대장 {rev} / 파일 {sorted(str(x) for x in revs)}")
        elif found:
            f = found[0]
            if name not in src_text[f]:
                status, note = "HOLD", f"문서명 불일치: 대장 '{name}' 가 {f} 에서 확인되지 않음"
            elif src_rev[f] and src_rev[f] != rev:
                status, note = "FAIL", f"Rev 불일치: 대장 {rev} / {f} {src_rev[f]}"
            else:
                note = f"{f} 에서 확인"
        else:
            status, note = "FAIL", "실제 파일/통합문서에서 찾을 수 없음"
        if doc in dup:
            status, note = "FAIL", note + " / 대장 중복 등재"
        rows.append((doc, kind, name, rev, status, note))
    cnt = collections.Counter(r[4] for r in rows)
    lines += [f"## 결과: PASS {cnt['PASS']} / HOLD {cnt['HOLD']} / FAIL {cnt['FAIL']}", "",
              "| 문서번호 | 구분 | 문서명 | Rev | 판정 | 비고 |", "|---|---|---|---|---|---|"]
    lines += [f"| {d} | {k} | {n} | {r} | {s_} | {nt or '-'} |" for d, k, n, r, s_, nt in rows if s_ != "PASS"] or ["| (이상 없음) | | | | | |"]
    ledger_ids = {e[2] for e in ents}
    extra_doc = sorted(({x for t in src_text.values() for x in re.findall(r"SH-(?:QM|QP|WI)-\d{3}", t)}) - ledger_ids)
    fm_master = set()
    for f in master_files("FM_Master"):
        fm_master |= set(re.findall(r"SH-FM-\d{3}", extract_text(f)))
    fm_used = {x for t in src_text.values() for x in re.findall(r"SH-FM-\d{3}", t)}
    fm_used |= {f"SH-{x}" for x in indiv if re.fullmatch(r"FM-\d{3}", x)}
    for q in stage_files(("orig", "edit", "appr", "final")):
        if MASTER not in q.parts:
            fm_used |= {f"SH-{norm(n)}" for n, _ in split_units(q)}
    # 실제 개별 파일은 있는데 대장/FM Master 에 없는 번호
    unreg = sorted(k for k in indiv if re.fullmatch(r"(QM|QP|WI|FM)-\d{3}", k) and f"SH-{k}" not in ledger_ids and f"SH-{k}" not in fm_master_ids())
    for u in unreg:
        rows.append((f"SH-{u}", "", "(개별 파일)", "", "FAIL", "실제 파일 존재 / 대장·FM Master 미등록"))
    lines += ["", "## 실제 파일 존재 / 대장·FM Master 미등록", ", ".join(f"SH-{u}" for u in unreg) or "- 없음"]
    lines += ["", "## 대장에 없는 QM/QP/WI 번호 (통합문서에서 발견)", ", ".join(extra_doc) or "- 없음",
              "", "## FM Master 에 없는 FM 번호 (통합문서/양식 파일에서 발견)",
              ", ".join(sorted(fm_used - fm_master)) or "- 없음"]
    out = unique_path(D["rev"] / "qms_ledger_check.md")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[LEDGER] PASS {cnt['PASS']} / HOLD {cnt['HOLD']} / FAIL {cnt['FAIL']}  | 대장 외 QM/QP/WI {len(extra_doc)}건 | FM Master 외 FM {len(fm_used - fm_master)}건 → {out.relative_to(ROOT)}")
    return rows, sorted(fm_used - fm_master)

def gate_check(p: Path, folder=""):
    """FINAL 자동 배포 전 Gate. 반환 [(게이트, PASS/FAIL/N/A, 비고)]"""
    typ = cfg("qms_rules.yaml")["classify"].get(prefix_of(p.name), "")
    num = cfg("document_number_rules.yaml")
    docno, issues, approved, units = check(p, typ, final_stage=True)
    msgs = lambda *kw: [m for _, m, _ in issues if any(k in m for k in kw)]
    ids = [norm(u[0]) for u in units] or [norm(docno)]
    g = []
    d = [m for c, m, _ in issues if c == "문서번호"]
    g.append(("G1 문서번호 일치", "FAIL" if d else "PASS", "; ".join(d)[:90] or "-"))
    g.append(("G2 승인상태 자동판정", "PASS" if approved else "FAIL", approval_state(extract_text(p)) if not units else ("전 양식 승인 표기" if approved else "승인 표기 없는 양식 있음")))
    other = [m for c, m, _ in issues if c != "문서번호" and "문서상태가 승인완료가 아님" not in m]
    g.append(("G3 검토 이슈 없음", "FAIL" if other else "PASS", f"{len(other)}건" if other else "-"))
    ctl = controlled_ids()
    if ctl:
        miss = [i for i in ids if i not in ctl]
        g.append(("G4 문서관리대장/FM Master 등재", "FAIL" if miss else "PASS", ", ".join(miss)[:90] or "-"))
    else:
        g.append(("G4 문서관리대장/FM Master 등재", "N/A", "대장 없음"))
    ledger_dup = [k for k, v in collections.Counter(norm(e[2]) for e in ledger_entries()).items() if v > 1 and k in ids]
    dups = duplicates(num["doc_pattern"], p, docno, (re.search(num["revision_pattern"], p.name) or [None, None])[1]) if docno and not units else []
    g.append(("G5 중복 Rev/문서 없음", "FAIL" if dups or ledger_dup else "PASS", ", ".join(dups + ledger_dup)[:90] or "-"))
    ph = msgs("폐기/참조금지", "삭제 지시")
    g.append(("G6 폐기·참조금지·삭제지시 없음", "FAIL" if ph else "PASS", "; ".join(ph)[:90] or "-"))
    hits = [ap for ap, gt in cfg("gate_rules.yaml")["gate"].items() if {norm(f) for f in (gt.get("forms") or [gt.get("form")])} & set(ids)]
    bad = [ap for ap in hits if cfg("gate_rules.yaml")["gate"][ap]["status"] != "APPROVED"]
    g.append(("G7 AP 게이트(AP-01~04)", "N/A" if not hits else ("FAIL" if bad else "PASS"), ", ".join(hits) + (" 미승인: " + ", ".join(bad) if bad else "") if hits else "해당 없음"))
    mk = approval_marker()
    pks = package_dirs(p.stem)
    if folder != "승인완료":
        g8 = ("FAIL", f"현재 {folder or '?'}")
    elif not pks:
        g8 = ("FAIL", "승인 패키지 없음")
    elif not any((d / mk).exists() for d in pks):
        g8 = ("FAIL", f"{mk} 없음 (실제 승인 후 sign 으로 생성)")
    else:
        g8 = ("PASS", f"승인완료 + {mk}")
    g.append(("G8 사람 승인 단계 완료", g8[0], g8[1]))
    return g

def print_gate(p: Path, folder):
    g = gate_check(p, folder)
    ok = all(x[1] != "FAIL" for x in g)
    print(f"### {p.name} — FINAL Gate: {'PASS (배포 가능)' if ok else 'FAIL (배포 불가)'}\n\n| Gate | 결과 | 비고 |\n|---|---|---|")
    for a, b, c in g:
        print(f"| {a} | {b} | {c} |")
    print()
    return ok

def gatecheck():
    """04_APPROVAL 의 문서에 대해 FINAL 배포 전 Gate 표 출력."""
    for sub in ("승인대기", "검토완료", "승인완료"):
        for p in sorted((D["appr"] / sub).iterdir()):
            if p.is_file() and p.name != ".gitkeep":
                print_gate(p, sub)

def is_finalized(p: Path):
    f = D["log"] / "finalized_hashes.txt"
    return f.exists() and sha(p) in f.read_text().split()

def release_gate():
    """FINAL 배포 전 종합 Release Gate: 상호참조·대장 대조·문서별 Gate(G1~G8)를 모아 PASS/HOLD/FAIL 판정.
    FAIL 이 하나라도 있으면 배포 금지 / FAIL 없고 HOLD 만 있으면 승인·확인 후 재검사 / 모두 PASS 일 때만 배포 후보."""
    blockers, holds = [], []
    for f, u, v, fl, lg in crosscheck():
        (blockers if v == "FAIL" else holds if v == "HOLD" else []).append(f"상호참조: {f}{' ▸ ' + u if u else ''} :: {', '.join(fl or lg)[:100] or '확인 필요'}")
    lrows, fm_missing = ledger_check()
    for d, k, n, r, st, note in lrows:
        (blockers if st == "FAIL" else holds if st == "HOLD" else []).append(f"대장대조: {d} :: {note}")
    if fm_missing:
        holds.append(f"대장대조: FM Master 미등록 FM {len(fm_missing)}건 ({', '.join(fm_missing[:4])}…)")
    gate_fail_blocking = ("G1", "G4", "G5", "G6", "G7")      # 배포 금지(FAIL)
    gate_hold = ("G2", "G3", "G8")                            # 승인/확인 후 재검사(HOLD)
    for sub in ("승인대기", "검토완료", "승인완료"):
        for p in sorted((D["appr"] / sub).iterdir()):
            if p.is_file() and p.name != ".gitkeep" and not is_finalized(p):   # 이미 릴리스된 문서는 제외
                for g, st, note in gate_check(p, sub):
                    if st == "FAIL":
                        (blockers if g[:2] in gate_fail_blocking else holds).append(f"Gate[{sub}]: {p.name} :: {g} {note}")
    status = "FAIL" if blockers else ("HOLD" if holds else "PASS")
    lines = ["# QMS FINAL Release Gate", f"- 생성: {now()}", "", f"## 결과: {status}", "",
             f"- FAIL 항목: {len(blockers)}", f"- HOLD 항목: {len(holds)}", "", "## FAIL"]
    lines += [f"- {x}" for x in blockers] or ["- 없음"]
    lines += ["", "## HOLD"] + ([f"- {x}" for x in holds] or ["- 없음"])
    lines += ["", "## 판정 기준", "- FAIL이 하나라도 있으면 FINAL 배포 금지", "- FAIL은 없고 HOLD가 있으면 승인/확인 후 재검사", "- 모두 PASS일 때만 FINAL 배포 후보"]
    out = unique_path(D["rev"] / "qms_release_gate.md")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[RELEASE GATE] {status} (FAIL {len(blockers)} / HOLD {len(holds)}) → {out.relative_to(ROOT)}")
    return status

def fullaudit():
    """전체 자동감사: 신규 문서 검색 → 점검 → 상호참조 → 대장 대조 → Release Gate."""
    scan()
    run()
    release_gate()

def fm_master_register():
    """양식 워크북(SH-FM-1xx 시트)의 번호 중 FM Master 에 없는 것을 FM Master 의 '새 파일'에 등록한다.
    원본 Master 는 수정/덮어쓰지 않는다. 값은 FM-122(현장양식목록·작성계획·번호배정대조표)에 있는 것만 옮기고,
    없는 값(보존기간·최종개정일·승인자 등)은 비워 둔다. 등록은 '승인'이 아니므로 승인상태는 '승인 전'으로 둔다."""
    try:
        from openpyxl import load_workbook
        from copy import copy
    except ImportError:
        sys.exit("openpyxl 이 필요합니다: pip install openpyxl")
    masters = [f for f in master_files("FM_Master") if "수정본" not in f.name]
    plans = [q for q in D["orig"].rglob("SH-FM-122*.xlsx")]
    forms = [q for q in D["orig"].rglob("*.xlsx") if MASTER not in q.parts and split_units(q) and "SH-FM-122" not in q.name]
    if not masters or not plans:
        sys.exit("FM Master 또는 SH-FM-122 계획 파일을 찾지 못함")
    master, plan = sorted(masters)[0], plans[0]
    have = fm_master_ids()
    targets = sorted({norm(n) for f in forms for n, _ in split_units(f)} - {norm(x) for x in have})
    targets = [f"SH-{t}" for t in targets]
    if not targets:
        print("[FM MASTER] 등록할 신규 번호가 없습니다 (이미 모두 등록됨)")
        return
    pw = load_workbook(plan, data_only=True)
    info = {}
    for r in pw["01_현장양식목록"].iter_rows(values_only=True):
        if r and isinstance(r[1], str) and r[1] in targets:
            info[r[1]] = {"name": r[2], "qp": r[3], "wi": r[4], "use": r[7], "src": r[8]}
    for r in pw["02_작성계획"].iter_rows(values_only=True):
        if r and isinstance(r[1], str) and r[1] in info:
            info[r[1]].update({"dept": r[3], "keep": r[6], "sign": r[10]})
    for r in pw["03_번호배정대조표"].iter_rows(values_only=True):
        if r and isinstance(r[1], str) and r[1] in info:
            info[r[1]].update({"assign": r[4], "rev": r[5], "state": r[6], "basis": r[7]})
    missing = [t for t in targets if t not in info]
    if missing:
        print(f"[FM MASTER] 계획 파일(FM-122)에 정보가 없어 등록하지 않는 번호: {', '.join(missing)}")
    wb = load_workbook(master)
    ws = wb["01_FM_Master"]
    row = 2
    while ws.cell(row, 1).value:
        row += 1
    tmpl = row - 1
    added = []
    for t in targets:
        if t not in info:
            continue
        i = info[t]
        vals = [t, i["name"], i.get("use"), i.get("qp"), i.get("rev") or "Rev.00", "신규 배정", f"승인 전 ({i.get('state') or '양식 등록·승인 필요'})",
                f"{i.get('assign') or '신규 번호 배정'} — {plan.name} 03_번호배정대조표", f"{plan.name} / {forms[0].name}",
                (f"{i['dept']}(안)" if i.get("dept") else None), None, None, None,
                f"신규 번호. 연계 WI: {i.get('wi') or '-'} / 결재 방식(안): {i.get('sign') or '-'}",
                "양식 사용승인 후 문서상태·승인자 갱신, 기록별 보존기간 확정"]
        for c, v in enumerate(vals, 1):
            cell = ws.cell(row, c, v)
            cell._style = copy(ws.cell(tmpl, c)._style)
        added.append(t)
        row += 1
    out_name = f"{master.stem}_수정본_FM{added[0][-3:]}-{added[-1][-3:]}등록.xlsx"
    out = unique_path(master.parent / out_name)
    wb.save(out)
    mfn = lambda f: f"{f.stem}"
    log("revision_history.csv", [dt.date.today(), "SH_FM_Master", "00", "00", f"FM Master 신규 번호 {len(added)}건 등록({added[0]}~{added[-1]}) 새 파일: {out.name}", "system", ""])
    log("workflow_log.csv", [now(), master.name, "", "FM Master", f"01_ORIGINAL/MASTER_REF/{out.name}", "system", f"신규 FM {len(added)}건 등록(원본 유지)"])
    make_diff(master, out)
    print(f"[FM MASTER] {len(added)}건 등록 ({added[0]}~{added[-1]}) → {out.relative_to(ROOT)}  (원본 {master.name} 은 변경하지 않음)")
    return out

def sq_audit():
    """SQ mark 심사 필요서류 리스트(07_AUDIT/고객심사/SQ*.xlsx) ↔ 현재 문서체계 대조.
    - 필요서류 FM번호(안)의 번호체계 / 중복 / 공식 번호체계(SH-FM-NNN)와의 충돌
    - 필요서류명과 비슷한 기존 양식(FM Master, FM-101~121, 공식양식) 후보 (제안일 뿐 확정 아님)
    - 관련 기존 QP/WI 가 문서관리대장에 있는지
    결과: 07_AUDIT/고객심사/SQ_필요서류_대조보고서.md, SQ_필요서류_번호대조.csv (원본 SQ 파일은 수정하지 않음)"""
    from openpyxl import load_workbook
    import difflib
    adir = D["root_audit"] if "root_audit" in D else ROOT / "07_AUDIT" / "고객심사"
    sqs = sorted(adir.glob("SQ*.xlsx"), key=lambda f: f.stat().st_mtime)
    if not sqs:
        sys.exit("07_AUDIT/고객심사/ 에 SQ*.xlsx 가 없습니다")
    wb = load_workbook(sqs[-1], data_only=True)
    ws = wb["전체_필요서류리스트"]
    hdr = [c.value for c in ws[4]]
    ix = {h: i for i, h in enumerate(hdr)}
    rows = [[c.value for c in r] for r in ws.iter_rows(min_row=5) if r[0].value]
    # 기존 양식 이름 후보
    known = {}
    for f in master_files("FM_Master"):
        try:
            mw = load_workbook(f, data_only=True)["01_FM_Master"]
            for r in mw.iter_rows(min_row=2, values_only=True):
                if r[0] and r[1]:
                    known[str(r[0])] = str(r[1])
        except Exception:
            pass
    for f in D["orig"].rglob("*.xlsx"):
        if MASTER in f.parts:
            continue
        for n, t in xlsx_sheets(f).items():
            m = re.fullmatch(r"SH-FM-\d{3}", n.strip())
            if m:
                first = t.splitlines()[0].replace(n.strip(), "").strip() if t else ""
                if first:
                    known.setdefault(n.strip(), first)
    mapf_ = sq_map_file(adir)
    if mapf_.exists():   # SQ 필요서류에 새로 배정한 번호는 '기존 양식' 후보에서 제외 (자기 자신과 매칭 방지)
        assigned = {r["정식 SH-FM 번호"] for r in csv.DictReader(open(mapf_, encoding="utf-8-sig"))}
        known = {k: v for k, v in known.items() if k not in assigned}
    norm_ = lambda x: re.sub(r"[\s\-_/·()\[\]]", "", str(x or ""))
    ledger = {e[2]: e[3] for e in latest_ledger_entries()} if "latest_ledger_entries" in globals() else {e[2]: e[3] for e in ledger_entries()}
    scheme = lambda n: ("공식(SH-FM-NNN)" if re.fullmatch(r"SH-FM-\d{3}", n or "") else
                        "QP/WI 근거형(SH-FM-QP###-NN)" if re.fullmatch(r"SH-FM-(QP|WI)\d{3}-\d{2}", n or "") else
                        "신규형(SH-FM-XXX-N##)" if re.fullmatch(r"SH-FM-[A-Z]{3}-N\d{2}", n or "") else "기타/없음")
    cnt_no = collections.Counter(r[ix["FM문서번호"]] for r in rows)
    out_rows, sc = [], collections.Counter()
    for r in rows:
        no, name, fm = r[ix["NO"]], r[ix["필요서류(준비서류)"]], r[ix["FM문서번호"]]
        best = max(((difflib.SequenceMatcher(None, norm_(name), norm_(v)).ratio(), k, v) for k, v in known.items()), default=(0, "", ""))
        rel = str(r[ix["확정 연계문서/FM번호"]] or r[ix["관련 기존 문서(참고)"]] or "")
        refs = re.findall(r"SH-(?:QP|WI)-\d{3}", rel)
        miss = [x for x in refs if x not in ledger]
        sc[scheme(fm)] += 1
        out_rows.append([no, r[ix["구분"]], r[ix["번호"]], r[ix["우선순위"]], name, fm, scheme(fm), "중복" if cnt_no[fm] > 1 else "",
                         (f"{best[1]} {best[2]} ({best[0]:.2f})" if best[0] >= 0.6 else ""), r[ix["작성구분(자동추정)"]], r[ix["담당부서"]],
                         r[ix["목표완료월(제안)"]], ", ".join(refs), ", ".join(miss)])
    csvp = unique_path(adir / "SQ_필요서류_번호대조.csv")
    with open(csvp, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["NO", "구분", "번호", "우선순위", "필요서류", "SQ안 FM번호", "번호체계", "번호 중복", "유사 기존 양식 후보(제안, 확정 아님)", "작성구분", "담당부서", "목표완료월", "연계 QP/WI", "대장에 없는 연계 QP/WI"])
        w.writerows(out_rows)
    dup = sorted(k for k, v in cnt_no.items() if v > 1)
    names = collections.Counter(norm_(r[ix["필요서류(준비서류)"]]) for r in rows)
    same_name = sorted({r[ix["필요서류(준비서류)"]] for r in rows if names[norm_(r[ix["필요서류(준비서류)"]])] > 1})
    sim = [r for r in out_rows if r[8]]
    by = lambda k: collections.Counter(r[k] for r in out_rows)
    L = ["# SQ mark 필요서류 ↔ 현재 문서체계 대조", f"- 생성: {now()}", f"- SQ 파일: {sqs[-1].name} (수정하지 않음)", f"- 필요서류 {len(rows)}건", "",
         "## 번호체계", "", "| 체계 | 건수 |", "|---|---|"] + [f"| {k} | {v} |" for k, v in sc.most_common()]
    L += ["", f"- 공식 번호체계(`SH-FM-NNN`: FM Master 001~100 + 신규 배정 101~122)와 다른 SQ안 번호가 {len(rows) - sc['공식(SH-FM-NNN)']}건입니다. 현재 점검 도구(`doc_pattern`)는 SQ안 번호(`SH-FM-QP010-01` 등)를 문서번호로 인식하지 못합니다.",
          f"- SQ안 번호가 서로 겹치는 경우: {len(dup)}개 번호 ({', '.join(dup[:8])}{' …' if len(dup) > 8 else ''})",
          f"- 같은 필요서류명이 여러 행에 반복: {len(same_name)}종 ({', '.join(same_name[:8])}{' …' if len(same_name) > 8 else ''})", "",
          "## 분류별 현황", "", "| 구분 | 건수 | 기존 절차 연계 | 신규 작성 필요 |", "|---|---|---|---|"]
    for g, n in sorted(by(1).items()):
        L.append(f"| {g} | {n} | {sum(1 for r in out_rows if r[1] == g and r[9] == '기존 절차 연계')} | {sum(1 for r in out_rows if r[1] == g and r[9] == '신규 작성 필요')} |")
    L += ["", f"## 기존 양식과 이름이 비슷한 필요서류 ({len(sim)}건, 제안일 뿐 확정 아님)", "", "| NO | 필요서류 | SQ안 번호 | 유사 기존 양식 |", "|---|---|---|---|"]
    L += [f"| {r[0]} | {r[4]} | {r[5]} | {r[8]} |" for r in sim[:60]] or ["| (없음) | | | |"]
    bad = [r for r in out_rows if r[13]]
    L += ["", f"## 문서관리대장에 없는 연계 QP/WI ({len(bad)}건)"] + ([f"- NO {r[0]} {r[4]}: {r[13]}" for r in bad[:30]] or ["- 없음"])
    L += ["", "## 다음 결정 필요", "- SQ안 번호를 공식 번호(`SH-FM-NNN`)로 새로 배정할지, SQ안 체계를 정식 체계로 채택할지 (번호는 사람이 확정)",
          "- 같은 서류명의 중복/통합 여부, 기존 양식으로 대체 가능한 항목 확정", "- '관리번호'(기록번호 등)의 정의와 부여 규칙"]
    rp = unique_path(adir / "SQ_필요서류_대조보고서.md")
    rp.write_text("\n".join(L) + "\n", encoding="utf-8")
    log("workflow_log.csv", [now(), sqs[-1].name, "", "07_AUDIT/고객심사", rp.name, "system", f"SQ 필요서류 {len(rows)}건 대조 보고서 생성"])
    print(f"[SQ AUDIT] {len(rows)}건 | 번호체계 {dict(sc)} | 중복 번호 {len(dup)} | 유사 기존 양식 {len(sim)} → {rp.relative_to(ROOT)}")
    return rp

def sq_number():
    """SQ안 FM번호 → 정식 SH-FM-NNN 번호 배정 (사용자 지시). 기존 최대 번호 다음부터 SQ 리스트 NO 순서로 한 번만 배정한다.
    산출: 07_AUDIT/고객심사/SQ_FM번호_배정대응표.csv, SQ 사본(정식번호반영, 번호대응표 시트), FM Master 새 파일(신규 번호 등록).
    SQ 원본 파일과 이전 Master 는 수정하지 않는다. 이미 배정했다면 번호를 바꾸지 않는다."""
    from openpyxl import load_workbook
    from copy import copy
    adir = ROOT / "07_AUDIT" / "고객심사"
    mapf = adir / "SQ_FM번호_배정대응표.csv"
    if mapf.exists():
        print(f"[SQ NUMBER] 이미 배정됨: {mapf.relative_to(ROOT)} (번호는 다시 바꾸지 않음)")
        return
    sqs = sorted((f for f in adir.glob("SQ*.xlsx") if "정식번호반영" not in f.name), key=lambda f: f.stat().st_mtime)
    if not sqs:
        sys.exit("07_AUDIT/고객심사/SQ*.xlsx 없음")
    sq = sqs[-1]
    wb0 = load_workbook(sq, data_only=True)
    ws0 = wb0["전체_필요서류리스트"]
    hdr = [c.value for c in ws0[4]]
    ix = {h: i for i, h in enumerate(hdr)}
    rows = [[c.value for c in r] for r in ws0.iter_rows(min_row=5) if r[0].value]
    # 시작 번호: 시스템에서 확인되는 가장 큰 SH-FM-NNN 다음
    ids = {int(x[-3:]) for x in (fm_master_ids() | {f"SH-{n}" for f in D["orig"].rglob("*.xlsx") if MASTER not in f.parts for n, _ in split_units(f)}) if re.fullmatch(r"SH-FM-\d{3}", x)}
    ids |= {int(m) for f in D["orig"].rglob("SH-FM-122*") for m in re.findall(r"FM-(\d{3})", f.name)}
    start = max(ids) + 1
    # 비슷한/중복 후보 표시(확정 아님)
    simf = sorted(adir.glob("SQ_필요서류_번호대조*.csv"), key=lambda f: f.stat().st_mtime)
    sim = {}
    if simf:
        for r in csv.DictReader(open(simf[-1], encoding="utf-8-sig")):
            sim[str(r["NO"])] = r["유사 기존 양식 후보(제안, 확정 아님)"]
    nm = lambda x: re.sub(r"[\s\-_/·()\[\]]", "", str(x or ""))
    names = collections.Counter(nm(r[ix["필요서류(준비서류)"]]) for r in rows)
    mapping, order = {}, []
    for r in rows:
        old = r[ix["FM문서번호"]]
        if old and old not in mapping:
            mapping[old] = f"SH-FM-{start + len(mapping):03d}"
        order.append(r)
    with open(mapf, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["SQ NO", "구분", "번호", "필요서류(양식명)", "SQ안 번호(구)", "정식 SH-FM 번호", "작성구분", "담당부서", "담당자", "목표완료월", "연계 QP/WI", "플래그(확정 필요)"])
        for r in order:
            old = r[ix["FM문서번호"]]
            flags = []
            if sim.get(str(r[0])):
                flags.append("기존 양식과 중복 가능: " + sim[str(r[0])])
            if names[nm(r[ix["필요서류(준비서류)"]])] > 1:
                flags.append("같은 서류명이 여러 행에 있음(통합 검토)")
            rel = str(r[ix["확정 연계문서/FM번호"]] or r[ix["관련 기존 문서(참고)"]] or "")
            w.writerow([r[0], r[ix["구분"]], r[ix["번호"]], r[ix["필요서류(준비서류)"]], old, mapping.get(old, ""), r[ix["작성구분(자동추정)"]],
                        r[ix["담당부서"]], r[ix["담당자"]], r[ix["목표완료월(제안)"]], ", ".join(dict.fromkeys(re.findall(r"SH-(?:QP|WI)-\d{3}", rel))), " | ".join(flags)])
    # SQ 사본: 셀 전체가 SQ안 번호인 곳을 정식 번호로 교체 + 번호대응표 시트
    wb = load_workbook(sq)
    changed = 0
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value in mapping:
                    c.value = mapping[c.value]; changed += 1
    mws = wb.create_sheet("번호대응표")
    mws.append(["SQ안 번호(구)", "정식 SH-FM 번호", "필요서류(양식명)", "구분", "비고"])
    names_by_old = {r[ix["FM문서번호"]]: r[ix["필요서류(준비서류)"]] for r in rows}
    grp_by_old = {r[ix["FM문서번호"]]: r[ix["구분"]] for r in rows}
    for old, new in mapping.items():
        mws.append([old, new, names_by_old.get(old), grp_by_old.get(old), "사용자 지시로 정식 번호 배정(양식 미작성)"])
    outsq = unique_path(adir / f"{sq.stem}_정식번호반영.xlsx")
    wb.save(outsq)
    # FM Master 새 파일
    masters = sorted(master_files("FM_Master"), key=lambda f: f.stat().st_mtime)
    cur = masters[-1]
    mw = load_workbook(cur)
    ws = mw["01_FM_Master"]
    row = 2
    while ws.cell(row, 1).value:
        row += 1
    tmpl = row - 1
    byold = {r[ix["FM문서번호"]]: r for r in rows}
    for old, new in mapping.items():
        r = byold[old]
        rel = ", ".join(dict.fromkeys(re.findall(r"SH-(?:QP|WI)-\d{3}", str(r[ix["확정 연계문서/FM번호"]] or r[ix["관련 기존 문서(참고)"]] or ""))))
        flag = sim.get(str(r[0]))
        vals = [new, r[ix["필요서류(준비서류)"]], r[ix["요구사항(세부 추진 항목)"]], rel or None, "Rev.00", "신규 배정", "번호 배정 (양식 미작성)",
                f"SQ mark 필요서류 NO {r[0]} ({r[ix['구분']]} {r[ix['번호']]})", f"{sq.name} / SQ안 번호 {old}", r[ix["담당부서"]], None, None, None,
                ("기존 양식과 중복 가능(확정 필요): " + flag) if flag else None, f"양식 작성(목표 {r[ix['목표완료월(제안)']]}) 후 승인 흐름 진행"]
        for k, v in enumerate(vals, 1):
            cell = ws.cell(row, k, v)
            cell._style = copy(ws.cell(tmpl, k)._style)
        row += 1
    outm = unique_path(cur.parent / "SH_FM_Master_Rev00_20260929_수정본_SQ번호배정.xlsx")
    mw.save(outm)
    first, last = list(mapping.values())[0], list(mapping.values())[-1]
    for f_, note in ((outsq, f"SQ 필요서류 FM번호(안) {len(mapping)}건 → 정식 {first}~{last} 배정(사용자 지시)"), (outm, f"FM Master 에 SQ 신규 번호 {len(mapping)}건 등록({first}~{last})")):
        log("revision_history.csv", [dt.date.today(), f_.stem, "", "", note, "system", ""])
        log("workflow_log.csv", [now(), f_.name, "", "07_AUDIT" if f_ is outsq else "FM Master", str(f_.relative_to(ROOT)), "system", note])
    make_diff(cur, outm)
    print(f"[SQ NUMBER] {len(mapping)}건 배정 {first}~{last} | 대응표 {mapf.relative_to(ROOT)} | SQ 사본 {outsq.name}(셀 {changed}곳 교체) | Master {outm.name}")

SQ_NONDOC = ("설치", "제작", "보관대", "검사대", "컴퓨터", "KEY-LOCK", "장소선정")
SQ_STD = ("기준서", "관리표준", "검사협정서", "관리기준", "검사기준", "작업조건표", "파괴검사기준")

def sq_kind(name):
    n = str(name or "")
    if n.startswith("(") or any(k in n for k in SQ_NONDOC):
        return "비문서"      # 설치·제작·장소선정 과제 또는 요구사항 메모 — 양식이 아님
    if any(k in n for k in SQ_STD):
        return "기준서"
    return "기록양식"

def sq_drafts(priority="높음", overwrite=False):
    """SQ 필요서류 중 우선순위 해당 건의 양식 초안 → 03_EDIT/AUTO_DRAFT/SQ_<우선순위>_초안/
    번호(정식 SH-FM-NNN)는 배정대응표를 따른다. 항목·기준값·결재 방식 등 확정되지 않은 내용은 비워 두고 '확정 필요'로 표시한다.
    연속 번호 범위마다 워크북 1개(시트 = 양식 1개), 승인 전 '초안' 상태."""
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    adir = ROOT / "07_AUDIT" / "고객심사"
    mp = sq_map_file(adir)
    if not mp.exists():
        sys.exit("먼저 sqnumber 로 정식 번호를 배정하세요")
    sqf = sorted(adir.glob("SQ*정식번호반영*.xlsx"), key=lambda f: f.stat().st_mtime)[-1]
    ws0 = load_workbook(sqf, data_only=True)["전체_필요서류리스트"]
    hdr = [c.value for c in ws0[4]]
    ix = {h: i for i, h in enumerate(hdr)}
    extra = {str(r[0]): r for r in ws0.iter_rows(min_row=5, values_only=True) if r[0]}
    sel = [r for r in csv.DictReader(open(mp, encoding="utf-8-sig")) if extra[r["SQ NO"]][ix["우선순위"]] == priority]
    sel.sort(key=lambda r: int(r["정식 SH-FM 번호"][-3:]))
    if not sel:
        sys.exit(f"우선순위 '{priority}' 항목이 없습니다")
    out_dir = D["edit"] / "AUTO_DRAFT" / f"SQ_{priority}_초안"
    out_dir.mkdir(parents=True, exist_ok=True)
    company = cfg("qms_rules.yaml")["company"]["name"]
    thin = Side(style="thin", color="888888")
    box = Border(left=thin, right=thin, top=thin, bottom=thin)
    gray = PatternFill("solid", fgColor="E7E6E6")
    ftxt = lambda b=False, sz=10: Font(name="맑은 고딕", bold=b, size=sz)
    wrap = Alignment(wrap_text=True, vertical="center")
    def put(ws, ref, val, bold=False, size=10, fill=None, border=False, merge=None, align=None):
        c = ws[ref]
        c.value, c.font, c.alignment = val, ftxt(bold, size), align or wrap
        if fill: c.fill = fill
        if merge: ws.merge_cells(merge)
        if border:
            rng = ws[merge or ref]
            cells = [x for row in rng for x in row] if isinstance(rng, tuple) else [rng]
            for cc in cells:
                cc.border = box
    def sheet(wb, r):
        no, name = r["정식 SH-FM 번호"], r["필요서류(양식명)"].strip()
        kind = sq_kind(name)
        x = extra[r["SQ NO"]]
        dept = r["담당부서"] if r["담당부서"] and "미정" not in r["담당부서"] else "(부서 미정 — 확정 필요)"
        ws = wb.create_sheet(no)
        for col, w in zip("ABCDEFGH", (13, 16, 26, 22, 16, 10, 12, 14)):
            ws.column_dimensions[col].width = w
        put(ws, "A1", name, True, 14, merge="A1:H1")
        put(ws, "A2", f"{company} | 문서번호 {no} | Rev.00 | 문서상태: 초안(작성중)", merge="A2:H2")
        put(ws, "A3", f"주관부서(안): {dept} | 연계: {r['연계 QP/WI'] or '확정 필요'} | 구분: {kind} | SQ {r['구분']} {r['번호']} | 목표 {r['목표완료월']}", merge="A3:H3")
        req = str(x[ix["요구사항(세부 추진 항목)"]] or "").strip()
        put(ws, "A4", f"SQ 요구사항(참고): {req or '-'}", merge="A4:H4")
        ws.row_dimensions[4].height = 48
        row = 6
        if kind == "비문서":
            put(ws, f"A{row}", "양식 아님 — 설치·제작·장소선정 과제(또는 요구사항 메모)입니다. 이 번호를 문서로 사용할지, 별도 실행 체크리스트로 관리할지 확정이 필요합니다.", True, merge=f"A{row}:H{row+2}")
            row += 4
        elif kind == "기준서":
            for t in ("1. 목적", "2. 적용 범위", "3. 관리 항목 및 기준"):
                put(ws, f"A{row}", t + ("  (내용은 담당부서 확정 필요)" if t[0] != "3" else ""), True, fill=gray, border=True, merge=f"A{row}:H{row}")
                row += 1
                if t[0] != "3":
                    put(ws, f"A{row}", "", border=True, merge=f"A{row}:H{row+1}"); row += 2
            for k, h in enumerate(("항목", "기준(값)", "확인 방법", "주기", "담당", "비고")):
                pass
            heads = (("A", "B", "항목"), ("C", "D", "기준(값)"), ("E", "F", "확인 방법"), ("G", "G", "주기"), ("H", "H", "담당"))
            for a, b, h in heads:
                put(ws, f"{a}{row}", h, True, fill=gray, border=True, merge=f"{a}{row}:{b}{row}" if a != b else None)
            if True:
                ws[f"A{row}"].border = box
            row += 1
            for _ in range(8):
                for a, b, h in heads:
                    put(ws, f"{a}{row}", "", border=True, merge=f"{a}{row}:{b}{row}" if a != b else None)
                row += 1
            for t in ("4. 이상 시 조치", "5. 관련 문서·기록"):
                put(ws, f"A{row}", t, True, fill=gray, border=True, merge=f"A{row}:H{row}"); row += 1
                put(ws, f"A{row}", (f"연계: {r['연계 QP/WI']}" if t[0] == "5" and r["연계 QP/WI"] else ""), border=True, merge=f"A{row}:H{row+1}"); row += 2
            put(ws, f"A{row}", "개정이력", True, fill=gray, border=True, merge=f"A{row}:H{row}"); row += 1
            for a, b, h in (("A", "A", "개정"), ("B", "B", "개정일"), ("C", "F", "개정 내용"), ("G", "G", "작성"), ("H", "H", "승인")):
                put(ws, f"{a}{row}", h, True, fill=gray, border=True, merge=f"{a}{row}:{b}{row}" if a != b else None)
            row += 1
            for a, b, h in (("A", "A", "Rev.00"), ("B", "B", ""), ("C", "F", "초안"), ("G", "G", ""), ("H", "H", "")):
                put(ws, f"{a}{row}", h, border=True, merge=f"{a}{row}:{b}{row}" if a != b else None)
            row += 2
        else:
            put(ws, f"A{row}", "작성일:                         / 기록번호:                  작성자 성명:", merge=f"A{row}:H{row}"); row += 2
            heads = ("일자", "품번 / LOT", "점검·검사 항목(확정 필요)", "기준", "결과(측정값)", "판정", "확인(서명)", "비고")
            for k, h in enumerate(heads):
                put(ws, f"{'ABCDEFGH'[k]}{row}", h, True, fill=gray, border=True)
            row += 1
            for _ in range(12):
                for k in range(8):
                    put(ws, f"{'ABCDEFGH'[k]}{row}", "", border=True)
                row += 1
            row += 1
        if kind == "기록양식":
            put(ws, f"A{row}", "종합결과 / 관련 증빙번호:", merge=f"A{row}:H{row}"); row += 2
        # 결재란: 결재 방식(작성/검토/승인 여부)은 미확정 → 기본 3단 표기, 성명·서명·일자는 기록 시 기재
        for k, h in enumerate(("작성", "검토", "승인")):
            col = "ABC"[k] if False else ("A", "C", "F")[k]
        put(ws, f"A{row}", "작성", True, fill=gray, border=True, merge=f"A{row}:B{row}")
        put(ws, f"C{row}", "검토", True, fill=gray, border=True, merge=f"C{row}:E{row}")
        put(ws, f"F{row}", "승인", True, fill=gray, border=True, merge=f"F{row}:H{row}")
        row += 1
        for lab in ("성명:", "서명:", "일자:", "직책 / 역할:"):
            put(ws, f"A{row}", lab, border=True, merge=f"A{row}:B{row}")
            put(ws, f"C{row}", lab, border=True, merge=f"C{row}:E{row}")
            put(ws, f"F{row}", lab, border=True, merge=f"F{row}:H{row}")
            row += 1
        row += 1
        put(ws, f"A{row}", f"보관위치(안): {dept} 기록철 | 보존기간: __________________", merge=f"A{row}:H{row}"); row += 1
        put(ws, f"A{row}", f"{no} · Rev.00 | 초안 — 결재 방식·항목·기준은 담당부서 확정 후 개정", merge=f"A{row}:H{row}")
        ws.page_setup.orientation, ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = "portrait", 1, 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        return kind
    # 연속 번호 구간별 워크북
    runs, cur = [], [sel[0]]
    for r in sel[1:]:
        if int(r["정식 SH-FM 번호"][-3:]) == int(cur[-1]["정식 SH-FM 번호"][-3:]) + 1:
            cur.append(r)
        else:
            runs.append(cur); cur = [r]
    runs.append(cur)
    made, listing = [], []
    for grp in runs:
        a, b = grp[0]["정식 SH-FM 번호"], grp[-1]["정식 SH-FM 번호"]
        wb = Workbook()
        idx = wb.active
        idx.title = "00_안내및목록"
        put(idx, "A1", f"SQ mark 심사 필요 양식 초안 {len(grp)}종 (우선순위 {priority})", True, 14, merge="A1:H1")
        put(idx, "A2", f"{company} | {a}~{b} | Rev.00 | 초안(작성중) — 승인 전", merge="A2:H2")
        put(idx, "A3", "항목·기준값·결재 방식·보존기간은 담당부서가 확정해야 하며, 이 초안은 자동으로 채우지 않았습니다. 확정 후 01_ORIGINAL 에 올려 검토·승인 흐름으로 진행합니다.", merge="A3:H3")
        ws_h = ("번호", "양식명", "유형", "담당부서", "목표월", "연계 QP/WI", "플래그", "")
        for k, h in enumerate(ws_h[:7]):
            put(idx, f"{'ABCDEFG'[k]}5", h, True, fill=gray, border=True)
        for col, w in zip("ABCDEFG", (13, 30, 10, 14, 10, 18, 40)):
            idx.column_dimensions[col].width = w
        for i, r in enumerate(grp):
            kind = sheet(wb, r)
            vals = (r["정식 SH-FM 번호"], r["필요서류(양식명)"], kind, r["담당부서"], r["목표완료월"], r["연계 QP/WI"], r["플래그(확정 필요)"][:80])
            for k, v in enumerate(vals):
                put(idx, f"{'ABCDEFG'[k]}{6+i}", v, border=True)
            listing.append((r["정식 SH-FM 번호"], r["필요서류(양식명)"], kind, r["담당부서"], r["목표완료월"], r["플래그(확정 필요)"]))
        fname = out_dir / f"{a}-{b[-3:]}_SQ{priority}_양식초안_Rev00.xlsx"
        fname = fname if overwrite else unique_path(fname)   # overwrite 는 자동 생성 직후 정정용(사람이 고친 초안은 덮어쓰지 않음)
        wb.save(fname)
        made.append(fname)
        log("revision_history.csv", [dt.date.today(), fname.stem, "00", "", f"SQ {priority} 양식 초안 {len(grp)}종 생성({a}~{b}, 초안·미승인)", "system", ""])
        log("workflow_log.csv", [now(), fname.name, "", "SQ 필요서류", str(fname.relative_to(ROOT)), "system", f"양식 초안 {len(grp)}종 생성(AUTO_DRAFT)"])
    kc = collections.Counter(x[2] for x in listing)
    L = [f"# SQ 우선순위 '{priority}' 양식 초안", f"- 생성: {now()}", f"- 총 {len(listing)}건 — 기록양식 {kc['기록양식']} / 기준서 {kc['기준서']} / 비문서(설치·제작·장소선정·메모) {kc['비문서']}",
         "- 항목·기준값·결재 방식·보존기간은 비워 두었습니다(담당부서 확정 필요).", "", "| 번호 | 양식명 | 유형 | 담당부서 | 목표월 | 플래그 |", "|---|---|---|---|---|---|"]
    L += [f"| {a} | {b} | {c} | {d} | {e} | {f} |" for a, b, c, d, e, f in listing]
    L += ["", "## 파일"] + [f"- {m.relative_to(ROOT)}" for m in made]
    rp = (out_dir / "초안_목록.md") if overwrite else unique_path(out_dir / "초안_목록.md")
    rp.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[SQ DRAFTS] {len(listing)}건 (기록양식 {kc['기록양식']} / 기준서 {kc['기준서']} / 비문서 {kc['비문서']}) → {len(made)}개 워크북: " + ", ".join(m.name for m in made))
    return made

def fullcycle():
    """전체 사이클(승인 직전까지): 신규 검색 → 점검(+AUTO_DRAFT) → 수정완료분 재감사(+DIFF) → Release Gate → 승인 패키지.
    승인(approve/sign)과 FINAL 배포(finalize)는 사람이 실제 승인한 뒤 직접 실행한다."""
    scan()
    run()
    recheck()
    release_gate()
    for sub in ("승인대기", "검토완료", "승인완료"):
        for f in sorted((D["appr"] / sub).iterdir()):
            if f.is_file() and f.name != ".gitkeep" and not list((D["appr"] / "PACKAGES").glob(f"{f.stem}*")):
                build_package(f, cfg("qms_rules.yaml")["classify"].get(prefix_of(f.name), ""), sub)
    print("\n[다음 단계] 실제 승인 후 사람이 실행: approve <파일> → sign <파일> → finalize  (자동 승인 없음)")

def scan():
    """1. 신규 문서 검색: 아직 검토되지 않은 파일 목록."""
    done, new = processed(), []
    for p in sorted(D["orig"].rglob("*")):
        if p.is_file() and p.name != ".gitkeep" and MASTER not in p.parts and sha(p) not in done:   # 관리자료(MASTER_REF)는 검토 대상 아님
            new.append(p)
    print(f"신규 문서 {len(new)}건")
    for p in new:
        print("  -", p.relative_to(ROOT))
    return new

def status():
    """9. FINAL 가능 여부 표시: 04_APPROVAL 의 문서별 상태."""
    for sub in ("승인대기", "검토완료", "승인완료"):
        for p in sorted((D["appr"] / sub).iterdir()):
            if p.is_file() and p.name != ".gitkeep":
                typ = cfg("qms_rules.yaml")["classify"].get(prefix_of(p.name), "")
                docno, issues, approved, _ = check(p, typ, final_stage=True)
                ok = not issues and sub == "승인완료"
                why = "가능" if ok else ("승인 완료 후 이동" if not issues and sub != "승인완료" else f"불가 ({len(issues)}건 이슈)")
                print(f"[{sub}] {p.name}: FINAL {why}")

def advance(name, src, dst, note):
    s = D["appr"] / src / name
    if not s.exists():
        sys.exit(f"{s} 없음")
    shutil.move(str(s), D["appr"] / dst / name)   # 04 내부 상태 이동(복사본)
    log("workflow_log.csv", [now(), name, "", f"04_APPROVAL/{src}", f"04_APPROVAL/{dst}", "human", note])
    print(f"{name}: {src} → {dst}")
    stem = Path(name).stem
    if dst == "승인완료" and not package_dirs(stem):   # 패키지가 없으면 먼저 생성
        f_ = D["appr"] / dst / name
        build_package(f_, cfg("qms_rules.yaml")["classify"].get(prefix_of(name), ""), dst)
    for st in package_dirs(stem):
        if (st / "STATUS.md").exists():
            with open(st / "STATUS.md", "a", encoding="utf-8") as f:
                f.write(f"- {now()} {src} → {dst} ({note})\n")
        if dst == "승인완료":   # 사람이 sign 을 실행한 경우에만 승인 표시 파일 생성 (자동 생성 금지)
            mkf = st / approval_marker()
            if not mkf.exists():
                mkf.write_text(f"APPROVED\napproved_at={dt.datetime.now().isoformat(timespec='seconds')}\n"
                               f"document={name}\nnote=사용자가 sign 명령으로 승인 완료를 확인한 후 생성된 표시파일\n", encoding="utf-8")
                print(f"  → 승인 표시 파일 생성: {mkf.relative_to(ROOT)}")

def gates():
    reg = registry(cfg("document_number_rules.yaml")["doc_pattern"])
    for ap, g in cfg("gate_rules.yaml")["gate"].items():
        forms = g.get("forms") or [g.get("form")]
        miss = [f for f in forms if norm(f) not in reg]
        print(f"{ap} [{g['status']}] " + ("충족" if not miss else f"미비: {', '.join(miss)}"))


# ---------------- 최종 처리 ----------------
def to_pdf(src: Path, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    if src.suffix.lower() == ".pdf":
        return safe_copy(src, outdir)
    if not shutil.which("soffice"):
        print("  ! soffice 없음: PDF 변환 생략"); return None
    out = outdir / (src.stem + ".pdf")
    if out.exists():   # 덮어쓰기 금지
        outdir = outdir / f"v{dt.datetime.now():%Y%m%d%H%M%S}"; outdir.mkdir()
        out = outdir / (src.stem + ".pdf")
    r = subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(outdir), str(src)],
                       capture_output=True, text=True, timeout=180)
    if not out.exists():
        print("  ! PDF 변환 실패:", (r.stderr or r.stdout).strip()[-200:])
        return None
    return out

RELEASED = D["final"] / "RELEASED"

DISTRIBUTION = D["final"] / "DISTRIBUTION"          # 배포목록·최종보고서·무결성 CSV 스냅샷
ROLLBACK = D["hist"] / "ROLLBACK_BACKUP"            # 기존 FINAL 교체 전 롤백용 백업 (자동 복원은 하지 않음)

def split_pdf(path):
    """양식 워크북(xlsx)을 양식(시트)별 PDF 로 분리한다. LibreOffice(soffice)가 있는 PC 에서 쓴다.
    - 승인·릴리스된 파일(05_FINAL/RELEASED 안)만 05_FINAL/배포본/양식별PDF/<파일명>/ 에 저장한다.
    - 그 밖의 파일(승인 전)은 03_EDIT/PDF_미리보기/<파일명>/ 에 '미승인_' 접두어로 저장한다(배포본 아님).
    - 원본 워크북은 수정하지 않는다(임시 폴더에서 시트 하나만 남긴 사본을 변환). 기존 PDF 는 덮어쓰지 않는다(_vN)."""
    import tempfile, openpyxl
    src = Path(path)
    if not src.exists() or src.suffix.lower() != ".xlsx":
        sys.exit(f"xlsx 파일을 지정하세요: {path}")
    if not shutil.which("soffice"):
        sys.exit("soffice 없음: LibreOffice 가 설치되고 PATH 에 잡힌 PC 에서 실행하세요")
    released = RELEASED.resolve() in src.resolve().parents
    outdir = (D["final"] / "배포본" / "양식별PDF" if released else D["edit"] / "PDF_미리보기") / src.stem
    outdir.mkdir(parents=True, exist_ok=True)
    prefix = "" if released else "미승인_"
    wb0 = openpyxl.load_workbook(src)
    titles = [n for n in wb0.sheetnames if not n.startswith("00") and not n.startswith("0_")] or list(wb0.sheetnames)
    made, failed = [], []
    for t in titles:
        label = re.sub(r'[\\/:*?"<>|]+', "_", re.sub(r"^SH-FM-\d+\s*", "", str(wb0[t]["A1"].value or "").strip()))[:40]
        with tempfile.TemporaryDirectory() as td:
            wb = openpyxl.load_workbook(src)
            for other in wb.sheetnames:
                if other != t:
                    del wb[other]
            ws = wb[t]  # 임시 사본에만 적용: 가로 한 쪽 폭에 맞춰 열이 쪽 밖으로 잘리지 않게 함
            # 시트에 이미 '한 페이지 맞춤(폭 1·높이 1) + 방향'이 지정돼 있으면 그대로 존중한다(양식 설계 의도).
            # 없으면 가로 한 쪽 폭에 맞춘다.
            pre_fit = bool(ws.sheet_properties.pageSetUpPr and ws.sheet_properties.pageSetUpPr.fitToPage
                           and ws.page_setup.fitToHeight == 1 and ws.page_setup.orientation)
            if not pre_fit:
                ws.page_setup.orientation = "landscape"
                ws.page_setup.fitToWidth = 1
                ws.page_setup.fitToHeight = 0
                ws.sheet_properties.pageSetUpPr = openpyxl.worksheet.properties.PageSetupProperties(fitToPage=True)
            ws.page_setup.paperSize = ws.PAPERSIZE_A4
            # 병합된 머리글 칸의 글이 줄바꿈으로 잘리지 않도록 임시 사본에서만 행 높이를 늘린다
            import math
            for mr in list(ws.merged_cells.ranges):
                cell = ws.cell(mr.min_row, mr.min_col)
                if mr.min_row != mr.max_row or not isinstance(cell.value, str) or not cell.alignment.wrap_text:
                    continue
                wsum = sum((ws.column_dimensions[openpyxl.utils.get_column_letter(c)].width or 8.43)
                           for c in range(mr.min_col, mr.max_col + 1))
                sz = cell.font.sz or 11
                vis = sum(2 if ord(ch) > 127 else 1 for ch in cell.value) * (sz / 11.0)
                need = math.ceil(vis / max(wsum, 1)) * sz * 1.45 + 4
                cur = ws.row_dimensions[mr.min_row].height or 15
                if cur < need:
                    ws.row_dimensions[mr.min_row].height = need
            # 작성칸(빈 행)에 테두리가 없으면 인쇄 시 보이지 않으므로 임시 사본에만 얇은 테두리를 그린다
            hdr = next((r for r in range(3, min(ws.max_row, 12) + 1)
                        if sum(1 for c in ws[r] if c.value not in (None, "")) >= 3), None)
            if hdr:
                thin = openpyxl.styles.Side(style="thin", color="999999")
                box = openpyxl.styles.Border(left=thin, right=thin, top=thin, bottom=thin)
                for r in range(hdr + 1, ws.max_row + 1):
                    for c in range(1, ws.max_column + 1):
                        cell = ws.cell(r, c)
                        if not (cell.border and cell.border.left and cell.border.left.style):
                            cell.border = box
                ws.print_area = f"A1:{openpyxl.utils.get_column_letter(ws.max_column)}{ws.max_row}"
            tmp = Path(td) / f"{t}.xlsx"
            wb.save(tmp)
            r = subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", td, str(tmp)],
                               capture_output=True, text=True, timeout=180)
            pdf = Path(td) / f"{t}.pdf"
            if not pdf.exists():
                failed.append((t, (r.stderr or r.stdout).strip()[-120:]))
                continue
            dest = unique_path(outdir / f"{prefix}{t}_{label}.pdf" if label else outdir / f"{prefix}{t}.pdf")
            shutil.copy2(pdf, dest)
            made.append((t, dest))
    with open(unique_path(outdir / f"{prefix}양식별PDF_목록.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["시트(양식)", "PDF", "SHA-256", "구분"])
        for t, d in made:
            w.writerow([t, d.name, sha(d), "배포용(승인·릴리스본)" if released else "미리보기(미승인, 배포본 아님)"])
    log("revision_history.csv", [dt.date.today(), src.stem, "", "", f"양식별 PDF {len(made)}개 생성({'배포' if released else '미리보기·미승인'}): {outdir.relative_to(ROOT)}" + (f", 실패 {len(failed)}" if failed else ""), "system", ""])
    print(f"[SPLITPDF] {src.name}: PDF {len(made)}개 → {outdir.relative_to(ROOT)}" + ("" if released else " (미승인 미리보기, 배포본 아님)"))
    for t, e in failed:
        print(f"  ! {t} 변환 실패: {e}")
    return made

def approval_marker():
    return (cfg("qms_rules.yaml").get("final_operation") or {}).get("approval_marker", "APPROVED.txt")

def package_dirs(stem):
    return [d for d in sorted((D["appr"] / "PACKAGES").glob(f"{stem}*")) if d.is_dir()]

def rollback_backup(path: Path):
    """기존 FINAL 을 이동하기 전에 06_HISTORY/ROLLBACK_BACKUP 에 사본 보관."""
    ROLLBACK.mkdir(parents=True, exist_ok=True)
    dst = unique_path(ROLLBACK / f"{dt.datetime.now():%Y%m%d_%H%M%S}_{path.name}")
    shutil.copytree(path, dst) if path.is_dir() else shutil.copy2(path, dst)
    return dst

def rollbackcheck():
    """롤백 백업 후보만 제시한다 (자동 롤백/복원 없음)."""
    bk = sorted(ROLLBACK.glob("*"), key=lambda q: q.stat().st_mtime, reverse=True) if ROLLBACK.exists() else []
    if not bk:
        print("[ROLLBACK] 롤백 백업이 없습니다.")
        return
    print("[ROLLBACK] 롤백은 자동 실행하지 않습니다. 최근 백업 후보:")
    for q in bk[:10]:
        print("  -", q.relative_to(ROOT))
    print("필요 시 해당 백업을 검토한 뒤 사람이 수동 복원하세요.")

def verify_release(rel: Path):
    """RELEASED/<문서>/Rev<NN>/MANIFEST.json 의 SHA-256 을 다시 계산해 변조·누락 검사. 반환 [(파일, PASS/FAIL, 비고)]"""
    mf = rel / "MANIFEST.json"
    if not mf.exists():
        return [("MANIFEST.json", "FAIL", "매니페스트 없음")]
    m = json.loads(mf.read_text(encoding="utf-8"))
    out = []
    for f in m["files"]:
        fp = rel / f["name"]
        if not fp.exists():
            out.append((f["name"], "FAIL", "파일 없음(삭제/이동됨)"))
        elif sha(fp) != f["sha256"]:
            out.append((f["name"], "FAIL", "SHA-256 불일치(변조 의심)"))
        else:
            out.append((f["name"], "PASS", f["sha256"][:12]))
    return out

def integrity_check(write_report=True):
    """05_FINAL/RELEASED 전체 무결성 검사 → 05_FINAL/RELEASED/무결성검사_*.md"""
    rows = []
    for mf in sorted(RELEASED.rglob("MANIFEST*.json")):
        rel = mf.parent
        for name, st, note in verify_release(rel):
            rows.append((str(rel.relative_to(RELEASED)), name, st, note))
    bad = [r for r in rows if r[2] == "FAIL"]
    print(f"[INTEGRITY] 파일 {len(rows)}개 중 FAIL {len(bad)}개" + ("" if not bad else " → " + "; ".join(f"{r[0]}/{r[1]}:{r[3]}" for r in bad[:3])))
    if write_report:
        lines = ["# 무결성 검사 (SHA-256)", f"- 생성: {now()}", f"- 결과: {'FAIL' if bad else 'PASS'} (검사 {len(rows)}개 / FAIL {len(bad)}개)", "",
                 "| 릴리스 | 파일 | 결과 | 비고 |", "|---|---|---|---|"] + [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows]
        RELEASED.mkdir(parents=True, exist_ok=True)
        unique_path(RELEASED / "무결성검사.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        DISTRIBUTION.mkdir(parents=True, exist_ok=True)
        with open(unique_path(DISTRIBUTION / f"final_integrity_{dt.datetime.now():%Y%m%d_%H%M%S}.csv"), "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["release", "file", "result", "note"])
            w.writerows(rows)
    return not bad

def release_record(p: Path, docno, rev, pdf, dist, gate_rows):
    """05_FINAL/RELEASED/<문서번호>/Rev<NN>/ 에 릴리스본(문서·PDF·배포본)과 MANIFEST.json 저장, 이전 Rev 는 06_HISTORY 로 이동."""
    tag = f"Rev{rev}" if rev != "" else "RevNA"
    m_ = re.search(cfg("document_number_rules.yaml")["doc_pattern"], p.name)
    if docno == p.stem and m_:   # 번호 범위 워크북: 파일명 전체 대신 문서번호(범위)를 릴리스 폴더명으로
        docno = m_.group(0)
    base = RELEASED / docno
    rel, n = base / tag, 2
    while rel.exists():
        rel = base / f"{tag}_v{n}"
        n += 1
    rel.mkdir(parents=True)
    files = [("문서", p)] + ([("PDF", pdf)] if pdf else []) + ([("배포본", dist)] if dist else [])
    entries = []
    for role, f in files:
        dst = rel / f.name
        shutil.copy2(f, dst)
        if sha(dst) != sha(f):   # 복사 직후 무결성 확인
            raise RuntimeError(f"복사 무결성 오류: {f.name}")
        entries.append({"role": role, "name": f.name, "sha256": sha(dst), "size": dst.stat().st_size})
    (rel / "MANIFEST.json").write_text(json.dumps({
        "document_no": docno, "revision": tag, "released_at": now(), "source": str(p.relative_to(ROOT)),
        "gates": [{"gate": a, "result": b, "note": c} for a, b, c in gate_rows], "files": entries}, ensure_ascii=False, indent=2), encoding="utf-8")
    moved = []
    for legacy in sorted(RELEASED.iterdir()):   # 예전 이름(파일명 전체)으로 만든 같은 문서의 릴리스 폴더도 이전 Rev 로 취급
        if legacy.is_dir() and legacy != base and (re.search(cfg("document_number_rules.yaml")["doc_pattern"], legacy.name) or [None])[0] == docno:
            dest = unique_path(D["hist"] / "이전버전" / docno / f"RELEASED_{legacy.name}")
            dest.parent.mkdir(parents=True, exist_ok=True)
            rollback_backup(legacy)
            shutil.move(str(legacy), dest)
            moved.append(f"{legacy.name} → 06_HISTORY/이전버전/{docno}/{dest.name}")
    for old in sorted(base.iterdir()):   # 이전 Rev → 06_HISTORY (이동, 삭제 아님)
        if old.is_dir() and old != rel:
            dest = unique_path(D["hist"] / "이전버전" / docno / f"RELEASED_{old.name}")
            dest.parent.mkdir(parents=True, exist_ok=True)
            rollback_backup(old)
            shutil.move(str(old), dest)
            moved.append(f"{old.name} → 06_HISTORY/이전버전/{docno}/{dest.name}")
    return rel, entries, moved

def finalize():
    num = cfg("document_number_rules.yaml")
    released, blocked = [], []
    for p in sorted((D["appr"] / "승인완료").iterdir()):
        if not p.is_file() or p.name == ".gitkeep":
            continue
        typ = cfg("qms_rules.yaml")["classify"].get(prefix_of(p.name), "")
        h = sha(p)
        if (D["log"] / "finalized_hashes.txt").exists() and h in (D["log"] / "finalized_hashes.txt").read_text().split():
            continue
        # FINAL 직전 재검증 (문서상태 승인완료 필수)
        docno, issues, approved, units = check(p, typ, final_stage=True)
        if units:
            for ud, ui, ua, ut in units:
                summary_table(p, ud, ui, ua, stage="FINAL 직전 재검증", text=ut, label=f"{p.name} ▸ {ud}", quiet=True)
        else:
            summary_table(p, docno, issues, approved, stage="FINAL 직전 재검증")
        if issues:
            cats = {c for c, _, _ in issues}
            tag = "문서번호 불일치로 FINAL 이동 금지" if "문서번호" in cats else "검토 이슈로 FINAL 이동 금지"
            folder = next((ERR_DIR[c] for c in ERR_DIR if c in cats), DEFAULT_ERR_DIR)
            safe_copy(p, D["rev"] / folder)
            cand = write_candidate(p, docno, issues)
            for c, m, _ in issues:
                log("error_log.csv", [now(), docno or p.stem, c, m, "OPEN"])
            log("workflow_log.csv", [now(), docno or p.stem, "", "04_APPROVAL/승인완료", f"02_REVIEW/{folder}", "system", tag])
            print(f"[BLOCKED] {p.name}: {tag} ({len(issues)}건) → 02_REVIEW/{folder}")
            blocked.append((p.name, tag))
            continue
        if not print_gate(p, "승인완료"):
            log("workflow_log.csv", [now(), docno or p.stem, "", "04_APPROVAL/승인완료", "(보류)", "system", "FINAL Gate FAIL: 배포 불가"])
            print(f"[BLOCKED] {p.name}: FINAL Gate FAIL → 05_FINAL 이동 안 함")
            blocked.append((p.name, "FINAL Gate FAIL"))
            continue
        docno = docno or p.stem
        rev = (re.search(num["revision_pattern"], p.name) or [None, ""])[1]
        sub = "EXCEL" if p.suffix.lower() in (".xlsx", ".xls", ".csv") else "WORD"
        # 같은 문서번호의 기존 최종본 → 06_HISTORY/이전버전 (이동, 삭제 아님)
        old_rev = ""
        for old in [f for f in (D["final"] / sub).iterdir() if f.is_file() and f.name != ".gitkeep"
                    and (re.search(num["doc_pattern"], f.name) or [None])[0] == (re.search(num["doc_pattern"], p.name) or [None])[0]
                    and f.name != p.name]:
            om = re.search(num["revision_pattern"], old.name)
            old_rev = om.group(1) if om else ""
            obsolete_dir = D["hist"] / "이전버전" / docno   # 구버전은 삭제하지 않고 이동
            obsolete_dir.mkdir(parents=True, exist_ok=True)
            rollback_backup(old)
            old.rename(obsolete_dir / f"{old.stem}__superseded{old.suffix}")
            for oldpdf in (D["final"] / "PDF").glob(f"{old.stem}.pdf"):
                rollback_backup(oldpdf)
                oldpdf.rename(obsolete_dir / f"{oldpdf.stem}__superseded.pdf")
        safe_copy(p, D["final"] / sub)
        pdf = to_pdf(p, D["final"] / "PDF")
        dist = None
        if pdf and approved:   # 승인된 문서만 배포본
            dist = safe_copy(pdf, D["final"] / "배포본", f"{pdf.stem}_배포본_{dt.date.today():%Y%m%d}.pdf")
        safe_copy(p, D["hist"] / "변경이력" / docno, f"{dt.datetime.now():%Y%m%d%H%M%S}_{p.name}")
        log("revision_history.csv", [dt.date.today(), docno, old_rev, rev, "승인 후 최종 발행", "", "승인완료"])
        log("workflow_log.csv", [now(), docno, rev, "04_APPROVAL/승인완료", "05_FINAL", "system",
                                 "PDF/배포본 생성" if dist else "PDF 변환 실패(배포본 없음)"])
        with open(D["log"] / "finalized_hashes.txt", "a") as f:
            f.write(h + "\n")
        for pk in sorted((D["appr"] / "PACKAGES").glob(f"{p.stem}*")):
            if pk.is_dir():
                shutil.copytree(pk, unique_path(D["hist"] / "변경이력" / docno / f"PACKAGE_{dt.datetime.now():%Y%m%d%H%M%S}_{pk.name}"))
        rel, entries, moved = release_record(p, docno, rev, pdf, dist, gate_check(p, "승인완료"))
        ok_int = all(st == "PASS" for _, st, _ in verify_release(rel))   # 릴리스 직후 무결성 검사
        released.append((docno, rev, p.name, rel, entries, moved, ok_int, bool(dist)))
        print(f"[FINAL  ] {p.name} → 05_FINAL/{sub}, RELEASED/{docno}/{rel.name}, PDF{'+배포본' if dist else ' 없음'}, 무결성 {'PASS' if ok_int else 'FAIL'}, 06_HISTORY 백업")
    if released or blocked:
        finish_report(released, blocked)

def finish_report(released, blocked):
    """배포목록(누적 CSV) + 최종보고서(MD) → 05_FINAL/RELEASED/"""
    RELEASED.mkdir(parents=True, exist_ok=True)
    lst = RELEASED / "배포목록.csv"
    new = not lst.exists()
    with open(lst, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["배포일", "문서번호", "Rev", "릴리스 경로", "문서 SHA-256", "PDF", "배포본", "무결성"])
        for docno, rev, name, rel, ents, moved, ok_int, has_dist in released:
            sha_doc = next(e["sha256"] for e in ents if e["role"] == "문서")
            w.writerow([dt.date.today(), docno, rev, str(rel.relative_to(ROOT)), sha_doc,
                        "O" if any(e["role"] == "PDF" for e in ents) else "X", "O" if has_dist else "X", "PASS" if ok_int else "FAIL"])
    lines = ["# 최종 보고서 (FINAL Release)", f"- 생성: {now()}", f"- 릴리스 {len(released)}건 / 보류 {len(blocked)}건", "",
             "## 릴리스", "", "| 문서번호 | Rev | 파일 | 릴리스 경로 | PDF | 배포본 | 무결성 | 이전 Rev 이동 |", "|---|---|---|---|---|---|---|---|"]
    for docno, rev, name, rel, ents, moved, ok_int, has_dist in released:
        lines.append(f"| {docno} | {rev} | {name} | {rel.relative_to(ROOT)} | {'O' if any(e['role']=='PDF' for e in ents) else 'X'} | {'O' if has_dist else 'X'} | {'PASS' if ok_int else 'FAIL'} | {'; '.join(moved) or '-'} |")
    if not released:
        lines.append("| (릴리스 없음) | | | | | | | |")
    lines += ["", "## 보류 (FINAL 이동 안 함)"] + ([f"- {n}: {t}" for n, t in blocked] or ["- 없음"])
    lines += ["", "## 비고", "- PDF 변환이 불가능한 환경에서는 PDF/배포본이 생성되지 않으며, 배포 가능 여부는 담당자가 별도 확인한다.",
              "- 승인 전 문서는 배포본을 만들지 않는다. 구버전(이전 Rev)은 삭제하지 않고 06_HISTORY 로 이동한다."]
    out = unique_path(RELEASED / "최종보고서.md")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    DISTRIBUTION.mkdir(parents=True, exist_ok=True)   # 배치별 스냅샷 (DISTRIBUTION)
    stamp = f"{dt.datetime.now():%Y%m%d_%H%M%S}"
    shutil.copy2(lst, unique_path(DISTRIBUTION / f"distribution_list_{stamp}.csv"))
    shutil.copy2(out, unique_path(DISTRIBUTION / f"FINAL_RELEASE_REPORT_{stamp}.md"))
    print(f"[REPORT ] 배포목록 {lst.relative_to(ROOT)} / 최종보고서 {out.relative_to(ROOT)} (+ 05_FINAL/DISTRIBUTION 스냅샷)")

def final_report_cmd():
    """현재까지의 릴리스 현황(RELEASED 매니페스트)과 무결성 결과로 최종 보고서를 다시 생성."""
    ok = integrity_check(write_report=True)
    rel = []
    for mf in sorted(RELEASED.rglob("MANIFEST.json")):
        m = json.loads(mf.read_text(encoding="utf-8"))
        rel.append((m["document_no"], m["revision"], m["released_at"], len(m["files"])))
    lines = ["# SHINHWA QMS FINAL RELEASE REPORT (현황)", f"- 생성: {now()}", f"- 릴리스 {len(rel)}건 / 무결성 {'PASS' if ok else 'FAIL'}", "",
             "| 문서번호 | Rev | 릴리스 일시 | 파일 수 |", "|---|---|---|---|"] + [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rel]
    lines += ["", "## 운영 원칙", "- 원본은 보존", "- 이전 Rev는 06_HISTORY 보관, 교체 전 롤백 백업 생성", "- 배포 전 Release Gate PASS + 승인 표시 파일 확인", "- 변경이력 및 배포목록 유지"]
    DISTRIBUTION.mkdir(parents=True, exist_ok=True)
    out = unique_path(DISTRIBUTION / f"FINAL_RELEASE_REPORT_{dt.datetime.now():%Y%m%d_%H%M%S}.md")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[REPORT ] {out.relative_to(ROOT)}")


# ====================== 통합 운영 (OPERATION 패키지 반영) ======================
OPS_MODULES = {"lot": ("lot_traceability", "LOT"), "safety": ("safety_risk", "SAFETY"), "equipment": ("equipment_trial", "EQUIPMENT"),
               "training": ("training", "TRAINING"), "production": ("production", "PRODUCTION"), "inventory": ("inventory", "INVENTORY"),
               "quality": ("quality", "QUALITY")}
IN_DIR, OUT_DIR, MGMT_DIR = ROOT / "11_INPUT", ROOT / "12_OUTPUT", ROOT / "13_MANAGEMENT"
CUST_DIR, BACKUP_DIR = ROOT / "15_CUSTOMER_RESPONSE", ROOT / "16_BACKUP"
AUDIT_KINDS = {"internal": "INTERNAL", "customer": "CUSTOMER", "certification": "CERTIFICATION"}   # 14_AUDIT 하위 (OPERATION 패키지 구조)
AUDIT_DIR = ROOT / "14_AUDIT"

def sq_map_file(adir: Path) -> Path:
    """SQ 번호 배정대응표: 정정본(`_정정본*.csv`, 가장 최근)이 있으면 그것을, 없으면 원래 파일을 읽는다(원본은 유지)."""
    fixed = sorted(adir.glob("SQ_FM번호_배정대응표_정정본*.csv"), key=lambda f: f.stat().st_mtime)
    return fixed[-1] if fixed else adir / "SQ_FM번호_배정대응표.csv"

def latest_file(folder: Path, pattern: str):
    fs = sorted(folder.glob(pattern), key=lambda f: f.stat().st_mtime) if folder.exists() else []
    return fs[-1] if fs else None

def read_csv_rows(f: Path):
    return list(csv.DictReader(open(f, encoding="utf-8-sig", newline=""))) if f else []

def current_docs():
    """현재 유효한 문서(문서번호별 최신 Rev, 릴리스 > 승인 단계 > 원본 순)."""
    num = cfg("document_number_rules.yaml")
    cand, prio = {}, {"RELEASED": 3, "APPROVAL": 2, "ORIGINAL": 1}
    def add(p, stage):
        if p.suffix.lower() not in (TEXT_EXT | {".pdf"}):
            return
        m = re.search(num["doc_pattern"], p.name)
        rv = re.search(num["revision_pattern"], p.name)
        score = (int(rv.group(1)) if rv else -1, prio[stage], p.stat().st_mtime)
        key = m.group(0) if m else p.stem
        if key not in cand or score > cand[key][0]:
            cand[key] = (score, p, stage)
    for mf in RELEASED.rglob("MANIFEST.json") if RELEASED.exists() else []:
        m = json.loads(mf.read_text(encoding="utf-8"))
        for fe in m["files"]:
            if fe["role"] == "문서" and (mf.parent / fe["name"]).exists():
                add(mf.parent / fe["name"], "RELEASED")
    for sub in ("승인대기", "검토완료", "승인완료"):
        for f in (D["appr"] / sub).glob("*"):
            if f.is_file() and f.name != ".gitkeep" and not is_finalized(f):
                add(f, "APPROVAL")
    for d in D["orig"].iterdir():
        if d.is_dir() and d.name != MASTER:
            for f in d.rglob("*"):
                if f.is_file() and f.name != ".gitkeep":
                    add(f, "ORIGINAL")
    return [(p, st) for _, p, st in cand.values()]

def ops_qms_audit():
    """QMS 자동감사: 현재 유효 문서별 PASS/HOLD/FAIL → 02_REVIEW/qms_audit_*.csv/md (조치사항·대시보드의 입력)"""
    rows = []
    for p, stage in sorted(current_docs(), key=lambda x: x[0].name):
        typ = cfg("qms_rules.yaml")["classify"].get(prefix_of(p.name), "")
        docno, issues, approved, units = check(p, typ)
        hard = [m for c, m, _ in issues if c != "확인필요"]
        hold = [m for c, m, _ in issues if c == "확인필요"]
        st = "FAIL" if hard else ("HOLD" if hold or not approved else "PASS")
        note = " | ".join((hard + hold)[:6]) + ("" if approved else ("" if not (hard or hold) else " | ") + "승인 표기 없음(승인 전)" if not approved else "")
        rows.append([str(p.relative_to(ROOT)), docno or p.stem, (re.search(cfg("document_number_rules.yaml")["revision_pattern"], p.name) or [None, ""])[1], st, note, stage])
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = D["rev"] / f"qms_audit_{ts}.csv"
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["file", "document_no", "revision", "status", "issues", "stage"]); w.writerows(rows)
    cnt = collections.Counter(r[3] for r in rows)
    md = ["# QMS 자동감사 (현재 유효 문서)", f"- 생성: {now()}", f"- PASS {cnt['PASS']} / HOLD {cnt['HOLD']} / FAIL {cnt['FAIL']}", "", "## HOLD / FAIL"]
    md += [f"- [{r[3]}] {r[0]} :: {r[4]}" for r in rows if r[3] != "PASS"] or ["- 없음"]
    (D["rev"] / f"qms_audit_{ts}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"[QMS AUDIT] PASS {cnt['PASS']} / HOLD {cnt['HOLD']} / FAIL {cnt['FAIL']} → {out.relative_to(ROOT)}")
    return out

def sheet_head_cells(p: Path, rows=10):
    """엑셀(.xls/.xlsx/.xlsm)의 앞 rows 행 셀 텍스트 목록(공백 제거·소문자). 읽을 수 없으면 빈 목록."""
    cells, ext = [], p.suffix.lower()
    try:
        if ext == ".xls":
            import xlrd
            wb = xlrd.open_workbook(str(p), on_demand=True)
            for sh in wb.sheets():
                for r in range(min(sh.nrows, rows)):
                    cells.extend(sh.row_values(r))
        elif ext in (".xlsx", ".xlsm"):
            import openpyxl
            wb = openpyxl.load_workbook(str(p), read_only=True, data_only=True)
            for ws in wb.worksheets:
                for row in ws.iter_rows(min_row=1, max_row=rows, values_only=True):
                    cells.extend(row)
    except Exception:
        return []
    return [re.sub(r"\s+", "", str(c).lower()) for c in cells if c not in (None, "")]

def module_check(key):
    """현장 모듈 입력 점검: 11_INPUT/<모듈>/ 파일의 필수 항목 존재 확인 → 12_OUTPUT/REPORTS/<모듈>_check_*.csv"""
    cfg_key, folder = OPS_MODULES[key]
    mod_cfg = cfg("integrated_rules.yaml")["integrated_modules"][cfg_key]
    required, aliases = mod_cfg["required_fields"], mod_cfg.get("field_aliases") or {}
    exemptions = mod_cfg.get("field_exemptions") or []     # 파일명에 name_contains 가 있으면 exempt 항목은 필수에서 제외
    src = IN_DIR / folder
    src.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "REPORTS").mkdir(parents=True, exist_ok=True)
    rows = []
    for p in sorted(src.rglob("*")):
        if not p.is_file() or p.name == ".gitkeep":
            continue
        text = extract_text(p)
        if not text:
            rows.append([str(p.relative_to(ROOT)), key, "HOLD", "본문을 읽을 수 없음(스캔/미지원 형식)"])
            continue
        compact = re.sub(r"\s+", "", text.lower())            # '품 명' 처럼 글자 사이에 공백이 있는 제목도 찾도록 공백을 없애 비교
        heads = sheet_head_cells(p) if aliases else []
        def ok_alias(x):                       # 열 제목이 동의어와 정확히 같을 때만('re:' 로 시작하면 정규식 전체 일치)
            for a in aliases.get(x, []):
                if a.startswith("re:"):
                    if any(re.fullmatch(a[3:], h) for h in heads):
                        return True
                elif re.sub(r"\s+", "", a.lower()) in heads:
                    return True
            return False
        fname = re.sub(r"\s+", "", p.name.lower())
        exempt = {x for e in exemptions if any(re.sub(r"\s+", "", k.lower()) in fname for k in e.get("name_contains", [])) for x in e.get("exempt", [])}
        miss = [x for x in required if x not in exempt and re.sub(r"\s+", "", x.lower()) not in compact and not ok_alias(x)]
        rows.append([str(p.relative_to(ROOT)), key, "PASS" if not miss else "HOLD", "; ".join(miss)])
    if not rows:
        rows.append([f"11_INPUT/{folder}", key, "NO_DATA", "입력 데이터 없음"])
    out = OUT_DIR / "REPORTS" / f"{key}_check_{dt.datetime.now():%Y%m%d_%H%M%S}.csv"
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["file", "module", "status", "missing_fields"]); w.writerows(rows)
    c = collections.Counter(r[2] for r in rows)
    print(f"[MODULE {key.upper():9}] " + " / ".join(f"{k} {v}" for k, v in c.items()) + f" → {out.relative_to(ROOT)}")
    return rows

def module_words(key, like=(), file_kw=""):
    """모듈 폴더의 엑셀 파일 윗부분(앞 10행)에 자주 나오는 열 제목 후보를 집계한다(읽기 전용). 필수 항목 동의어를 정할 때 쓴다.
    → 12_OUTPUT/REPORTS/<모듈>_words_*.md  ※ 이름(제목)만 집계하며, 동의어 추가는 사용자 확인 후에만 한다."""
    cfg_key, folder = OPS_MODULES[key]
    required = cfg("integrated_rules.yaml")["integrated_modules"][cfg_key]["required_fields"]
    src = IN_DIR / folder
    word_files, nfiles, per_file = collections.defaultdict(set), 0, {}
    for p in sorted(src.rglob("*")) if src.exists() else []:
        ext = p.suffix.lower()
        if ext not in (".xlsx", ".xlsm", ".xls") or not p.is_file():
            continue
        cells = []
        try:
            if ext == ".xls":
                import xlrd
                wb = xlrd.open_workbook(str(p), on_demand=True)
                for sh in wb.sheets():
                    for r in range(min(sh.nrows, 10)):
                        cells.extend(sh.row_values(r))
            else:
                import openpyxl
                wb = openpyxl.load_workbook(str(p), read_only=True, data_only=True)
                for ws in wb.worksheets:
                    for row in ws.iter_rows(min_row=1, max_row=10, values_only=True):
                        cells.extend(row)
        except Exception:
            continue
        nfiles += 1
        titles = []
        for c in cells:
            t = re.sub(r"\s+", " ", str(c)).strip() if c is not None else ""
            if 2 <= len(t) <= 14 and not re.fullmatch(r"[\d\.\-/: ]+", t):
                word_files[t].add(p.name)
            if t and len(t) <= 24 and not re.fullmatch(r"[\d\.\-/: ]+", t) and t not in titles:
                titles.append(t)
        if file_kw and file_kw.lower() in p.name.lower():
            per_file[p.name] = titles
    L = [f"# {key} 열 제목 후보 (앞 10행, 읽을 수 있는 엑셀 {nfiles}개)", f"- 생성: {now()}", "", "## 현재 필수 항목이 들어 있는 파일 수", ""]
    L += [f"- {r}: " + str(len(set().union(*[fs for w, fs in word_files.items() if r.lower() in w.lower()]))) + "개 파일" for r in required]
    L += ["", "## 자주 나오는 제목 (파일 수 순, 상위 80)", "", "| 제목 | 파일 수 |", "|---|---|"]
    L += [f"| {w} | {len(fs)} |" for w, fs in sorted(word_files.items(), key=lambda x: -len(x[1]))[:80]]
    if like:
        cand = {w: fs for w, fs in word_files.items() if len(w) <= 10 and any(k.lower() in w.lower() for k in like)}
        L += ["", f"## '{', '.join(like)}' 가 들어간 짧은 제목 (파일 수 순)", "", "| 제목 | 파일 수 |", "|---|---|"]
        L += [f"| {w} | {len(fs)} |" for w, fs in sorted(cand.items(), key=lambda x: -len(x[1]))[:60]] or ["| (없음) | 0 |"]
    if file_kw:
        L += ["", f"## 파일명에 '{file_kw}' 가 들어간 파일의 제목(앞 10행, 나온 순서, 최대 6개 파일)", ""]
        for name, titles in list(per_file.items())[:6]:
            L += [f"### {name}", "", "- " + " | ".join(titles[:80]), ""]
        if not per_file:
            L += ["- (해당하는 읽을 수 있는 엑셀 파일 없음)"]
    L += ["", "※ 파일 이름·제목만 집계했습니다. 필수 항목의 동의어(예: 품번↔품목)는 사용자가 확인한 뒤에만 설정에 추가합니다."]
    (OUT_DIR / "REPORTS").mkdir(parents=True, exist_ok=True)
    out = unique_path(OUT_DIR / "REPORTS" / f"{key}_words_{dt.datetime.now():%Y%m%d_%H%M%S}.md")
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[MODULE WORDS {key.upper()}] 엑셀 {nfiles}개 / 제목 후보 {len(word_files)}개 → {out.relative_to(ROOT)}")
    return out

def record_inventory(plan_csv=None):
    """모듈별 '기록 종류 있음/없음' 현황: 11_INPUT/<모듈>/ 파일명에 설정(record_types)의 키워드가 있는지로만 판단한다(내용은 판정하지 않음).
    → 12_OUTPUT/REPORTS/record_inventory_*.md / .csv"""
    types = cfg("integrated_rules.yaml").get("record_types") or {}
    plan_csv = plan_csv or latest_file(OUT_DIR / "REPORTS", "organize_plan_*.csv")        # '없음'인 기록 종류는 08_SQ심사·00_QMS문서 폴더(11_INPUT 에 넣지 않은 자료)에 있는지 참고로 표시
    sq_names = []
    if plan_csv and Path(plan_csv).exists():
        for r in csv.DictReader(open(plan_csv, encoding="utf-8-sig")):
            if r.get("분류") in ("08_SQ심사", "00_QMS문서"):
                sq_names.append(r["원본 경로"].replace("/", "\\").split("\\")[-1])
        sq_names = sorted(set(sq_names))
    rows, L = [], ["# 현장 모듈 기록 종류 있음/없음 현황 (파일명 기준)", f"- 생성: {now()}", "- **주의**: 파일 이름의 키워드로만 판단합니다. '있음'은 해당 이름의 파일이 있다는 뜻이며 내용·최신성은 확인하지 않았습니다. 키워드는 `00_CONFIG/integrated_rules.yaml` 의 `record_types` 에서 담당자가 수정합니다.", ""]
    for key, (cfg_key, folder) in OPS_MODULES.items():
        src = IN_DIR / folder
        names = sorted({p.name for p in src.rglob("*") if p.is_file() and p.name != ".gitkeep"}) if src.exists() else []
        L += [f"## {key} (파일 {len(names)}개)", ""]
        if not names:
            L += ["- NO_DATA: 입력 파일이 없음", ""]
        L += ["| 기록 종류 | 상태 | 파일 수 | 예시 |", "|---|---|---|---|"]
        for rtype, kws in (types.get(key) or {}).items():
            hits = [n for n in names if any(re.sub(r"\s+", "", k.lower()) in re.sub(r"\s+", "", n.lower()) for k in kws)]
            st = "있음" if hits else ("없음" if names else "NO_DATA")
            note = ""
            if st != "있음" and sq_names:
                sq_hits = [n for n in sq_names if any(re.sub(r"\s+", "", k.lower()) in re.sub(r"\s+", "", n.lower()) for k in kws)]
                if sq_hits:
                    note = f"(참고: SQ·QMS 폴더에 {len(sq_hits)}개 — {'; '.join(sq_hits[:2])})"
            rows.append([key, rtype, st, len(hits), "; ".join(hits[:3]), note])
            L.append(f"| {rtype} | {st} | {len(hits)} | {'; '.join(hits[:2]) or note} |")
        L.append("")
    (OUT_DIR / "REPORTS").mkdir(parents=True, exist_ok=True)
    stamp = f"{dt.datetime.now():%Y%m%d_%H%M%S}"
    mdp = unique_path(OUT_DIR / "REPORTS" / f"record_inventory_{stamp}.md")
    mdp.write_text("\n".join(L) + "\n", encoding="utf-8")
    cp = unique_path(OUT_DIR / "REPORTS" / f"record_inventory_{stamp}.csv")
    with open(cp, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh); w.writerow(["module", "record_type", "status", "files", "examples", "sq_folder_note"]); w.writerows(rows)
    c = collections.Counter(r[2] for r in rows)
    print("[RECORD INVENTORY] " + " / ".join(f"{k} {v}" for k, v in c.items()) + f" → {mdp.relative_to(ROOT)}")
    return rows

def integrated_audit():
    """QMS + 현장 모듈 7종 통합 점검 → 12_OUTPUT/REPORTS/integrated_audit_*.csv/md"""
    ops_qms_audit()
    summary = []
    q_rows = read_csv_rows(latest_file(D["rev"], "qms_audit_*.csv"))
    qc = collections.Counter(r["status"] for r in q_rows)
    summary.append(["QMS", dict(qc)])
    for key in OPS_MODULES:
        rows = module_check(key)
        summary.append([key.upper(), dict(collections.Counter(r[2] for r in rows))])
    out = OUT_DIR / "REPORTS" / f"integrated_audit_{dt.datetime.now():%Y%m%d_%H%M%S}.csv"
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["area", "result"]); w.writerows([[a, json.dumps(r, ensure_ascii=False)] for a, r in summary])
    md = ["# 통합 점검 요약", f"- 생성: {now()}", "", "| 영역 | 결과 |", "|---|---|"] + [f"| {a} | {r} |" for a, r in summary]
    md += ["", "※ NO_DATA = 입력 데이터 없음(점검하지 않음). PASS 가 아닙니다."]
    out.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"[INTEGRATED] → {out.relative_to(ROOT)}")
    return out

def collect_actions():
    """HOLD/FAIL 조치사항 취합 → 12_OUTPUT/ACTION_ITEMS/action_items_*.csv (이전 담당자·기한·상태는 이어받음)"""
    (OUT_DIR / "ACTION_ITEMS").mkdir(parents=True, exist_ok=True)
    prev = {}
    pf = latest_file(OUT_DIR / "ACTION_ITEMS", "action_items_*.csv")
    for r in read_csv_rows(pf):
        prev[(r["target"], r["issue"])] = (r["owner"], r["due_date"], r["action_status"])
    items = []
    qf = latest_file(D["rev"], "qms_audit_*.csv")
    for r in read_csv_rows(qf):
        if r["status"] in ("HOLD", "FAIL"):
            items.append([qf.name, r["document_no"] or r["file"], r["status"], r["issues"]])
    for key in OPS_MODULES:
        mf = latest_file(OUT_DIR / "REPORTS", f"{key}_check_*.csv")
        for r in read_csv_rows(mf):
            if r["status"] in ("HOLD", "FAIL"):
                items.append([mf.name, r["file"], r["status"], r["missing_fields"]])
    # SQ 심사: 담당자 확인 대기 항목
    dec = latest_file(ROOT / "07_AUDIT" / "고객심사", "SQ_중복검토_결정*.csv")
    for r in read_csv_rows(dec):
        if r["결정"].startswith("보류"):
            items.append([dec.name, f"{r['정식 SH-FM 번호']} {r['양식명']}", "HOLD", f"중복/문서 여부 담당자 확인: {r['근거']}"])
    for wbk in sorted((D["edit"] / "AUTO_DRAFT").glob("SQ_*_초안/*.xlsx")):
        items.append(["SQ 양식 초안", wbk.name, "HOLD", "초안 — 항목·기준·결재방식·보존기간 담당부서 확정 필요"])
    out = unique_path(OUT_DIR / "ACTION_ITEMS" / f"action_items_{dt.datetime.now():%Y%m%d_%H%M%S}.csv")
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["source", "target", "status", "issue", "owner", "due_date", "action_status"])
        for src, tgt, st, iss in items:
            o, d_, a = prev.get((tgt, iss), ("", "", "OPEN"))
            w.writerow([src, tgt, st, iss, o, d_, a])
    print(f"[ACTIONS] 조치 {len(items)}건 (FAIL {sum(1 for i in items if i[2]=='FAIL')} / HOLD {sum(1 for i in items if i[2]=='HOLD')}) → {out.relative_to(ROOT)}")
    return out, items

def dashboard_data():
    """대시보드용 JSON → 12_OUTPUT/DASHBOARD_DATA/dashboard_*.json"""
    (OUT_DIR / "DASHBOARD_DATA").mkdir(parents=True, exist_ok=True)
    areas = {}
    qf = latest_file(D["rev"], "qms_audit_*.csv")
    if qf:
        areas["qms"] = dict(collections.Counter(r["status"] for r in read_csv_rows(qf)))
    for key in OPS_MODULES:
        mf = latest_file(OUT_DIR / "REPORTS", f"{key}_check_*.csv")
        if mf:
            areas[key] = dict(collections.Counter(r["status"] for r in read_csv_rows(mf)))
    af = latest_file(OUT_DIR / "ACTION_ITEMS", "action_items_*.csv")
    acts = read_csv_rows(af)
    sq = {}
    mp = sq_map_file(ROOT / "07_AUDIT" / "고객심사")
    if mp.exists():
        sq = {"required_docs": len(read_csv_rows(mp)), "number_assigned": len(read_csv_rows(mp)),
              "drafts_created": sum(1 for _ in (D["edit"] / "AUTO_DRAFT").glob("SQ_*_초안/*.xlsx")), "approved_forms": 0}
    summary = {"generated_at": dt.datetime.now().isoformat(timespec="seconds"), "areas": areas,
               "action_items": {"total": len(acts), "open": sum(1 for r in acts if r["action_status"] == "OPEN")},
               "released_documents": len(list(RELEASED.rglob("MANIFEST.json"))) if RELEASED.exists() else 0, "sq": sq}
    out = unique_path(OUT_DIR / "DASHBOARD_DATA" / f"dashboard_{dt.datetime.now():%Y%m%d_%H%M%S}.json")
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[DASHBOARD] → {out.relative_to(ROOT)}")
    return out

def weekly_report():
    """주간 통합 운영 보고 → 13_MANAGEMENT/WEEKLY/weekly_management_*.md"""
    (MGMT_DIR / "WEEKLY").mkdir(parents=True, exist_ok=True)
    rules = cfg("integrated_rules.yaml")["management_reports"]["weekly"]["sections"]
    af = latest_file(OUT_DIR / "ACTION_ITEMS", "action_items_*.csv")
    acts = read_csv_rows(af)
    qf = latest_file(D["rev"], "qms_audit_*.csv")
    qc = collections.Counter(r["status"] for r in read_csv_rows(qf))
    gate = latest_file(D["rev"], "qms_release_gate*.md")
    gtxt = re.search(r"## 결과:\s*(\w+)", gate.read_text(encoding="utf-8")) if gate else None
    def mod(key):
        mf = latest_file(OUT_DIR / "REPORTS", f"{key}_check_*.csv")
        c = collections.Counter(r["status"] for r in read_csv_rows(mf))
        return dict(c) if c else "점검 결과 없음"
    secmap = {"QMS 변경/오류": f"문서 PASS {qc['PASS']} / HOLD {qc['HOLD']} / FAIL {qc['FAIL']}, Release Gate: {gtxt.group(1) if gtxt else '미실행'}",
              "LOT 추적성": mod("lot"), "안전/위험성평가": mod("safety"), "설비": mod("equipment"), "교육": mod("training"),
              "생산": mod("production"), "재고": mod("inventory"), "품질": mod("quality"),
              "미결 조치사항": f"{len(acts)}건 (OPEN {sum(1 for r in acts if r['action_status']=='OPEN')})"}
    L = ["# 주간 통합 운영 보고", "", f"- 작성일: {dt.date.today()}", ""]
    for sct in rules:
        L += [f"## {sct}", f"{secmap.get(sct, '데이터 없음')}", ""]
    L += ["## 우선 확인 (HOLD/FAIL 상위 30)"] + [f"- [{r['status']}] {r['target']} :: {r['issue'][:100]}" for r in acts[:30]]
    out = unique_path(MGMT_DIR / "WEEKLY" / f"weekly_management_{dt.date.today():%Y%m%d}.md")
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[WEEKLY] → {out.relative_to(ROOT)}")
    return out

def monthly_report():
    """월간 품질·생산 관리 보고 → 13_MANAGEMENT/MONTHLY/. 입력 데이터(11_INPUT/QUALITY)가 있으면 고객사별 집계, 없으면 '데이터 입력 필요'."""
    (MGMT_DIR / "MONTHLY").mkdir(parents=True, exist_ok=True)
    rules = cfg("integrated_rules.yaml")["management_reports"]["monthly"]["sections"]
    rows = []
    for p in (IN_DIR / "QUALITY").rglob("*") if (IN_DIR / "QUALITY").exists() else []:
        if p.suffix.lower() == ".csv":
            rows += list(csv.DictReader(open(p, encoding="utf-8-sig", newline="")))
        elif p.suffix.lower() == ".xlsx":
            from openpyxl import load_workbook
            for wsx in load_workbook(p, data_only=True).worksheets:
                data = [[c for c in r] for r in wsx.iter_rows(values_only=True) if any(c is not None for c in r)]
                hi = next((i for i, r in enumerate(data) if "고객사" in [str(c) for c in r] and "PPM" in [str(c) for c in r]), None)
                if hi is not None:
                    hdr = [str(c) for c in data[hi]]
                    rows += [dict(zip(hdr, r)) for r in data[hi + 1:]]
    def num(v):
        try:
            return float(str(v).replace(",", ""))
        except Exception:
            return None
    by = collections.defaultdict(list)
    for r in rows:
        if r.get("고객사") and num(r.get("PPM")) is not None:
            by[r["고객사"]].append(num(r["PPM"]))
    sec = {s: "데이터 입력 필요" for s in rules}
    if by:
        sec["고객사별 PPM"] = "\n".join(f"- {c}: 평균 PPM {sum(v)/len(v):.1f} (n={len(v)})" for c, v in sorted(by.items()))
    L = ["# 월간 품질·생산 관리 보고", "", f"- 작성월: {dt.date.today():%Y-%m}", f"- 입력 데이터: {'11_INPUT/QUALITY ('+str(len(rows))+'행)' if rows else '없음'}", ""]
    for i, sct in enumerate(rules, 1):
        L += [f"## {i}. {sct}", sec[sct], ""]
    L += ["※ 목표 PPM·전월 값 등 확정되지 않은 수치는 임의로 채우지 않습니다."]
    out = unique_path(MGMT_DIR / "MONTHLY" / f"monthly_quality_management_{dt.date.today():%Y%m}.md")
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[MONTHLY] → {out.relative_to(ROOT)}")
    return out

def audit_package(kind):
    """심사 패키지(내부/고객/인증) → 14_AUDIT/<INTERNAL|CUSTOMER|CERTIFICATION>/AUDIT_PACKAGE_*/"""
    folder = AUDIT_KINDS[kind]
    pkg = AUDIT_DIR / folder / f"AUDIT_PACKAGE_{dt.datetime.now():%Y%m%d_%H%M%S}"
    pkg.mkdir(parents=True)
    srcs = [("QMS_REVIEW", D["rev"], ["qms_audit_*", "qms_release_gate*", "qms_ledger_check*", "qms_crosscheck_summary*"]),
            ("MODULE_REPORTS", OUT_DIR / "REPORTS", ["*_check_*", "integrated_audit_*"]),
            ("ACTION_ITEMS", OUT_DIR / "ACTION_ITEMS", ["action_items_*"]),
            ("MANAGEMENT", MGMT_DIR, ["WEEKLY/*", "MONTHLY/*"]),
            ("RELEASE", D["final"] / "RELEASED", ["배포목록.csv", "최종보고서*", "무결성검사*"])]
    if kind in ("customer", "certification"):
        srcs.append(("SQ", ROOT / "07_AUDIT" / "고객심사", ["SQ_필요서류_대조보고서*", "SQ_FM번호_배정대응표*.csv", "SQ_중복검토_*"]))
    n = 0
    for name, base, pats in srcs:
        (pkg / name).mkdir()
        for pat in pats:
            fs = sorted(base.glob(pat), key=lambda f: f.stat().st_mtime) if base.exists() else []
            for f in [x for x in fs if x.is_file()][-3:]:   # 패턴별 최신 3개
                shutil.copy2(f, pkg / name / f.name); n += 1
    (pkg / "AUDIT_README.md").write_text(f"# {folder} 패키지\n\n- 생성: {now()}\n- 포함 파일 {n}개\n\n포함: QMS 최신 검토·Release Gate·문서관리대장 대조, 현장 모듈 점검, 미결 조치사항, 주간/월간 보고, 릴리스 이력"
                                        f"{'(SQ 필요서류 대조 포함)' if kind != 'internal' else ''}.\n\n**제출 전 확인**: HOLD/FAIL 항목이 있으면 제출하지 않고, 최신성·승인 상태를 확인합니다. 자동 생성 자료이며 실제 승인 책임은 승인권자에게 있습니다.\n", encoding="utf-8")
    log("workflow_log.csv", [now(), pkg.name, "", "심사 패키지", str(pkg.relative_to(ROOT)), "system", f"{folder} 패키지 생성({n}개 파일)"])
    print(f"[AUDIT PKG] {folder}: {n}개 파일 → {pkg.relative_to(ROOT)}")
    return pkg

def customer_response():
    """고객사(한온시스템) 품질 대응자료 템플릿 → 15_CUSTOMER_RESPONSE/HANON_RESPONSE_*/ (내용은 임의 생성하지 않음)"""
    pkg = CUST_DIR / f"HANON_RESPONSE_{dt.datetime.now():%Y%m%d_%H%M%S}"
    pkg.mkdir(parents=True)
    lot = latest_file(OUT_DIR / "REPORTS", "lot_check_*.csv")
    (pkg / "CUSTOMER_RESPONSE_TEMPLATE.md").write_text("\n".join([
        f"# 고객사 품질 대응자료 — {cfg('qms_rules.yaml').get('main_customer', '한온시스템')}", "", f"- 작성일: {dt.date.today()}",
        f"- LOT 추적성 기준: 보존 {cfg('qms_rules.yaml')['lot_traceability_retention']}, 추적 목표시간 {cfg('qms_rules.yaml')['lot_trace_target_time']}",
        f"- 최근 LOT 점검 결과 파일: {lot.name if lot else '없음'}", ""] +
        [f"## {i}. {t}\n입력 필요\n" for i, t in enumerate(["문제현상", "대상 품번 / LOT", "LOT 추적 결과", "원인분석", "임시조치", "영구대책", "재발방지"], 1)] +
        ["## 8. 증빙자료\n첨부 필요\n", "## 9. 담당자 / 완료일\n입력 필요\n"]), encoding="utf-8")
    log("workflow_log.csv", [now(), pkg.name, "", "고객 대응", str(pkg.relative_to(ROOT)), "system", "고객 대응자료 템플릿 생성"])
    print(f"[CUSTOMER] → {pkg.relative_to(ROOT)}")
    return pkg

def backup_workspace():
    """작업공간 전체 백업(zip) → 16_BACKUP/ (백업 폴더 자신은 제외)"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    out = unique_path(BACKUP_DIR / f"SHINHWA_BACKUP_{dt.datetime.now():%Y%m%d_%H%M%S}.zip")
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(ROOT.rglob("*")):
            if f.is_file() and BACKUP_DIR not in f.parents and "__pycache__" not in f.parts:
                z.write(f, f.relative_to(ROOT)); n += 1
    log("workflow_log.csv", [now(), out.name, "", "백업", str(out.relative_to(ROOT)), "system", f"{n}개 파일 백업"])
    print(f"[BACKUP ] {n}개 파일 → {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)")
    return out

SECRET_RX = [re.compile(r"(?i)(api[_-]?key|secret|token|passwd|password)[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9_\-\.]{12,}"),
             re.compile(r"\bsk-[A-Za-z0-9]{20,}"), re.compile(r"\bghp_[A-Za-z0-9]{30,}"), re.compile(r"Bearer\s+[A-Za-z0-9\-\._]{20,}"), re.compile(r"\bAKIA[0-9A-Z]{16}")]

def mcp_health_check():
    """MCP 상태·보안 점검(읽기 전용). claude mcp list, .mcp.json 비밀값, .gitignore, 저장소 내 비밀값 패턴.
    MCP 가 없거나 장애여도 로컬 QMS 자동화는 계속 사용 가능 → 보고서만 남기고 중단하지 않는다."""
    rows, repo = [], ROOT.parent
    add = lambda area, st, note: rows.append((area, st, note))
    if shutil.which("claude"):
        r = subprocess.run(["claude", "mcp", "list"], capture_output=True, text=True, timeout=60)
        out = (r.stdout or r.stderr).strip()
        if "No MCP servers configured" in out:
            add("claude mcp list", "INFO", "설정된 MCP 서버 없음 — 로컬 QMS 자동화는 정상 사용 가능")
        else:
            lines = [l for l in out.splitlines() if l.strip()]
            bad = [l for l in lines if re.search(r"(?i)fail|error|disconnect|needs auth|✗", l)]
            add("claude mcp list", "WARN" if bad else "PASS", f"서버 {len(lines)}개" + (f", 이상: {'; '.join(bad[:3])}" if bad else ", 모두 정상 표시"))
    else:
        add("claude mcp list", "INFO", "claude CLI 를 찾을 수 없음(이 환경에서는 확인 불가)")
    mcpjs = [f for f in (repo / ".mcp.json", ROOT / ".mcp.json") if f.exists()]
    if not mcpjs:
        add(".mcp.json", "INFO", "프로젝트 .mcp.json 없음")
    for f in mcpjs:
        txt = f.read_text(encoding="utf-8", errors="ignore")
        hit = [rx.pattern[:20] for rx in SECRET_RX if rx.search(txt)]
        add(str(f.relative_to(repo)), "FAIL" if hit else "PASS", "비밀값(키/토큰) 직접 기재 의심 — 환경변수·OAuth 로 교체" if hit else "비밀값 직접 기재 없음")
    gi = (repo / ".gitignore").read_text(encoding="utf-8") if (repo / ".gitignore").exists() else ""
    need = [".env", "credentials", "token"]
    miss = [n for n in need if n not in gi]
    add(".gitignore", "WARN" if miss else "PASS", f"누락 패턴: {', '.join(miss)}" if miss else ".env/credentials/token 패턴 제외됨")
    tracked = subprocess.run(["git", "ls-files"], cwd=repo, capture_output=True, text=True).stdout.splitlines()
    risky = [t for t in tracked if re.search(r"(^|/)(\.env(\..*)?|.*credentials.*\.json|.*token.*\.json|client_secret.*\.json)$", t, re.I)]
    add("추적 중인 민감 파일", "FAIL" if risky else "PASS", ", ".join(risky[:5]) if risky else "없음")
    hits = []
    for t in tracked:
        if t.lower().endswith((".md", ".py", ".yaml", ".yml", ".json", ".txt", ".csv", ".sh")) and "06_HISTORY/업로드패키지" not in t:
            try:
                for i, line in enumerate((repo / t).read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                    if any(rx.search(line) for rx in SECRET_RX):
                        hits.append(f"{t}:{i}")
            except Exception:
                pass
    add("저장소 내 비밀값 패턴", "WARN" if hits else "PASS", (f"{len(hits)}곳 확인 필요: " + ", ".join(hits[:5])) if hits else "발견 없음")
    try:
        subprocess.run([sys.executable, str(Path(__file__)), "scan"], capture_output=True, text=True, timeout=120, check=True)
        add("로컬 QMS 자동화", "PASS", "MCP 와 독립적으로 동작(scan 실행 확인)")
    except Exception as e:
        add("로컬 QMS 자동화", "FAIL", f"scan 실행 실패: {e}")
    add("권한 단계", "INFO", "초기 운영은 LEVEL 1(READ) 권장. 메일 발송·외부 공유·삭제·승인/배포(LEVEL 4)는 사용자의 명시적 승인 없이 실행하지 않음 (17_MCP/MCP_SECURITY_POLICY.md)")
    worst = "FAIL" if any(r[1] == "FAIL" for r in rows) else "WARN" if any(r[1] == "WARN" for r in rows) else "PASS"
    L = ["# MCP 상태·보안 점검 (읽기 전용)", f"- 생성: {now()}", f"- 종합: {worst}", "", "| 영역 | 결과 | 비고 |", "|---|---|---|"] + [f"| {a} | {b} | {c} |" for a, b, c in rows]
    (OUT_DIR / "REPORTS").mkdir(parents=True, exist_ok=True)
    out = unique_path(OUT_DIR / "REPORTS" / f"mcp_health_{dt.datetime.now():%Y%m%d_%H%M%S}.md")
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[MCP HEALTH] {worst} " + " / ".join(f"{a}:{b}" for a, b, _ in rows[:7]) + f" → {out.relative_to(ROOT)}")
    return worst

def mcp_safe_start():
    """MCP 점검 후 전체 운영 시작. MCP 문제와 무관하게 로컬 QMS 운영은 계속하되, FAIL 이면 MCP 사용을 중단하라고 안내한다."""
    worst = mcp_health_check()
    if worst == "FAIL":
        print("[MCP SAFE START] FAIL 항목이 있어 외부 연동(MCP) 사용은 보류합니다. 로컬 QMS 운영은 계속합니다.")
    full_operation()

def opt_list(flag):
    """명령행 옵션 '--only 폴더A,폴더B' / '--exclude 폴더C' 값을 목록으로 읽는다(최상위 폴더 이름, 대소문자 무시)."""
    if flag in sys.argv:
        i = sys.argv.index(flag)
        if i + 1 < len(sys.argv):
            return [x.strip().lower() for x in sys.argv[i + 1].split(",") if x.strip()]
    return []

def prune_scope(base, dp, dns, fns, only, exclude):
    """최상위 폴더 범위 제한: only 가 있으면 그 폴더만, exclude 는 제외. only 가 있으면 루트 직하 파일도 제외한다."""
    if Path(dp) == base:
        dns[:] = [d for d in dns if (not only or d.lower() in only) and d.lower() not in exclude]
        if only:
            fns[:] = []

def classify_module(rel_parts, fn, kw):
    """모듈 분류: ① 가까운 상위 폴더부터 올라가며 '한 모듈'만 맞는 폴더 이름 ② 파일명 ③ 상위 폴더 전체. 반환 (모듈|None, 사유)"""
    mods_of = lambda text: [k for k, ws in kw.items() if any(w.lower() in text.lower() for w in ws)]
    for d in reversed(rel_parts):
        m = mods_of(d)
        if len(m) == 1:
            return m[0], f"폴더({d})"
    m = mods_of(fn)
    if len(m) == 1:
        return m[0], "파일명"
    if len(m) > 1:
        return None, "여러 모듈(파일명): " + "/".join(m)
    allm = mods_of(" ".join(rel_parts))
    if len(allm) == 1:
        return allm[0], "상위 폴더 전체"
    return None, ("여러 모듈(폴더): " + "/".join(allm)) if allm else "키워드 없음"

def drive_scan(src, only=(), exclude=()):
    """분류 키워드 조정용 현황 조사(읽기 전용): 확장자별·최상위 폴더별 파일 수, 자주 나오는 이름 토큰, 현재 규칙의 분류 결과·미분류 토큰.
    파일 내용은 읽지 않으며 이름만 집계한다. → 12_OUTPUT/REPORTS/drivescan_*.md"""
    base = Path(src).expanduser()
    if not base.exists():
        sys.exit(f"폴더를 찾을 수 없음: {src}")
    kw = cfg("integrated_rules.yaml")["input_sync"]["keywords"]
    skip = {"$recycle.bin", "system volume information", "windows", "program files", "program files (x86)", ".git", "node_modules", "__pycache__", "appdata"}
    ext_c, top_c, res_c, tok_all, tok_un, total = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter(), 0
    sample_un = []
    print(f"[DRIVE SCAN] 조사 시작: {base}  (파일이 많으면 몇 분 걸립니다. 중단하려면 Ctrl+C)", flush=True)
    for dp, dns, fns in os.walk(base):
        dns[:] = [d for d in dns if d.lower() not in skip and not d.startswith("$") and (Path(dp) / d).resolve() != ROOT.resolve()]
        prune_scope(base, dp, dns, fns, only, exclude)
        for fn in fns:
            if fn.startswith("~$") or fn.lower() in ("thumbs.db", "desktop.ini"):
                continue
            f = Path(dp) / fn
            rel = f.relative_to(base).parts
            total += 1
            if total % 2000 == 0:
                print(f"  ... {total:,}개 확인함", flush=True)
            ext_c[f.suffix.lower() or "(없음)"] += 1
            top_c[rel[0] if len(rel) > 1 else "(루트 직하)"] += 1
            mod, why = classify_module(rel[:-1], fn, kw)
            res_c[mod or "미분류"] += 1
            toks = set(re.findall(r"[가-힣A-Za-z]{2,}", Path(fn).stem)) | {t for d in rel[:-1] for t in re.findall(r"[가-힣A-Za-z]{2,}", d)}
            for t in toks:
                tok_all[t] += 1
                if not mod:
                    tok_un[t] += 1
            if not mod and len(sample_un) < 25:
                sample_un.append(f"{f.relative_to(base)}  ({why})")
    L = ["# 드라이브 현황 조사(분류 키워드 조정용)", f"- 생성: {now()}", f"- 대상: {base} (이름만 집계, 내용은 읽지 않음)" + (f" / 포함 폴더: {', '.join(only)}" if only else "") + (f" / 제외 폴더: {', '.join(exclude)}" if exclude else ""), f"- 파일 {total}개", "",
         "## 현재 키워드 규칙의 분류 결과", "", "| 분류 | 파일 수 |", "|---|---|"] + [f"| {k} | {v} |" for k, v in sorted(res_c.items())]
    L += ["", "## 확장자별", ""] + [f"- {k}: {v}" for k, v in ext_c.most_common(12)]
    L += ["", "## 최상위 폴더별 파일 수 (상위 25)", ""] + [f"- {k}: {v}" for k, v in top_c.most_common(25)]
    L += ["", "## 미분류 파일에 자주 나온 이름 토큰 (키워드 후보, 상위 40)", ""] + [f"- {k} ({v})" for k, v in tok_un.most_common(40)]
    L += ["", "## 전체에서 자주 나온 토큰 (상위 40)", ""] + [f"- {k} ({v})" for k, v in tok_all.most_common(40)]
    L += ["", "## 미분류 예시 (최대 25)", ""] + [f"- {x}" for x in sample_un]
    L += ["", "※ 위 '키워드 후보'를 보고 `00_CONFIG/integrated_rules.yaml` 의 `input_sync.keywords` 에 어느 모듈인지 정해 추가합니다(모듈을 임의로 추정해 넣지 않음)."]
    (OUT_DIR / "REPORTS").mkdir(parents=True, exist_ok=True)
    out = unique_path(OUT_DIR / "REPORTS" / f"drivescan_{dt.datetime.now():%Y%m%d_%H%M%S}.md")
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[DRIVE SCAN] 파일 {total}개 / 분류 " + ", ".join(f"{k} {v}" for k, v in sorted(res_c.items())) + f" → {out.relative_to(ROOT)}")
    return out

def dup_scan(src, folders=()):
    """최상위 폴더 간 중복 조사(읽기 전용): 파일 이름+크기가 같으면 같은 파일 후보로 본다(내용은 읽지 않음).
    각 폴더의 파일 수, 다른 폴더에도 있는 파일 수, 고유 파일 수를 보고한다. → 12_OUTPUT/REPORTS/dupscan_*.md"""
    base = Path(src).expanduser()
    if not base.exists():
        sys.exit(f"폴더를 찾을 수 없음: {src}")
    want = [x.lower() for x in folders]
    skip = {"$recycle.bin", "system volume information", "windows", "program files", "program files (x86)", ".git", "node_modules", "__pycache__", "appdata"}
    seen, total = collections.defaultdict(set), 0       # (이름,크기) → 최상위 폴더 집합
    per_top = collections.defaultdict(list)
    print(f"[DUP SCAN] 조사 시작: {base}  (이름·크기만 비교, 내용은 읽지 않음. 중단: Ctrl+C)", flush=True)
    for dp, dns, fns in os.walk(base):
        dns[:] = [d for d in dns if d.lower() not in skip and not d.startswith("$") and (Path(dp) / d).resolve() != ROOT.resolve()]
        if Path(dp) == base:
            dns[:] = [d for d in dns if not want or d.lower() in want]
            fns[:] = []
        for fn in fns:
            if fn.startswith("~$") or fn.lower() in ("thumbs.db", "desktop.ini"):
                continue
            f = Path(dp) / fn
            try:
                size = f.stat().st_size
            except OSError:
                continue
            top = f.relative_to(base).parts[0]
            key = (fn.lower(), size)
            seen[key].add(top); per_top[top].append(key)
            total += 1
            if total % 5000 == 0:
                print(f"  ... {total:,}개 확인함", flush=True)
    L = ["# 폴더 간 중복 조사 (이름+크기 기준, 읽기 전용)", f"- 생성: {now()}", f"- 대상: {base}", f"- 파일 {total}개", "",
         "| 최상위 폴더 | 파일 수 | 다른 폴더에도 있음 | 이 폴더에만 있음 |", "|---|---|---|---|"]
    for top, keys in sorted(per_top.items(), key=lambda x: -len(x[1])):
        shared = sum(1 for k in keys if len(seen[k]) > 1)
        L.append(f"| {top} | {len(keys)} | {shared} | {len(keys) - shared} |")
    tops = sorted(per_top)
    L += ["", "## 폴더 쌍별 겹치는 파일 수(이름+크기 같음)", "", "| 폴더 A | 폴더 B | 겹침 |", "|---|---|---|"]
    pair = collections.Counter()
    for k, ts in seen.items():
        ts = sorted(ts)
        for i in range(len(ts)):
            for j in range(i + 1, len(ts)):
                pair[(ts[i], ts[j])] += 1
    L += [f"| {a} | {b} | {n} |" for (a, b), n in pair.most_common(30)]
    L += ["", "※ 이름과 크기만 같은 후보입니다. 같은 파일 여부는 사람이 확인하세요. 아무것도 이동·삭제하지 않았습니다."]
    (OUT_DIR / "REPORTS").mkdir(parents=True, exist_ok=True)
    out = unique_path(OUT_DIR / "REPORTS" / f"dupscan_{dt.datetime.now():%Y%m%d_%H%M%S}.md")
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[DUP SCAN] 파일 {total}개 / 폴더 {len(per_top)}개 → {out.relative_to(ROOT)}")
    return out

def input_sync(src, apply=False, only=(), exclude=(), match=(), force_mod=None):
    """로컬 폴더(예: E:\\)의 현장 파일을 모듈별로 11_INPUT 에 '복사'한다. 원본 폴더는 읽기만 한다(수정·삭제·이동 없음).
    기본은 미리보기(dry-run)이며 --apply 일 때만 복사한다. 같은 내용은 건너뛰고, 같은 이름·다른 내용은 _vN 으로 새로 저장한다.
    두 모듈 이상에 걸리거나 분류할 수 없는 파일은 복사하지 않고 목록으로 보고한다."""
    base = Path(src).expanduser()
    if not base.exists():
        sys.exit(f"원본 폴더를 찾을 수 없음: {src}")
    rules = cfg("integrated_rules.yaml")["input_sync"]
    exts, limit = {e.lower() for e in rules["extensions"]}, rules["max_file_mb"] * 1024 * 1024
    skip = {"$recycle.bin", "system volume information", "windows", "program files", "program files (x86)", ".git", "node_modules", "__pycache__", "appdata"}
    plan, ambiguous, unmatched, too_big = [], [], 0, []
    for dp, dns, fns in os.walk(base):
        dns[:] = [d for d in dns if d.lower() not in skip and not d.startswith("$") and (Path(dp) / d).resolve() != ROOT.resolve()]
        prune_scope(base, dp, dns, fns, only, exclude)
        for fn in fns:
            f = Path(dp) / fn
            if f.suffix.lower() not in exts or fn.startswith("~$"):
                continue
            if match and not any(m in re.sub(r"\s+", "", (fn + " " + str(f.parent.relative_to(base))).lower()) for m in match):
                continue                                   # --match: 파일명·폴더명에 키워드가 있는 파일만
            try:
                size = f.stat().st_size
            except OSError:
                continue
            if size > limit:
                too_big.append(str(f)); continue
            rel = f.relative_to(base).parts
            mod, why = (force_mod, "지정") if force_mod else classify_module(rel[:-1], fn, rules["keywords"])
            if mod:
                plan.append((mod, f))
            elif why.startswith("여러"):
                ambiguous.append((f, [why.split(": ", 1)[1]]))
            else:
                unmatched += 1
    L = ["# 로컬 폴더 → 11_INPUT 복사 " + ("(실행)" if apply else "(미리보기, 복사 안 함)"), f"- 생성: {now()}", f"- 원본: {base} (읽기만 함)", ""]
    copied = same = 0
    L += ["## 모듈별 복사 대상", "", "| 모듈 | 파일 | 처리 |", "|---|---|---|"]
    for mod, f in sorted(plan, key=lambda x: (x[0], str(x[1]))):
        dest_dir = IN_DIR / OPS_MODULES[mod][1]
        ex = find_identical(f, dest_dir)
        if ex is not None:
            act = "이미 있음(동일)" + ("" if ex.name == f.name else f" → {ex.name}"); same += 1
        elif apply:
            dst = safe_copy(f, dest_dir)
            act = f"복사 → {dst.relative_to(ROOT)}"; copied += 1
        else:
            act = "복사 예정"
        L.append(f"| {mod} | {f} | {act} |")
    L += ["", f"## 여러 모듈에 걸려 복사하지 않은 파일 ({len(ambiguous)})"] + [f"- {f} ← {', '.join(m)}" for f, m in ambiguous[:50]]
    L += ["", f"## 크기 제한({rules['max_file_mb']}MB) 초과로 건너뜀 ({len(too_big)})"] + [f"- {x}" for x in too_big[:20]]
    L += ["", f"- 키워드가 맞지 않아 분류하지 않은 파일: {unmatched}개"]
    (OUT_DIR / "REPORTS").mkdir(parents=True, exist_ok=True)
    out = unique_path(OUT_DIR / "REPORTS" / f"inputsync_{dt.datetime.now():%Y%m%d_%H%M%S}.md")
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    if apply:
        log("workflow_log.csv", [now(), str(base), "", "inputsync", "11_INPUT", "system", f"{copied}개 복사, {same}개 동일(건너뜀)"])
    print(f"[INPUT SYNC] {'복사 ' + str(copied) + '개' if apply else '복사 예정 ' + str(len(plan) - same) + '개'} / 동일 {same} / 모듈 겹침 {len(ambiguous)} / 미분류 {unmatched} / 용량초과 {len(too_big)} → {out.relative_to(ROOT)}")
    return out

def drive_layout_cfg():
    return cfg("integrated_rules.yaml")["drive_layout"]

def folder_tree(root):
    """정리용 표준 폴더 구조를 만든다(이미 있으면 그대로 둔다). 예: python qms_workflow.py foldertree "E:\\SHINHWA" """
    lay = drive_layout_cfg()
    names = [lay[k] for k in ("qms", "lot", "safety", "equipment", "training", "production", "inventory", "quality", "sq", "customer", "unsorted")]
    base = Path(root).expanduser()
    for n in names:
        (base / n).mkdir(parents=True, exist_ok=True)
    print(f"[FOLDER TREE] {base} 아래에 {len(names)}개 폴더 준비: " + ", ".join(names))
    return base

def classify_category(rel_dirs, fn, lay, kw):
    """정리 분류: QMS 문서 > SQ > 단일 모듈 키워드 > 고객사 > 미분류. 반환 (분류키, 사유)
    QMS: 파일명이 SH-/SH_ 로 시작, qms_keywords(파일명·폴더), qms_name_keywords(파일명만), qms_folder_keywords(폴더만)."""
    hay = fn + " " + " ".join(rel_dirs)
    low, fnl, fol = hay.lower(), fn.lower(), " ".join(rel_dirs).lower()
    mod, mwhy = classify_module(rel_dirs, fn, kw)
    if (fn.upper().startswith(("SH-", "SH_")) or any(w.lower() in low for w in lay["qms_keywords"])
            or any(w.lower() in fnl for w in lay.get("qms_name_keywords", [])) or any(w.lower() in fol for w in lay.get("qms_folder_keywords", []))):
        return "qms", "QMS 문서(SH-/키워드)"
    if any(re.search(rf"(?<![A-Za-z]){w}(?![A-Za-z])", hay) for w in lay["sq_keywords"]):
        return "sq", "SQ 심사 자료"
    if mod:
        return mod, mwhy
    if any(w.lower() in low for w in lay["customer_keywords"]):
        return "customer", "고객사(한온시스템)"
    for name, target in (lay.get("name_overrides") or {}).items():          # 미분류일 때만: 파일명 → 분류(폴더 지정보다 먼저)
        if name.lower() in fn.lower():
            return target, f"파일명 지정({name})"
    for name, target in (lay.get("folder_overrides") or {}).items():       # 미분류일 때만: 사용자가 확인한 폴더 이름 → 분류
        if any(name.lower() in d.lower() for d in rel_dirs):
            return target, f"폴더 지정({name})"
    return "unsorted", mwhy

def organize_plan(src, dest_root, apply=False, only=(), exclude=()):
    """원본 폴더의 파일을 표준 폴더 구조로 '복사' 계획을 세운다(기본 미리보기). 원본은 읽기만 하며 이동·삭제하지 않는다.
    분류: QMS 문서(SH-/키워드) > SQ > 단일 모듈 키워드 > 한온시스템 > 그 외/여러 모듈은 99_미분류_확인필요. 하위는 파일 수정 연도 폴더."""
    srcp, dest = Path(src).expanduser(), Path(dest_root).expanduser()
    if not srcp.exists():
        sys.exit(f"원본 폴더를 찾을 수 없음: {src}")
    lay, kw = drive_layout_cfg(), cfg("integrated_rules.yaml")["input_sync"]["keywords"]
    skip = {"$recycle.bin", "system volume information", "windows", "program files", "program files (x86)", ".git", "node_modules", "__pycache__", "appdata"}
    limit = lay["max_file_mb"] * 1024 * 1024
    plan, big = [], []
    for dp, dns, fns in os.walk(srcp):
        dns[:] = [d for d in dns if d.lower() not in skip and not d.startswith("$") and (Path(dp) / d).resolve() != dest.resolve()]
        prune_scope(srcp, dp, dns, fns, only, exclude)
        for fn in fns:
            f = Path(dp) / fn
            if fn.lower() in lay["skip_names"] or fn.startswith("~$") or fn.lower().endswith(".tmp"):
                continue
            try:
                st = f.stat()
            except OSError:
                continue
            if st.st_size > limit:
                big.append(str(f)); continue
            cat, why = classify_category(f.relative_to(srcp).parts[:-1], fn, lay, kw)
            year = dt.datetime.fromtimestamp(st.st_mtime).strftime("%Y")
            plan.append((f, cat, why, dest / lay[cat] / year / fn, st.st_size, dt.datetime.fromtimestamp(st.st_mtime).date()))
    (OUT_DIR / "REPORTS").mkdir(parents=True, exist_ok=True)
    out = unique_path(OUT_DIR / "REPORTS" / f"organize_plan_{dt.datetime.now():%Y%m%d_%H%M%S}.csv")
    copied = same = 0
    with open(out, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["원본 경로", "분류", "사유", "대상 경로", "크기(KB)", "수정일", "처리"])
        for f, cat, why, dst, size, mdate in sorted(plan, key=lambda x: (x[1], str(x[0]))):
            ex = find_identical(f, dst.parent, dst.name)
            if ex is not None:
                act = "이미 있음(동일)" + ("" if ex == dst else f" → {ex.name}"); same += 1
            elif apply:
                dst.parent.mkdir(parents=True, exist_ok=True)
                act = f"복사 → {safe_copy(f, dst.parent, dst.name)}"; copied += 1
            else:
                act = "복사 예정"
            w.writerow([f, lay[cat], why, dst, size // 1024, mdate, act])
    stale = []                                   # 이전 실행에서 다른 분류 폴더에 복사됐다가 지금은 옮겨진 같은 내용의 복사본(삭제하지 않고 목록만)
    planned = {str(d).lower() for _, _, _, d, _, _ in plan}   # 이번 계획에서 다른 원본이 쓰는 위치는 옛 복사본이 아니므로 제외(같은 파일이 두 폴더에 각각 있는 경우)
    for f, cat, why, dst, size, mdate in plan:
        for other in [lay[k] for k in ("qms", "lot", "safety", "equipment", "training", "production", "inventory", "quality", "sq", "customer", "unsorted")]:
            if other == lay[cat]:
                continue
            old_copy = dest / other / dst.parent.name / f.name
            if str(old_copy).lower() in planned:
                continue
            try:
                if old_copy.exists() and old_copy.stat().st_size == size and old_copy.read_bytes() == f.read_bytes():
                    stale.append(old_copy)
            except OSError:
                pass
    stale = list(dict.fromkeys(stale))
    if stale:
        sp = unique_path(OUT_DIR / "REPORTS" / f"organize_stale99_{dt.datetime.now():%Y%m%d_%H%M%S}.csv")
        with open(sp, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows([["이전 분류 폴더에 남아 있는 옛 복사본(새 위치에 같은 파일이 있음, 삭제는 사람이 확인 후)"]] + [[str(x)] for x in stale])
        print(f"  이전 분류 폴더에 남은 옛 복사본 {len(stale)}개 → {sp.relative_to(ROOT)} (삭제하지 않음)")
    cnt = collections.Counter(lay[c] for _, c, *_ in plan)
    print(f"[ORGANIZE] {'복사 ' + str(copied) + '개' if apply else '미리보기: 복사 예정 ' + str(len(plan) - same) + '개'} / 동일 {same} / 용량초과 {len(big)} → {out.relative_to(ROOT)}")
    print("  분류별: " + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items())))
    if apply:
        log("workflow_log.csv", [now(), str(srcp), "", "organize", str(dest), "system", f"{copied}개 복사(원본 유지), 동일 {same}"])
        print("  원본 폴더는 그대로입니다. 복사본을 확인한 뒤 원본 정리는 사람이 직접 하세요.")
    return out

def sq_match(plan_csv):
    """SQ 필요서류 240건(SH-FM-123~362)과 E 드라이브 정리 계획(organizeplan CSV)의 08_SQ심사·00_QMS문서 파일을 '파일명'으로 대응시킨다(내용은 읽지 않음).
    판정: 이름 일치 / 후보(사람 확인) / 같은 SQ 번호 폴더에 자료만 있음 / 자료 없음. → 07_AUDIT/고객심사/SQ_기존자료_대응표.csv, SQ_기존자료_대응보고서.md
    ※ '이름 일치'는 파일명이 비슷하다는 뜻이며 요구사항을 충족한다는 뜻이 아니다. 충족 여부는 담당자가 내용을 보고 확인한다."""
    audit = ROOT / "07_AUDIT" / "고객심사"
    sq_rows = list(csv.DictReader(open(sq_map_file(audit), encoding="utf-8-sig")))
    dec = {r["정식 SH-FM 번호"]: r["결정"] for r in csv.DictReader(open(audit / "SQ_중복검토_결정.csv", encoding="utf-8-sig"))}
    plan = [r for r in csv.DictReader(open(plan_csv, encoding="utf-8-sig")) if r["분류"] in ("08_SQ심사", "00_QMS문서")]
    norm = lambda t: re.sub(r"[^0-9a-z가-힣]", "", t.lower())
    bigr = lambda t: {t[i:i + 2] for i in range(len(t) - 1)} or {t}
    num_rx = re.compile(r"^\s*(\d+)\s*\.?\s*-\s*(\d+)")
    files, seen = [], set()
    for r in plan:
        parts = r["원본 경로"].replace("/", "\\").split("\\")[1:]
        fn, dirs = parts[-1], parts[:-1]
        key = (fn.lower(), r["분류"])
        if key in seen:
            continue                                    # 같은 이름이 여러 폴더에 있으면 한 건으로
        seen.add(key)
        nos = {f"{m.group(1)}-{m.group(2)}" for d in dirs for m in [num_rx.match(d)] if m}
        files.append((fn, norm(Path(fn).stem), nos, r["분류"], "\\".join(parts)))
    out_rows, tier_c = [], collections.Counter()
    for q in sq_rows:
        name, no = q["필요서류(양식명)"], q["번호"]
        n = norm(re.sub(r"\(.*?\)", "", name)) or norm(name)
        nb = bigr(n)
        scored = []
        for fn, fnn, nos, cat, rel in files:
            if len(n) >= 3 and (n in fnn or (len(fnn) >= 4 and fnn in n and len(fnn) >= 0.7 * len(n))):
                sc = 1.0            # 파일명이 서류명을 포함하거나, 파일명이 서류명의 대부분일 때만(체크시트·관리대장 같은 일반 이름은 제외)
            else:
                fb = bigr(fnn)
                sc = 2 * len(nb & fb) / (len(nb) + len(fb)) if fb else 0.0
            if len(fnn) <= 5:
                sc = min(sc, 0.65)      # 체크시트·관리대장 같은 짧은 일반 이름은 '이름 일치'로 보지 않고 후보로만 둔다
            same_no = no in nos
            scored.append((sc + (0.15 if same_no else 0), sc, same_no, fn, cat, rel))
        scored.sort(key=lambda x: -x[0])
        best = scored[0] if scored else None
        same_folder = [x for x in scored if x[2]]
        if best and best[1] >= 0.7:
            tier = "이름 일치"
        elif best and (best[1] >= 0.4 or (best[2] and best[1] >= 0.25)):
            tier = "후보(사람 확인)"
        elif same_folder:
            tier = "같은 SQ 번호 폴더에 자료만 있음"
        else:
            tier = "자료 없음"
        tier_c[tier] += 1
        cands = [x for x in scored if x[1] >= 0.25][:3] if tier in ("이름 일치", "후보(사람 확인)") else same_folder[:3]
        memo = ""
        if tier in ("이름 일치", "후보(사람 확인)") and q["작성구분"] == "신규 작성 필요":
            memo = "SQ안은 '신규 작성 필요'인데 비슷한 기존 자료가 있음 — 재사용 가능 여부 확인"
        elif tier == "자료 없음" and q["작성구분"] == "기존 절차 연계":
            memo = "'기존 절차 연계'로 표시됐으나 E 드라이브 1차 범위에서 자료를 찾지 못함"
        out_rows.append([q["SQ NO"], q["구분"], no, name, q["정식 SH-FM 번호"], q["작성구분"], dec.get(q["정식 SH-FM 번호"], ""), tier,
                         f"{best[1]:.2f}" if best else "", len(same_folder)] + [f"{c[3]} [{c[4]}] ({c[5]})" for c in cands] + [""] * (3 - len(cands)) + [memo])
    hdr = ["SQ NO", "구분", "번호", "필요서류(양식명)", "정식 SH-FM 번호", "SQ안 작성구분", "중복검토 결정", "판정", "최고 유사도", "같은 번호 폴더 파일 수", "후보1", "후보2", "후보3", "메모"]
    cp = unique_path(audit / "SQ_기존자료_대응표.csv")
    with open(cp, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh); w.writerow(hdr); w.writerows(out_rows)
    by_gu = collections.defaultdict(collections.Counter)
    for r in out_rows:
        by_gu[r[1]][r[7]] += 1
    tiers = ["이름 일치", "후보(사람 확인)", "같은 SQ 번호 폴더에 자료만 있음", "자료 없음"]
    L = ["# SQ 필요서류 ↔ E 드라이브 기존 자료 대응 (파일명 기준)", f"- 생성: {now()}", f"- 입력: {Path(plan_csv).name} (08_SQ심사·00_QMS문서 서로 다른 파일 {len(files)}개)", f"- SQ 필요서류: {len(sq_rows)}건",
         "- **주의**: 파일 이름만 비교했습니다(내용 미확인). '이름 일치'는 파일명이 비슷하다는 뜻이며 요구사항 충족 여부는 담당자가 확인해야 합니다.", "", "## 판정 요약", "", "| 판정 | 건수 |", "|---|---|"]
    L += [f"| {t} | {tier_c[t]} |" for t in tiers]
    L += ["", "## 구분별", "", "| 구분 | " + " | ".join(tiers) + " |", "|---|" + "---|" * len(tiers)]
    L += [f"| {g} | " + " | ".join(str(c[t]) for t in tiers) + " |" for g, c in sorted(by_gu.items())]
    L += ["", "※ 상세는 `SQ_기존자료_대응표.csv` (후보 파일 경로 포함). 사람이 후보를 확인한 뒤에만 '기존 자료 사용'으로 확정합니다(번호·내용은 임의 생성하지 않음)."]
    rp = unique_path(audit / "SQ_기존자료_대응보고서.md")
    rp.write_text("\n".join(L) + "\n", encoding="utf-8")
    log("workflow_log.csv", [now(), Path(plan_csv).name, "", "sqmatch", str(cp.relative_to(ROOT)), "system", " / ".join(f"{t} {tier_c[t]}" for t in tiers)])
    print("[SQ MATCH] " + ", ".join(f"{t} {tier_c[t]}" for t in tiers) + f" → {cp.relative_to(ROOT)}")
    return cp

def name_find(src, kws, only=(), exclude=()):
    """파일·폴더 이름에 키워드가 들어 있는 항목을 찾는다(읽기 전용, 내용은 읽지 않음). 영문 키워드(LOT 등)는 앞뒤가 영문자가 아닐 때만 일치(SLOT·PILOT 제외).
    → 12_OUTPUT/REPORTS/namefind_*.md / .csv"""
    base = Path(src).expanduser()
    if not base.exists():
        sys.exit(f"폴더를 찾을 수 없음: {src}")
    skip = {"$recycle.bin", "system volume information", "windows", "program files", "program files (x86)", ".git", "node_modules", "__pycache__", "appdata"}
    def hit(text):
        for k in kws:
            if re.fullmatch(r"[A-Za-z0-9 ]+", k):
                if re.search(rf"(?<![A-Za-z]){re.escape(k)}(?![A-Za-z])", text, re.I):
                    return k
            elif k.lower() in text.lower():
                return k
        return None
    rows, total = [], 0
    by_top, by_kw, by_ext = collections.Counter(), collections.Counter(), collections.Counter()
    print(f"[NAME FIND] 조사 시작: {base} / 키워드: {', '.join(kws)}  (이름만 확인, 중단: Ctrl+C)", flush=True)
    for dp, dns, fns in os.walk(base):
        dns[:] = [d for d in dns if d.lower() not in skip and not d.startswith("$") and (Path(dp) / d).resolve() != ROOT.resolve()]
        prune_scope(base, dp, dns, fns, only, exclude)
        rel_dirs = Path(dp).relative_to(base).parts
        for fn in fns:
            total += 1
            if total % 20000 == 0:
                print(f"  ... {total:,}개 확인함", flush=True)
            if fn.startswith("~$"):
                continue
            k_file, k_dir = hit(fn), hit(" / ".join(rel_dirs))
            if not (k_file or k_dir):
                continue
            ext = Path(fn).suffix.lower() or "(없음)"
            top = rel_dirs[0] if rel_dirs else "(루트 직하)"
            by_top[top] += 1; by_kw[k_file or k_dir] += 1; by_ext[ext] += 1
            rows.append([top, "파일명" if k_file else "폴더명", k_file or k_dir, ext, str(Path(*rel_dirs, fn)) if rel_dirs else fn])
    L = ["# 이름 검색 결과 (읽기 전용)", f"- 생성: {now()}", f"- 대상: {base}" + (f" / 포함 폴더: {', '.join(only)}" if only else "") + (f" / 제외 폴더: {', '.join(exclude)}" if exclude else ""),
         f"- 키워드: {', '.join(kws)} (파일명 또는 폴더명에 포함)", f"- 확인한 파일 {total:,}개 / 일치 {len(rows):,}개", "",
         "## 최상위 폴더별 일치", ""] + [f"- {k}: {v}" for k, v in by_top.most_common(30)]
    L += ["", "## 키워드별", ""] + [f"- {k}: {v}" for k, v in by_kw.most_common()]
    L += ["", "## 확장자별", ""] + [f"- {k}: {v}" for k, v in by_ext.most_common(12)]
    fn_rows = [r for r in rows if r[1] == "파일명"]
    L += ["", f"## 파일명에 키워드가 있는 예시 (최대 80, 전체 {len(fn_rows)}개)", ""] + [f"- {r[4]}" for r in fn_rows[:80]]
    L += ["", "※ 이름만 비교한 결과입니다. 실제 LOT 추적 기록인지는 담당자가 열어서 확인해야 합니다. 아무것도 이동·복사·삭제하지 않았습니다."]
    (OUT_DIR / "REPORTS").mkdir(parents=True, exist_ok=True)
    stamp = f"{dt.datetime.now():%Y%m%d_%H%M%S}"
    mdp = unique_path(OUT_DIR / "REPORTS" / f"namefind_{stamp}.md")
    mdp.write_text("\n".join(L) + "\n", encoding="utf-8")
    cp = unique_path(OUT_DIR / "REPORTS" / f"namefind_{stamp}.csv")
    with open(cp, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh); w.writerow(["최상위 폴더", "일치 위치", "키워드", "확장자", "경로"]); w.writerows(rows[:5000])
    print(f"[NAME FIND] 파일 {total:,}개 확인 / 일치 {len(rows):,}개 (파일명 {len(fn_rows)}) → {mdp.relative_to(ROOT)}")
    return mdp

def make_light_package():
    """PC 에서 드라이브 조사·정리·복사(drivescan/organizeplan/inputsync)만 쓸 수 있는 가벼운 ZIP 을 만든다.
    경로가 짧고(최대 약 60자) 파일이 적어, 전체 저장소 ZIP 이 풀리지 않는 PC 에서도 풀린다. → LIGHT_PACKAGE/SHINHWA_QMS_LIGHT.zip"""
    out_dir = ROOT / "LIGHT_PACKAGE"
    out_dir.mkdir(exist_ok=True)
    zp = unique_path(out_dir / "SHINHWA_QMS_LIGHT.zip") if False else out_dir / "SHINHWA_QMS_LIGHT.zip"
    root = "SHINHWA_QMS_LIGHT"
    readme = (
        "SHINHWA QMS LIGHT — 로컬 드라이브 조사·정리·복사 도구 (읽기 전용 위주)\r\n\r\n"
        "1) Python 3.10 이상 설치 (설치 화면에서 Add python.exe to PATH 체크)\r\n"
        "2) 이 폴더에서 명령 프롬프트(cmd)를 열고:\r\n"
        "     python -m pip install -r requirements.txt\r\n"
        "     set PYTHONUTF8=1\r\n"
        "3) 드라이브 조사(내용은 읽지 않고 이름만 집계, 아무것도 바꾸지 않음):\r\n"
        "     python scripts\\qms_workflow.py drivescan E:/\r\n"
        "   결과: 12_OUTPUT\\REPORTS\\drivescan_*.md\r\n"
        "4) 정리 미리보기 / 복사(원본은 그대로 두고 복사만):\r\n"
        "     python scripts\\qms_workflow.py foldertree E:/SHINHWA\r\n"
        "     python scripts\\qms_workflow.py organizeplan E:/정리할폴더 E:/SHINHWA\r\n"
        "     python scripts\\qms_workflow.py organizeplan E:/정리할폴더 E:/SHINHWA --apply\r\n"
        "5) 경로는 E:/ 처럼 슬래시(/)로 쓰세요. \"E:\\\" 처럼 끝에 역슬래시를 붙이면 오류가 납니다.\r\n")
    keep = [("scripts/qms_workflow.py", ROOT / "scripts" / "qms_workflow.py"), ("requirements.txt", ROOT / "requirements.txt")]
    keep += [(f"00_CONFIG/{f.name}", f) for f in sorted((ROOT / "00_CONFIG").glob("*.yaml"))]
    dirs = ["01_ORIGINAL/MASTER_REF", "02_REVIEW", "03_EDIT", "04_APPROVAL/승인대기", "04_APPROVAL/검토완료", "04_APPROVAL/승인완료", "05_FINAL", "06_HISTORY",
            "11_INPUT/LOT", "11_INPUT/SAFETY", "11_INPUT/EQUIPMENT", "11_INPUT/TRAINING", "11_INPUT/PRODUCTION", "11_INPUT/INVENTORY", "11_INPUT/QUALITY", "12_OUTPUT/REPORTS"]
    dirs = [d for d in dirs if all(ord(c) < 128 for c in d)]   # 이름은 영문만(압축 호환)
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for arc, f in keep:
            z.write(f, f"{root}/{arc}")
        for d in dirs:
            z.writestr(f"{root}/{d}/", "")
        for fn, hdr in (("workflow_log.csv", "timestamp,action,status,message"), ("error_log.csv", "timestamp,file,error_type,detail"), ("revision_history.csv", "timestamp,document_no,revision,action,source,target,note")):
            z.writestr(f"{root}/99_LOG/{fn}", "\ufeff" + hdr + "\r\n")
        z.writestr(f"{root}/README.txt", "\ufeff" + readme)
    n = len(zipfile.ZipFile(zp).namelist())
    print(f"[LIGHT] {zp.relative_to(ROOT)} ({zp.stat().st_size // 1024} KB, 항목 {n}개, 가장 긴 경로 {max(len(x) for x in zipfile.ZipFile(zp).namelist())}자)")
    return zp

def full_operation():
    """전체 운영: QMS 사이클(승인 직전까지) → 통합 점검 → 조치사항 → 대시보드 → 주간 보고. 승인/배포는 하지 않는다."""
    fullcycle()
    integrated_audit()
    collect_actions()
    dashboard_data()
    weekly_report()
    print("\n[완료] 승인(approve/sign)과 FINAL 배포(finalize)는 사람이 지시할 때만 실행합니다. 월간 보고·심사 패키지·고객 대응·백업은 필요 시 개별 명령으로.")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "run": run(rereview="--rereview" in sys.argv)
    elif cmd == "recheck": recheck()
    elif cmd == "approve" and len(sys.argv) > 2: advance(sys.argv[2], "승인대기", "검토완료", "검토 완료")
    elif cmd == "sign" and len(sys.argv) > 2: advance(sys.argv[2], "검토완료", "승인완료", "승인")
    elif cmd == "gates": gates()
    elif cmd == "diff" and len(sys.argv) > 2: diff_cmd(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif cmd == "package" and len(sys.argv) > 2: package_cmd(sys.argv[2])
    elif cmd == "scan": scan()
    elif cmd == "crosscheck": crosscheck()
    elif cmd == "ledger": ledger_check()
    elif cmd == "releasegate": release_gate()
    elif cmd == "fullaudit": fullaudit()
    elif cmd == "fullcycle": fullcycle()
    elif cmd == "sqaudit": sq_audit()
    elif cmd == "fulloperation": full_operation()
    elif cmd == "mcphealth": mcp_health_check()
    elif cmd == "foldertree" and len(sys.argv) > 2: folder_tree(sys.argv[2])
    elif cmd == "makelight": make_light_package()
    elif cmd == "sqmatch" and len(sys.argv) > 2: sq_match(sys.argv[2])
    elif cmd == "drivescan" and len(sys.argv) > 2: drive_scan(sys.argv[2], opt_list("--only"), opt_list("--exclude"))
    elif cmd == "namefind" and len(sys.argv) > 3: name_find(sys.argv[2], [k for k in sys.argv[3].split(",") if k.strip()], opt_list("--only"), opt_list("--exclude"))
    elif cmd == "dupscan" and len(sys.argv) > 2: dup_scan(sys.argv[2], opt_list("--only"))
    elif cmd == "organizeplan" and len(sys.argv) > 3: organize_plan(sys.argv[2], sys.argv[3], apply="--apply" in sys.argv, only=opt_list("--only"), exclude=opt_list("--exclude"))
    elif cmd == "inputsync" and len(sys.argv) > 2 and opt_list("--as") and opt_list("--as")[0] not in OPS_MODULES: sys.exit("--as 는 " + "/".join(OPS_MODULES) + " 중 하나여야 합니다")
    elif cmd == "inputsync" and len(sys.argv) > 2: input_sync(sys.argv[2], apply="--apply" in sys.argv, only=opt_list("--only"), exclude=opt_list("--exclude"), match=[re.sub(r"\s+", "", m) for m in opt_list("--match")], force_mod=(opt_list("--as") or [None])[0] if (opt_list("--as") or [None])[0] in OPS_MODULES else None)
    elif cmd == "mcpsafestart": mcp_safe_start()
    elif cmd == "qmsaudit": ops_qms_audit()
    elif cmd == "integratedaudit": integrated_audit()
    elif cmd == "recordinventory": record_inventory(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "modulewords" and len(sys.argv) > 2 and sys.argv[2] in OPS_MODULES: module_words(sys.argv[2], [x for x in (sys.argv[3].split(",") if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else []) if x], (sys.argv[sys.argv.index("--file") + 1] if "--file" in sys.argv and sys.argv.index("--file") + 1 < len(sys.argv) else ""))
    elif cmd == "modulecheck" and len(sys.argv) > 2 and sys.argv[2] in OPS_MODULES: module_check(sys.argv[2])
    elif cmd == "collectactions": collect_actions()
    elif cmd == "dashboarddata": dashboard_data()
    elif cmd == "weeklyreport": weekly_report()
    elif cmd == "monthlyreport": monthly_report()
    elif cmd == "auditpackage" and len(sys.argv) > 2 and sys.argv[2] in AUDIT_KINDS: audit_package(sys.argv[2])
    elif cmd == "customerresponse": customer_response()
    elif cmd == "backupworkspace": backup_workspace()
    elif cmd == "sqnumber": sq_number()
    elif cmd == "sqdrafts": sq_drafts(sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else "높음", overwrite="--overwrite" in sys.argv)
    elif cmd == "fmregister": fm_master_register()
    elif cmd == "gatecheck": gatecheck()
    elif cmd == "status": status()
    elif cmd == "finalize": finalize()
    elif cmd == "rollbackcheck": rollbackcheck()
    elif cmd == "finalreport": final_report_cmd()
    elif cmd == "integrity": sys.exit(0 if integrity_check() else 1)
    elif cmd == "splitpdf" and len(sys.argv) > 2: split_pdf(sys.argv[2])
    else: print(__doc__)
