QMS + 현장 모듈 통합 점검. 작업 디렉터리: `SHINHWA_QMS_WORKFLOW/`

`python3 scripts/qms_workflow.py integratedaudit` → `12_OUTPUT/REPORTS/integrated_audit_*.csv/md` (모듈별 `*_check_*.csv`). 입력: `11_INPUT/{LOT,SAFETY,EQUIPMENT,TRAINING,PRODUCTION,INVENTORY,QUALITY}`. 단일 모듈: `modulecheck <lot|safety|equipment|training|production|inventory|quality>`.
