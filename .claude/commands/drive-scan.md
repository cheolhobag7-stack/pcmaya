E 드라이브 등 로컬 폴더의 현황을 조사해 분류 키워드를 맞춘다(읽기 전용). 작업 디렉터리: `SHINHWA_QMS_WORKFLOW/`

1. 사용하는 PC 에서: `python3 scripts/qms_workflow.py drivescan "E:\"` → `12_OUTPUT/REPORTS/drivescan_*.md`
   - 파일 이름·폴더 이름만 집계한다(내용은 읽지 않음). 확장자별/최상위 폴더별 파일 수, 현재 키워드의 분류 결과, 미분류에 자주 나온 이름 토큰.
2. 보고서를 사용자가 올리거나 붙여 주면, '미분류 토큰'이 어느 모듈인지 사용자와 확인한 뒤 `00_CONFIG/integrated_rules.yaml` 의 `input_sync.keywords` 에 추가한다. 모듈을 임의로 추정해 넣지 않는다.
3. 조정 후 `organizeplan`/`inputsync` 미리보기로 분류 결과를 다시 확인한다. 분류 규칙: 가까운 상위 폴더 이름 → 파일명 → 상위 폴더 전체 순으로 '한 모듈'만 맞을 때 확정, 여러 모듈이면 미분류.
