# SHINHWA H&T QMS WORKFLOW

## 0. 이어서 작업하는 법 (새 세션 시작 시 먼저 읽기)
상태는 모두 파일로 남아 있다(`SHINHWA_QMS_WORKFLOW/` 하위 폴더와 `99_LOG`). 대화 기억에 의존하지 말고 아래 순서로 현재 상태를 읽는다.

1. 환경: `cd SHINHWA_QMS_WORKFLOW && pip install -r requirements.txt` (PyYAML, pypdf, openpyxl(fmregister 용). PDF 변환은 LibreOffice 필요)
2. 현재 상태 확인:
   - `python3 scripts/qms_workflow.py scan` — 아직 검토하지 않은 신규 문서
   - `python3 scripts/qms_workflow.py status` — `04_APPROVAL` 문서별 FINAL 가능 여부
   - `python3 scripts/qms_workflow.py releasegate` — 종합 Release Gate (PASS/HOLD/FAIL)
   - 이력: `99_LOG/workflow_log.csv`, `revision_history.csv`, `error_log.csv`, 최신 `05_FINAL/RELEASED/최종보고서*.md`
3. 작업 진행:
   - 신규 문서를 `01_ORIGINAL/` 에 올린 뒤 `/qms-full-cycle` (승인 직전까지 자동)
   - 수정은 `03_EDIT/AUTO_DRAFT` 의 `_DRAFT` 사본을 고쳐 `03_EDIT/수정완료/` 에 `_수정본` 이름으로 저장 → `recheck`
   - 승인·배포는 사용자가 실제 승인을 확인했다고 지시한 뒤에만: `/qms-approve` → `/qms-final-release` → `/qms-final-verify` → `/qms-final-report`
4. 규칙: 원본 삭제/덮어쓰기 금지, 확정되지 않은 값(승인자·일자·번호·보존기간) 임의 생성 금지, 승인(`sign`/`APPROVED.txt`)은 사람의 지시로만. 스크립트가 같은 이름의 파일을 만들면 `_v2` 로 새로 저장한다.
5. 사용자가 올린 패키지 폴더(v0.2~FINAL)는 `SHINHWA_QMS_WORKFLOW/06_HISTORY/업로드패키지/` 에 보관 중이다(참고용, 실행에 쓰지 않음). 새 패키지가 루트에 올라오면 같은 곳으로 옮기고 필요한 기능만 `qms_workflow.py` 에 통합한다.
6. 작업이 끝나면 커밋·푸시한다(브랜치 `claude/shinhwa-qms-workflow-54alyc`). 생성된 보고서와 로그도 함께 올린다.

### 현재 미결 사항 (처리하면 이 목록에서 지운다)
- 현장작성양식(SH-FM-101~121): Rev.03(제정일·개정일 2026-09-01, 보존기간 5년, 승인완료) `sign`/`finalize` 완료 → `05_FINAL/RELEASED/SH-FM-101-121/Rev03`(이전 Rev.00 은 06_HISTORY). FM Master 는 `..._Rev03반영.xlsx` 에 반영. 남은 일: PDF/배포본 미생성(LibreOffice PC 변환), 개정이력(개정 사유) 미기록, 날짜: 사용자 지시로 통합문서(QM/QP/WI)·문서관리대장의 시행·개정·제정일을 2026-09-01 로 통일(새 파일 `MASTER_REF/..._수정본.*`, 원본 유지). 실제 승인·배포 기록(2026-09-23 승인, 배포 이력)과 일치하는지 확인 필요
- SH-FM-122 현장양식목록 작성계획: `_수정본`(승인완료 표기·제정일 2026-09-29) `sign`/`finalize` 완료 → `05_FINAL/RELEASED/SH-FM-122/Rev00`. 단 결재란 '승인' 성명·서명·일자는 비어 있음(승인자 확정 후 사람이 기재), PDF/배포본 미생성
- 공식양식 워크북(SH-FM-066~069 외 9종): `05_FINAL/RELEASED` 릴리스 완료. 단 PDF/배포본은 미생성(FM-122 도 동일)(LibreOffice 가 되는 PC 에서 변환 필요)
- 승인체크리스트의 작성자·승인자: 확정 전이라 `[확인 필요]`
- SQ mark 심사 준비(한온시스템): 필요서류 240건 리스트를 `07_AUDIT/고객심사/SQ___________260930_SH.xlsx` 에 보관(수정 금지). `sqaudit` 대조 보고서: `07_AUDIT/고객심사/SQ_필요서류_대조보고서.md`, `SQ_필요서류_번호대조.csv`. **미결**: SQ안 FM번호(`SH-FM-QP###-NN`/`SH-FM-XXX-N##` 240건)는 공식 번호체계(`SH-FM-NNN`, Master 001~100·신규 101~122)와 달라 정식 번호 배정 방식 결정 필요(번호는 사람이 확정), 기존 양식과 중복 가능 항목(예: 계측기관리대장=SH-FM-023) 확정, '관리번호'(기록번호 등) 정의·규칙 미정
- 릴리스 폴더명: 번호 범위 워크북은 파일명 전체가 문서번호 자리에 들어감 (원하는 이름 규칙 미정)

