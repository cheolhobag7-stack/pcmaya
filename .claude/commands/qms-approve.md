실제 승인이 끝난 문서를 승인 처리한다. 작업 디렉터리: `SHINHWA_QMS_WORKFLOW/`

1. 승인 대상 파일을 사용자에게 확인한다. 파일이 지정되지 않았으면 `python3 scripts/qms_workflow.py status` 로 후보를 보여주고 어떤 문서의 승인이 실제로 끝났는지 묻는다. 임의로 고르지 않는다.
2. 사용자가 실제 승인을 확인한 문서만: `approve <파일>` (승인대기→검토완료), 이어서 `sign <파일>` (검토완료→승인완료).
   `sign` 은 승인 패키지에 `APPROVED.txt` 승인 표시 파일을 생성한다. 사용자의 실제 승인 없이 실행하지 않는다.
3. 승인 후 FINAL 배포는 `/qms-final-release` 로 진행한다.
