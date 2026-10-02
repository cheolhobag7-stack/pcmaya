QMS 전체 사이클을 승인 직전까지 실행한다. 작업 디렉터리: `SHINHWA_QMS_WORKFLOW/`

1. `python3 scripts/qms_workflow.py fullcycle`
   - 신규 문서 검색 → 전체 자동감사 → 수정 제안/`03_EDIT/AUTO_DRAFT` → `03_EDIT/수정완료` 재감사(+원본↔수정본 DIFF)
     → Release Gate → `04_APPROVAL/PACKAGES` 승인 패키지
2. 생성된 보고서(`02_REVIEW/qms_release_gate*.md`, 자동검토결과 요약, 승인 패키지)를 읽고 PASS/HOLD/FAIL 로 요약한다.
3. 여기서 멈춘다. 승인(`approve`/`sign`)과 FINAL 배포(`finalize`)는 사용자가 실제 승인 후 지시할 때만 실행한다.

원본은 수정/삭제하지 않는다. 확정되지 않은 값은 임의로 만들지 않는다.
