승인 완료된 문서만 FINAL 로 배포한다. 작업 디렉터리: `SHINHWA_QMS_WORKFLOW/`

1. 먼저 `python3 scripts/qms_workflow.py gatecheck` 로 대상 문서의 Release Gate(G1~G8)를 보여준다.
2. 사용자 확인 후 `python3 scripts/qms_workflow.py finalize`
   - Gate 재확인(문서번호/Rev/승인상태/APPROVED.txt) → 05_FINAL + 05_FINAL/RELEASED/<문서>/Rev<NN>/(MANIFEST) → 이전 Rev 롤백 백업 후 06_HISTORY 이동 → 배포목록·최종보고서
3. Gate FAIL/HOLD 문서는 이동되지 않는다. 자동 롤백은 하지 않는다.
