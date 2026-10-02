#!/usr/bin/env python3
"""(주)신화에이치앤티 QMS 문서관리 자동화 (ISO 9001:2015 / IATF 16949:2016).

사용법 (SHINHWA_QMS_WORKFLOW 에서):
  python3 scripts/qms_workflow.py run [--rereview]  # (--rereview: 이미 검토한 파일도 새 보고서로 다시 검토)
  # 01_ORIGINAL 분류 → 17개 항목 검토 → 02_REVIEW(+수정후보) / 04_APPROVAL
  python3 scripts/qms_workflow.py recheck    # 03_EDIT/수정완료 재검증
  python3 scripts/qms_workflow.py approve F  # (사람) 승인대기 → 검토완료
  python3 scripts/qms_workflow.py sign F     # (사람) 검토완료 → 승인완료
  python3 scripts/qms_workflow.py crosscheck # QM/QP/WI/FM 상호참조 종합 점검 → 02_REVIEW/qms_crosscheck_summary.md
  python3 scripts/qms_workflow.py scan       # 신규 문서 검색
  python3 scripts/qms_workflow.py status     # 04_APPROVAL 문서별 FINAL 가능 여부
  python3 scripts/qms_workflow.py gates      # AP-01~04 게이트 양식 존재 확인
  python3 scripts/qms_workflow.py finalize   # 승인완료 재검증 → 05_FINAL + PDF + 배포본 + 06_HISTORY

절대 규칙(코드로 강제):
  - 원본은 삭제/덮어쓰기 하지 않는다. 단계 이동은 모두 '복사'이며, 기존 파일과 이름이 겹치면 _vN 으로 새로 저장한다.
    (01_ORIGINAL 루트에 투입된 파일을 유형 폴더로 정리하는 것만 같은 01_ORIGINAL 안의 이동이다.)
  - 수정본/수정후보는 항상 새 파일(03_EDIT/수정중)이며 모든 생성은 revision_history.csv 에 기록한다.
  - 문서번호 오류가 하나라도 있으면 FINAL 이동 금지. 검토 이슈가 있으면 FINAL 이동 금지.
  - 승인(문서상태=승인완료 + 사람의 sign) 전 문서는 배포본을 만들지 않는다.
  - 폐기 문서 참조는 오류. 확정되지 않은 값은 임의로 만들지 않고 '[확인 필요]'로 표시한다.
"""
import csv, hashlib, json, re, shutil, subprocess, sys, zipfile, datetime as dt
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
            if p.is_file() and p.name != ".gitkeep":
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
        stem_name = re.sub(r"(_수정후보.*|_v\d+)$", "", q.stem)
        if m and norm(m.group(0)) == me and (r.group(1) if r else None) == rev \
                and stem_name != re.sub(r"(_v\d+)$", "", p.stem):
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
        add("내용보완", "본문 텍스트 추출 불가(PDF/미지원 형식) - 본문 검사 생략, 수동 확인 필요")
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
    """수정후보: 원본을 건드리지 않고 03_EDIT/수정중 에 새 파일 생성. 확정되지 않은 값은 임의 생성 금지."""
    ts = dt.datetime.now().strftime("%Y%m%d%H%M%S")
    out = D["edit"] / "수정중" / f"{p.stem}_수정후보_{ts}.md"
    lines = [f"# 수정후보: {p.name}", f"- 생성: {now()}", f"- 원본: {p} (변경 없음)",
             f"- 주의: '{UNCONFIRMED}' 표시는 담당자 확정 전에는 임의 값을 넣지 않음", "", "| # | 분류 | 문제 | 수정 제안 |", "|---|---|---|---|"]
    for i, (c, m, f) in enumerate(issues, 1):
        lines.append(f"| {i} | {c} | {m} | {f or '-'} |")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    rv = (re.search(cfg("document_number_rules.yaml")["revision_pattern"], p.name) or [None, ""])[1]
    log("revision_history.csv", [dt.date.today(), docno or p.stem, rv, "", f"수정후보 생성(미확정, {len(issues)}건): {out.name}", "system", ""])
    return out

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
    rows.append(("승인상태", "PASS" if approved else "HOLD", (st.group(1) if st else "") if approved else "승인 전"))
    ph = hit(kw=["삭제 지시"])
    hold_msgs = hit("확인필요")
    row("삭제 지시 문구", ph, bad_note="; ".join(ph)[:80])
    if hold_msgs:
        rows.append(("SH 접두어 참조", "HOLD", "; ".join(hold_msgs)[:80]))
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
        print(f"[REVIEW ] {p.name}: {len(issues)}건 → 02_REVIEW/{folder} (수정후보: 03_EDIT/수정중/{cand.name})")
    else:
        safe_copy(p, D["appr"] / "승인대기")
        log("workflow_log.csv", [now(), name, "", p.parent.name, "04_APPROVAL/승인대기", "system",
                                 "검사통과 (문서상태 승인완료 표기됨)" if approved else "검사통과 (승인 전: 배포 불가)"])
        print(f"[PASS   ] {p.name} → 04_APPROVAL/승인대기")
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
    multi = {k: sorted(v) for k, v in revs.items() if len(v) > 1}
    lines += ["", "## 동일 문서번호의 복수 Rev (최신 Rev 후보)"]
    lines += [f"- {k}: Rev.{', Rev.'.join(v)} → 최신 후보 Rev.{v[-1]}" for k, v in sorted(multi.items())] or ["- 없음"]
    out = unique_path(D["rev"] / "qms_crosscheck_summary.md")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    cnt = {k: sum(r[2] == k for r in rows) for k in ("PASS", "HOLD", "FAIL")}
    print(f"[CROSSCHECK] PASS {cnt['PASS']} / HOLD {cnt['HOLD']} / FAIL {cnt['FAIL']} → {out.relative_to(ROOT)}")

def scan():
    """1. 신규 문서 검색: 아직 검토되지 않은 파일 목록."""
    done, new = processed(), []
    for p in sorted(D["orig"].rglob("*")):
        if p.is_file() and p.name != ".gitkeep" and sha(p) not in done:
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

def finalize():
    num = cfg("document_number_rules.yaml")
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
            old.rename(obsolete_dir / f"{old.stem}__superseded{old.suffix}")
            for oldpdf in (D["final"] / "PDF").glob(f"{old.stem}.pdf"):
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
        print(f"[FINAL  ] {p.name} → 05_FINAL/{sub}, PDF{'+배포본' if dist else ' 없음'}, 06_HISTORY 백업")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "run": run(rereview="--rereview" in sys.argv)
    elif cmd == "recheck": recheck()
    elif cmd == "approve" and len(sys.argv) > 2: advance(sys.argv[2], "승인대기", "검토완료", "검토 완료")
    elif cmd == "sign" and len(sys.argv) > 2: advance(sys.argv[2], "검토완료", "승인완료", "승인")
    elif cmd == "gates": gates()
    elif cmd == "scan": scan()
    elif cmd == "crosscheck": crosscheck()
    elif cmd == "status": status()
    elif cmd == "finalize": finalize()
    else: print(__doc__)
