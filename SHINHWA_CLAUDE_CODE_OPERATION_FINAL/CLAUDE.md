# SHINHWA H&T — CLAUDE CODE OPERATING SYSTEM

## 1. 목적
(주)신화에이치앤티의 QMS, LOT 추적성, 안전, 설비, 교육, 생산, 재고, 품질관리 업무를 Claude Code에서 일관되게 운영한다.

## 2. 절대 규칙
1. 원본 파일을 삭제하거나 덮어쓰지 않는다.
2. 수정 전 반드시 복사본 또는 별도 작업본을 만든다.
3. 확정되지 않은 승인자/일자/문서번호/수치를 임의 생성하지 않는다.
4. 승인 전 문서를 FINAL 또는 배포본으로 취급하지 않는다.
5. HOLD/FAIL 항목이 있으면 최종 배포 또는 심사 제출을 막는다.
6. 이전 Rev와 변경이력을 유지한다.
7. 모든 자동검사 결과는 로그 또는 결과 파일로 남긴다.
8. 실제 승인 책임은 회사의 승인권자에게 있다.

## 3. 주요 운영 영역
- QMS
- LOT 추적
- 위험성평가/안전
- 설비 트라이얼
- 교육일지
- 생산관리
- 재고관리
- 품질실적
- 주간/월간 경영보고
- 내부/고객/인증 심사 준비
- 고객사 대응
- 백업

## 4. 기본 명령
가장 먼저 `/full-operation`을 사용한다.

세부 명령:
- `/qms-audit`
- `/integrated-audit`
- `/collect-actions`
- `/dashboard-data`
- `/weekly-report`
- `/monthly-report`
- `/audit-internal`
- `/audit-customer`
- `/audit-certification`
- `/customer-response`
- `/backup-workspace`

## 5. QMS 기준
문서번호:
- SH-QM
- SH-QP
- SH-WI
- SH-FM

기준:
- ISO 9001:2015
- IATF 16949:2016

고객사:
- 한온시스템

LOT 기준:
- 보존기간 3년
- 목표 추적시간 1시간

## 6. 운영 원칙
사용자가 새 파일을 넣으면 적절한 입력 폴더에 분류하고 점검한다.
검사결과는 PASS/HOLD/FAIL로 구분한다.
HOLD/FAIL은 조치목록으로 모은다.
수정이 필요한 경우 원본이 아닌 작업본만 수정한다.