## 1. 역할
이 저장소는 (주)신화에이치앤티의 ISO 9001:2015 + IATF 16949:2016 기반 QMS 문서 검토·수정·승인·배포 준비를 위한 작업공간이다.

Claude Code는 다음 원칙을 최우선으로 따른다.

## 2. 절대 규칙
1. 원본 파일은 삭제하거나 덮어쓰지 않는다.
2. 수정본은 반드시 새 파일명 또는 별도 폴더에 생성한다.
3. 확정되지 않은 회사 정보, 승인자, 문서번호, 일자, 보존기간을 임의 생성하지 않는다.
4. 문서번호 불일치 문서는 FINAL로 이동시키지 않는다.
5. 승인 전 문서는 배포본으로 취급하지 않는다.
6. 폐기·참조금지 문서를 발견하면 오류로 기록한다.
7. 변경사항은 `SHINHWA_QMS_WORKFLOW/99_LOG/revision_history.csv`에 기록한다.
8. 자동수정 전 반드시 원본 대비 변경사항을 요약한다.
9. QMS 관련 판단은 `SHINHWA_QMS_WORKFLOW/00_CONFIG/` 의 YAML (qms_rules.yaml 등)을 우선 기준으로 한다.
10. 사용자가 별도 지시한 경우 사용자 지시가 이 문서보다 우선한다.

## 3. 문서 체계
- QM: 품질경영매뉴얼
- QP: 절차서
- WI: 작업표준서
- FM: 기록양식

회사 문서번호 접두어:
- SH-QM
- SH-QP
- SH-WI
- SH-FM

## 4. 기본 검토 항목
모든 문서는 아래 항목을 확인한다.

1. 문서번호
2. 문서명
3. 회사명
4. Rev 번호
5. 제정/개정일
6. 작성/검토/승인 상태
7. QM/QP/WI/FM 상호참조
8. 폐기 문서 참조 여부
9. ISO 9001:2015 관련성
10. IATF 16949:2016 관련성
11. APQP/PPAP/PFMEA/Control Plan/SPC/MSA 연계
12. 기록 보존기간
13. LOT 추적성
14. 페이지 번호/목차 이상 여부
15. 중복 문서 또는 중복 파일
16. 고객 요구사항 반영 여부
17. 최종 배포 가능 상태

## 5. 작업 폴더 (`SHINHWA_QMS_WORKFLOW/` 하위)
자동화 스크립트: `SHINHWA_QMS_WORKFLOW/scripts/qms_workflow.py` (명령: scan, run, recheck, approve, sign, status, gates, finalize)
- `01_ORIGINAL`: 원본
- `02_REVIEW`: 자동점검 및 검토 결과
- `03_EDIT`: 수정 작업본
- `04_APPROVAL`: 검토·승인 대기
- `05_FINAL`: 승인 후 최종본
- `06_HISTORY`: 이전 버전/변경이력
- `07_AUDIT`: 심사 자료
- `99_LOG`: 검사 및 수정 로그

## 6. 기본 처리 흐름
원본 → 자동점검 → 오류보고 → 수정본 → 재점검 → 승인대기 → 승인완료 → FINAL → 이력보관

## 7. 승인 Gate
`SHINHWA_QMS_WORKFLOW/00_CONFIG/` 의 YAML (qms_rules.yaml 등)의 AP-01~AP-04 값을 따른다.

## 8. 파일명 권장 형식
예:
- SH-QM-001_품질경영매뉴얼_Rev03.docx
- SH-QP-001_문서화된정보관리절차서_Rev00.docx
- SH-WI-001_공정작업표준서_Rev00.docx
- SH-FM-066_제품안전관리기록_Rev00.xlsx

## 9. Claude Code 작업 원칙
문서를 수정하라는 요청을 받으면:
1. 현재 파일과 규칙을 확인한다.
2. 오류/불일치 목록을 먼저 만든다.
3. 필요한 수정만 적용한다.
4. 수정본을 별도 파일로 저장한다.
5. 변경이력을 기록한다.
6. FINAL 이동 가능 여부를 PASS/HOLD/FAIL로 표시한다.

## 10. v0.2 내부 내용 검사 (qms_workflow.py 에 통합)
- DOCX는 문단/표/머리글/바닥글 텍스트를, XLSX는 시트별 셀 텍스트를 점검한다. 양식 워크북은 시트 1개 = 양식 1개로 쪼개서 검토한다.
- 파일명과 본문 문서번호/Rev가 불일치하면 FAIL 처리한다.
- SH 접두어 없는 기존 참조는 HOLD 처리한다.
- 삭제 지시된 문구(`qms_rules.yaml` 의 `prohibited_phrases`)가 발견되면 FAIL 처리한다.
- LOT 추적 관련 문서는 보존기간 3년(36개월), 목표시간 1시간(60분)을 확인한다.
- FM 양식 단계에서는 보존기간 공란을 허용한다 (허용값 외 구체값은 오류).
- `SH_` 로 시작하는 관리자료는 `01_ORIGINAL/MASTER_REF` 로 분류하며 승인 흐름 없이 상호참조 기준으로만 쓴다.

