# SHINHWA QMS Claude Code Workflow — FINAL

이 패키지는 (주)신화에이치앤티의 ISO 9001:2015 + IATF 16949:2016 QMS 문서 운영을 위한 최종 워크플로우입니다.

## 전체 흐름
원본 → 자동감사 → 수정제안 → AUTO_DRAFT → 변경비교 → 재감사 → 승인대기패키지 → 승인 → FINAL 배포 → 무결성검사 → 배포보고

## 주요 명령
```text
/qms-full-audit
/qms-autofix-plan
/qms-create-drafts
/qms-diff
/qms-approval-package
/qms-approve
/qms-final-release
/qms-final-verify
/qms-final-report
/qms-rollback-check
/qms-full-cycle
```

## 설치
```bash
pip install -r requirements.txt
```

## 가장 권장하는 사용법
```text
/qms-full-cycle
```

단, 승인 단계에서는 반드시 사용자의 실제 승인 후 `/qms-approve`를 실행합니다.

## FINAL 배포 조건
- Release Gate PASS
- 승인대기 패키지 존재
- APPROVED.txt 존재
- 문서번호/Rev 검증 완료
- HOLD/FAIL 없음

## 자동 보호 기능
- 원본 덮어쓰기 금지
- 승인 전 배포 금지
- 기존 FINAL 자동 아카이브
- 롤백 백업 생성
- revision_history.csv 자동기록
- workflow_log.csv 자동기록
- 배포목록 자동생성
- SHA-256 무결성 검사
- 최종 배포 보고서 자동생성

## 주요 폴더
- `01_ORIGINAL` : 원본
- `02_REVIEW` : 검사/DIFF
- `03_EDIT/AUTO_DRAFT` : 수정초안
- `04_APPROVAL/PACKAGES` : 승인대기
- `05_FINAL/RELEASED` : 최종 승인본
- `05_FINAL/DISTRIBUTION` : 배포목록/보고
- `06_HISTORY/ARCHIVE` : 이전 Rev
- `06_HISTORY/ROLLBACK_BACKUP` : 롤백 백업
- `99_LOG` : 운영 이력

## 중요
이 시스템은 문서 운영 자동화를 지원하지만, QMS 승인 자체를 자동으로 대체하지 않습니다.
최종 승인 책임은 사내 승인 절차와 실제 승인권자에게 있습니다.
