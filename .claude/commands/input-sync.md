로컬 폴더의 현장 파일을 모듈별로 `11_INPUT` 에 복사한다. 작업 디렉터리: `SHINHWA_QMS_WORKFLOW/`

1. 미리보기(기본, 복사 안 함): `python3 scripts/qms_workflow.py inputsync "<로컬폴더>"` (예: `E:\`)
2. 목록을 확인하고(모듈 분류, 여러 모듈에 걸림, 미분류) 사용자가 승인하면: `python3 scripts/qms_workflow.py inputsync "<로컬폴더>" --apply`
3. 원본 폴더는 읽기만 한다(수정·삭제·이동 없음). 같은 내용은 건너뛰고 같은 이름·다른 내용은 `_vN` 으로 저장한다. 분류 키워드는 `00_CONFIG/integrated_rules.yaml` 의 `input_sync`.
4. 복사 후 `/integrated-audit` 으로 모듈 점검을 실행한다.
