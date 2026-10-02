# SHINHWA QMS Claude Code Workflow v0.4

## v0.4 추가 기능
- 자동 수정 제안서 생성
- 안전한 AUTO_DRAFT 배치 생성
- 원본 ↔ 수정본 변경점(diff) 보고
- 승인대기 패키지 자동 생성
- 전체 사이클 명령 `/qms-full-cycle`

## 핵심 명령
```text
/qms-full-audit
/qms-autofix-plan
/qms-create-drafts
/qms-diff
/qms-approval-package
/qms-full-cycle
```

## 권장 흐름
1. `01_ORIGINAL`에 원본 투입
2. `/qms-full-audit`
3. `/qms-autofix-plan`
4. `/qms-create-drafts`
5. `03_EDIT/AUTO_DRAFT`에서 수정
6. `/qms-diff`
7. `/qms-full-audit`
8. `/qms-approval-package`
9. 승인 후에만 FINAL 처리

## 중요 안전장치
- 원본 파일은 자동으로 수정하지 않음
- AUTO_DRAFT는 승인 전 배포 금지
- 불명확한 값은 자동입력하지 않음
- Release Gate FAIL 시 FINAL 금지