## 11. v0.3 자동감사 규칙 (qms_workflow.py 에 통합)
- PDF 본문도 검사한다 (pdftotext 우선, 없으면 pypdf). 스캔형 PDF는 자동판정하지 않고 HOLD 처리한다.
- 참조된 QM/QP/WI/FM 이 실제 프로젝트(파일, 양식 시트, 문서관리대장, FM Master)에 존재하는지 확인한다.
- 동일 문서번호의 중복 Rev와 Rev 누락을 검출하고 최신 Rev 후보를 표시한다 (crosscheck).
- 문서관리대장과 실제 파일을 양방향으로 대조한다 (ledger). 대장 위치: `01_ORIGINAL/MASTER_REF` 또는 `00_CONFIG` (파일명에 `문서관리대장`, 샘플 제외).
- FINAL 이동 전 Release Gate(G1~G8)를 반드시 통과해야 한다 (gatecheck / releasegate / finalize 자동 실행).
- 전체 자동감사: `fullaudit` (`/qms-full-audit`).

## 12. 수정 → DIFF → 재점검 → 승인 패키지 흐름
01_ORIGINAL → `fullaudit`(전체 자동감사) → 수정 필요사항 추출 → `03_EDIT/AUTO_DRAFT`(수정필요사항 목록 + `_DRAFT` 편집용 사본)
→ 사람이 수정해 `03_EDIT/수정완료` 에 저장 → `recheck`(원본↔수정본 DIFF 를 `03_EDIT/DIFF` 에 자동 생성 후 재점검)
→ Release Gate → 통과 시 `04_APPROVAL/승인대기` + `04_APPROVAL/PACKAGES/<문서>/`(문서·검토요약·DIFF·Release_Gate·승인체크리스트·STATUS)
→ 사람이 `approve`/`sign` → `finalize`(Gate 재확인, 05_FINAL, 패키지는 06_HISTORY/변경이력 에 보관)
- 원본은 수정하지 않는다. AUTO_DRAFT 사본도 자동으로 값을 채우지 않는다(확정되지 않은 값은 사람이 입력).
- 수정본 파일명 규칙: 원본 이름 뒤에 `_수정본`, `_수정본2`, `_vN` 등을 붙이면 원본과 자동 연결된다.
- 수동 실행: `diff 수정본 [원본]`, `package 파일명`.

## 13. 릴리스 기록 (05_FINAL/RELEASED)
- `finalize` 는 Gate 재확인 후 `05_FINAL/RELEASED/<문서번호>/Rev<NN>/` 에 릴리스본(문서·PDF·배포본)과 `MANIFEST.json`(SHA-256)을 저장한다. 기존 `WORD/EXCEL/PDF/배포본` 폴더도 유지한다.
- 릴리스 직후 무결성 검사를 자동 실행하고, 언제든 `integrity` 명령으로 `RELEASED` 전체를 재검사한다 (변조·누락 시 FAIL, 종료코드 1).
- 배포목록은 `05_FINAL/RELEASED/배포목록.csv` 에 누적(append)되고, 실행마다 `최종보고서.md` 가 생성된다. 기존 보고서는 덮어쓰지 않는다(`_vN`).
- 이전 Rev 의 릴리스 폴더와 구 최종본은 삭제하지 않고 `06_HISTORY/이전버전/<문서번호>/` 로 이동한다.
- PDF 변환이 불가능한 환경에서는 PDF/배포본이 생성되지 않는다.

## 14. 최종 배포 운영 규칙 (FINAL 패키지 반영)
- FINAL 배포는 Release Gate PASS + 승인 표시 파일(`APPROVED.txt`, 설정 `final_operation.approval_marker`)이 모두 충족된 경우에만 수행한다.
- `APPROVED.txt` 는 사람이 `sign`(`/qms-approve`)을 실행했을 때만 승인 패키지에 생성된다. 사용자의 실제 승인 없이 자동 생성하지 않는다.
- 기존 FINAL 동일 문서번호는 `06_HISTORY` 로 이동하며, 이동 전에 `06_HISTORY/ROLLBACK_BACKUP` 에 사본을 만든다. 롤백은 자동 실행하지 않고 `rollbackcheck` 로 후보만 제시한다.
- 배포목록(`05_FINAL/RELEASED/배포목록.csv`)·변경이력·워크플로우 로그를 기록하고, 배포 후 SHA-256 무결성 검사를 수행한다. 스냅샷은 `05_FINAL/DISTRIBUTION/` 에 저장한다.
- 명령: `/qms-approve`, `/qms-final-release`, `/qms-final-verify`, `/qms-final-report`, `/qms-rollback-check`, `/qms-diff`, `/qms-approval-package`, `/qms-autofix-plan`, `/qms-create-drafts`, `/qms-full-cycle`.
