FINAL 릴리스본의 무결성(SHA-256)을 검사한다. 작업 디렉터리: `SHINHWA_QMS_WORKFLOW/`

`python3 scripts/qms_workflow.py integrity` — 05_FINAL/RELEASED 의 MANIFEST.json 해시와 실제 파일을 대조한다. 변조/누락은 FAIL(종료코드 1).
결과: `05_FINAL/RELEASED/무결성검사*.md`, `05_FINAL/DISTRIBUTION/final_integrity_*.csv`
