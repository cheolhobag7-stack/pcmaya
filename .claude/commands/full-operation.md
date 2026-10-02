전체 운영을 실행한다(승인 직전까지). 작업 디렉터리: `SHINHWA_QMS_WORKFLOW/`

1. `python3 scripts/qms_workflow.py fulloperation`
   - QMS 사이클(감사→AUTO_DRAFT→재감사→Release Gate→승인 패키지) → 통합 점검(QMS + 현장 모듈 7종) → 조치사항 취합 → 대시보드 데이터 → 주간 보고
2. 생성 보고서(`12_OUTPUT/REPORTS`, `12_OUTPUT/ACTION_ITEMS`, `13_MANAGEMENT/WEEKLY`, `02_REVIEW/qms_release_gate*.md`)를 읽고 PASS/HOLD/FAIL·NO_DATA 로 요약한다. NO_DATA(입력 없음)는 PASS 가 아니다.
3. 승인(approve/sign)과 FINAL 배포(finalize)는 사용자가 실제 승인 후 지시할 때만 실행한다. 원본은 수정/삭제하지 않는다.
