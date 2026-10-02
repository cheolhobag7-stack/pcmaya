QM/QP/WI/FM 상호참조만 별도로 점검한다. 작업 디렉터리: `SHINHWA_QMS_WORKFLOW/`

1. `python3 scripts/qms_workflow.py crosscheck` 실행 (양식 워크북은 시트=양식 단위로 점검)
2. 참조된 문서번호가 `01_ORIGINAL`, `03_EDIT`, `04_APPROVAL`, `05_FINAL`, 문서관리대장/FM Master 에 존재하는지 확인 (자동)
3. SH 접두어 없는 참조는 HOLD, 존재하지 않거나 폐기/참조금지 문서 참조는 FAIL (자동)
4. 동일 문서번호가 여러 Rev로 존재하면 최신 Rev 후보를 표시 (자동)
5. 결과는 `02_REVIEW/qms_crosscheck_summary.md` 에 저장된다. 이를 읽어 PASS/HOLD/FAIL 로 요약하고 문서별 권고를 작성한다.

원본은 수정하지 않는다.
