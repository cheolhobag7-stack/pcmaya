수정 제안을 만든다. 작업 디렉터리: `SHINHWA_QMS_WORKFLOW/`

`python3 scripts/qms_workflow.py run` (또는 `fullaudit`) 이 문제 문서마다 `03_EDIT/AUTO_DRAFT/<문서>_수정필요사항_*.md` 를 만든다. 자동 수정은 하지 않는다(auto_edit_allowed=NO). 확정되지 않은 값은 `[확인 필요]` 로 표시한다.
