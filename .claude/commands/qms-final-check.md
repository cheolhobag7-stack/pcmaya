QMS 문서의 최종 배포 가능 여부를 검사한다. 작업 디렉터리: `SHINHWA_QMS_WORKFLOW/`

실행: `python3 scripts/qms_workflow.py status` (04_APPROVAL 문서별 FINAL 가능 여부, FINAL 직전 재검증 기준)

검사 기준:
- 문서번호 일치
- Rev 일치
- 승인상태 완료 (본문 문서상태 + 04_APPROVAL/승인완료)
- 금지된/폐기 참조문서 없음
- 최신 수정본 여부 확인
- 중복 파일 없음

결과는 반드시 아래 3단계로 표시:
- PASS: 승인 및 배포 가능
- HOLD: 확인 또는 승인 필요
- FAIL: 수정 필요

원본 파일은 수정하지 않는다.
