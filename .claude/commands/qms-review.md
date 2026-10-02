QMS 원본 폴더를 자동 점검한다. 작업 디렉터리: `SHINHWA_QMS_WORKFLOW/`

수행 순서:
1. `00_CONFIG/*.yaml` 규칙 확인 (qms_rules, document_number_rules, customer_rules, approval_rules, gate_rules)
2. 신규 문서 검색: `python3 scripts/qms_workflow.py scan`
3. 점검 실행: `python3 scripts/qms_workflow.py run`
   (문서번호·Rev·문서명·회사명·일자·결재·상호참조·폐기/참조금지·ISO/IATF·보존기간·LOT·페이지/목차·중복 검사,
    02_REVIEW 오류 보고서, 03_EDIT/수정중 수정후보, 통과 문서는 04_APPROVAL/승인대기)
4. 출력된 문서별 요약표와 `02_REVIEW/자동검토결과/*_요약.md` 를 읽어 PASS/HOLD/FAIL 로 요약
5. FAIL/HOLD 문서별 수정 권고 작성 (`03_EDIT/수정중` 수정후보 참고, 확정되지 않은 값은 임의 생성 금지)
6. FINAL 가능 여부: `python3 scripts/qms_workflow.py status`
7. 원본은 절대 수정/삭제하지 않는다. approve/sign/finalize 는 사용자가 지시할 때만 실행한다.
