from pathlib import Path
import re, csv, yaml
from datetime import datetime
from common_extract import extract_text

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT/"01_QMS_ORIGINAL"
REVIEW = ROOT/"02_QMS_REVIEW"
CFG = yaml.safe_load((ROOT/"00_CONFIG"/"qms_rules.yaml").read_text(encoding="utf-8"))
REVIEW.mkdir(parents=True, exist_ok=True)

DOC_RE = re.compile(r"\b(?:SH-)?(?:QM|QP|WI|FM)-\d{3}\b", re.I)
FILE_DOC_RE = re.compile(r"(SH-(QM|QP|WI|FM)-\d{3})", re.I)
REV_RE = re.compile(r"Rev\.\d{2}", re.I)

def normalize(ref):
    ref = ref.upper()
    return ref if ref.startswith("SH-") else "SH-"+ref

def actual_docs():
    docs = set()
    for base_name in ["01_QMS_ORIGINAL","03_QMS_EDIT","04_QMS_APPROVAL","05_QMS_FINAL"]:
        base = ROOT/base_name
        if not base.exists(): continue
        for p in base.rglob("*"):
            if p.is_file():
                m = FILE_DOC_RE.search(p.stem)
                if m: docs.add(m.group(1).upper())
    return docs

def main():
    known = actual_docs()
    rows = []
    for p in ORIGINAL.rglob("*"):
        if not p.is_file(): continue
        st, issues = "PASS", []
        fm = FILE_DOC_RE.search(p.stem)
        rm = REV_RE.search(p.stem)
        file_doc = fm.group(1).upper() if fm else ""
        file_rev = rm.group(0) if rm else ""
        if not file_doc:
            st="FAIL"; issues.append("파일명 문서번호 누락")
        if not file_rev:
            st="HOLD" if st=="PASS" else st; issues.append("파일명 Rev 누락")
        try:
            text = extract_text(p)
        except Exception as e:
            rows.append([str(p.relative_to(ROOT)),file_doc,file_rev,"FAIL",f"읽기 실패: {e}"])
            continue
        refs = sorted(set(normalize(m.group(0)) for m in DOC_RE.finditer(text)))
        if any(x in text for x in CFG.get("prohibited_phrases",[])):
            st="FAIL"; issues.append("삭제 지시 문구 발견")
        legacy = [m.group(0).upper() for m in re.finditer(r"(?<!SH-)\b(?:QM|QP|WI|FM)-\d{3}\b", text, re.I)]
        if legacy:
            st="HOLD" if st=="PASS" else st; issues.append("SH 접두어 미적용 참조")
        missing = [r for r in refs if r not in known and r != file_doc]
        if missing:
            st="FAIL"; issues.append("미존재 참조: "+", ".join(missing[:20]))
        if not any(x in text for x in CFG["company"]["accepted_names"]):
            st="HOLD" if st=="PASS" else st; issues.append("회사명 확인 필요")
        rows.append([str(p.relative_to(ROOT)),file_doc,file_rev,st," | ".join(issues),"; ".join(refs[:100])])

    ts=datetime.now().strftime("%Y%m%d_%H%M%S")
    out=REVIEW/f"qms_audit_{ts}.csv"
    with out.open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.writer(f); w.writerow(["file","document_no","revision","status","issues","references"]); w.writerows(rows)
    md=REVIEW/f"qms_audit_{ts}.md"
    lines=["# QMS 자동감사",""]
    for s in ["PASS","HOLD","FAIL"]:
        lines.append(f"- {s}: {sum(r[3]==s for r in rows)}")
    lines+=["","## HOLD / FAIL"]
    for r in rows:
        if r[3] in {"HOLD","FAIL"}: lines.append(f"- [{r[3]}] {r[0]} :: {r[4]}")
    md.write_text("\n".join(lines),encoding="utf-8")
    print(out); print(md)

if __name__=="__main__":
    main()
