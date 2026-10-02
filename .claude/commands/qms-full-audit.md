QMS 전체 자동감사를 실행한다. 작업 디렉터리: `SHINHWA_QMS_WORKFLOW/`

1. `python3 scripts/qms_workflow.py fullaudit`
   - 신규 문서 검색 → 점검(DOCX/XLSX/PDF 본문, 양식 시트 분할) → 상호참조·중복 Rev 점검 → 문서관리대장 대조 → FINAL Release Gate
2. 생성된 보고서를 읽고 PASS/HOLD/FAIL 로 요약한다.
   - `02_REVIEW/자동검토결과/*_요약.md`, `qms_crosscheck_summary*.md`, `qms_ledger_check*.md`, `qms_release_gate*.md`
3. FAIL 은 배포 금지, HOLD 는 승인/확인 후 재검사. 항목별 조치 권고를 작성한다 (확정되지 않은 값은 임의 생성 금지).
4. 문서별 FINAL Gate 표는 `python3 scripts/qms_workflow.py gatecheck`.

원본은 수정/삭제하지 않는다. approve/sign/finalize 는 사용자가 지시할 때만 실행한다.
