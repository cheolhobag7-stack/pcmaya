---
name: qms-review
description: (주)신화에이치앤티 QMS 문서(SH-QM/QP/WI/FM)를 자동 검토한다. 신규 문서 검색, 문서번호/Rev/상호참조/ISO·IATF 검사, 오류 보고서와 수정 후보 생성, 승인대기 분리, FINAL 가능 여부 표시, 이력 저장.
---
SHINHWA_QMS_WORKFLOW 에서 `scripts/qms_workflow.py` 를 사용한다. 규칙은 00_CONFIG/*.yaml.

순서:
1. 신규 문서 검색 — `python3 scripts/qms_workflow.py scan`
2~8. 검사/보고서/수정후보/승인대기 분리 — `python3 scripts/qms_workflow.py run`
   (문서번호, Rev, 관련 문서 링크, ISO/IATF 검사 → 02_REVIEW/자동검토결과 JSON·요약표 → 03_EDIT/수정중 수정후보 → 통과 문서는 04_APPROVAL/승인대기)
9. FINAL 가능 여부 — `python3 scripts/qms_workflow.py status` (요약표의 "FINAL 이동" 행도 참고)
10. 이력 — 99_LOG/workflow_log.csv, error_log.csv, revision_history.csv 자동 기록

결과는 문서별 표(검사 | 결과 | 조치)로 사용자에게 보고한다.
규칙: 원본 삭제/덮어쓰기 금지, 수정본은 새 파일, 문서번호 불일치 시 FINAL 금지, 승인 전 배포본 금지,
폐기 문서 참조는 오류, 확정되지 않은 값은 임의 생성 금지. 승인(approve/sign)은 사람이 지시할 때만 실행한다.
