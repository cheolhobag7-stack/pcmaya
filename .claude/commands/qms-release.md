승인 완료된 QMS 문서만 FINAL 배포 대상으로 처리한다. 작업 디렉터리: `SHINHWA_QMS_WORKFLOW/`

규칙:
1. 승인상태가 확인되지 않으면 이동 금지
2. FAIL/HOLD 상태 문서는 FINAL 이동 금지
3. 기존 FINAL 파일이 있으면 덮어쓰지 말고 이전 버전을 `06_HISTORY` 로 보관 (스크립트가 자동 처리)
4. 먼저 `python3 scripts/qms_workflow.py status` 로 배포 대상 목록을 출력
5. 사용자 승인 여부를 확인한 뒤에만 `python3 scripts/qms_workflow.py finalize` 실행
6. 변경이력은 `99_LOG/revision_history.csv` 에 자동 기록됨
