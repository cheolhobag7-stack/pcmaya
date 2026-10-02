# SHINHWA QMS Claude Code Workflow v0.3

## 추가된 핵심 기능
- PDF 본문 텍스트 검사
- 실제 존재하지 않는 QM/QP/WI/FM 참조 자동 탐지
- 동일 문서번호의 중복 Rev 검사
- 최신 Rev 후보 식별
- 문서관리대장(XLSX/XLSM)과 실제 파일 자동 대조
- FINAL Release Gate 자동 판정
- 전체 자동감사 명령 `/qms-full-audit`

## 설치
```bash
pip install -r requirements.txt
```

## 권장 실행
```text
/qms-full-audit
```

또는 개별 실행:
```bash
python scripts/qms_review.py
python scripts/qms_content_review.py
python scripts/qms_revision_crosscheck.py
python scripts/qms_register_compare.py
python scripts/qms_release_gate.py
```

## 문서관리대장 사용
`00_CONFIG` 폴더에 파일명에 `문서관리대장`이 포함된 XLSX/XLSM 파일을 넣는다.
샘플:
`SHINHWA_QMS_문서관리대장_샘플.xlsx`

## FINAL 판정
- PASS: 배포 후보
- HOLD: 승인/확인 후 재검사
- FAIL: 배포 금지

## 현재 범위
- DOCX
- XLSX/XLSM
- PDF(텍스트형)
- TXT/MD

스캔형 PDF는 OCR 없이 HOLD 처리한다.
