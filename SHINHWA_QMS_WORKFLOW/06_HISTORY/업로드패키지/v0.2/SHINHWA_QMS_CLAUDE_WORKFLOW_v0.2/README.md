# SHINHWA QMS Claude Code Workflow v0.2

## v0.2 핵심 기능
- 파일명 문서번호/Rev 검사
- DOCX 내부 텍스트 검사
- XLSX/XLSM 내부 셀 텍스트 검사
- 파일명 ↔ 본문 문서번호 비교
- 파일명 ↔ 본문 Rev 비교
- 회사명 확인
- 고객사 표기 확인
- LOT 추적 보존기간 3년 확인
- LOT 추적 목표시간 1시간 확인
- 삭제 지시 문구 검출
- QM/QP/WI/FM 상호참조 추출
- SH 접두어 미적용 참조 검출
- CSV + Markdown 요약 리포트 생성

## 설치
Claude Code 프로젝트 폴더에서:

```bash
pip install -r requirements.txt
```

## 실행
Claude Code:
- `/qms-review`
- `/qms-crosscheck`
- `/qms-final-check`
- `/qms-release`
- `/qms-history`

직접 실행:
```bash
python scripts/qms_review.py
python scripts/qms_content_review.py
```

## 사용 순서
1. 검토할 DOCX/XLSX/XLSM/TXT/MD 파일을 `01_ORIGINAL`에 넣기
2. `/qms-review`
3. `02_REVIEW`의 CSV/MD 확인
4. HOLD/FAIL 문서는 `03_EDIT`에서 수정
5. 재점검
6. 승인 완료 후 `05_FINAL`

## 주의
PDF 내부본문 검사는 v0.3에서 추가 권장.
현재 v0.2는 DOCX/XLSX 중심이다.
