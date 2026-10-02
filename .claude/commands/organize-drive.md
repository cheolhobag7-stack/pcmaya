로컬 드라이브(예: E:\)의 파일을 표준 폴더 구조로 정리한다(복사). 작업 디렉터리: `SHINHWA_QMS_WORKFLOW/`

1. 표준 폴더 만들기: `python3 scripts/qms_workflow.py foldertree "E:\SHINHWA"`
   (00_QMS문서, 01_LOT추적, 02_안전, 03_설비, 04_교육, 05_생산, 06_재고, 07_품질, 08_SQ심사, 09_고객대응(한온시스템), 99_미분류_확인필요)
2. 미리보기(복사 안 함): `python3 scripts/qms_workflow.py organizeplan "<정리할폴더>" "E:\SHINHWA"` → `12_OUTPUT/REPORTS/organize_plan_*.csv` 를 사용자와 함께 확인
3. 승인 후 복사: 같은 명령에 `--apply`. **원본은 이동·삭제하지 않는다.** 복사본을 확인한 뒤 원본 정리는 사람이 한다.
4. `99_미분류_확인필요` 는 사람이 직접 분류한다(키워드는 `00_CONFIG/integrated_rules.yaml` 의 `drive_layout`, `input_sync`).
5. 정리 후 `/input-sync "E:\SHINHWA"` 로 현장 데이터를 `11_INPUT` 에 복사한다.
