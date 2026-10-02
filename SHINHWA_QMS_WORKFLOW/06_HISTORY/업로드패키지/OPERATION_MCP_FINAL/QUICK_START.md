# QUICK START — Claude Code 최종 운영

## 1. 압축 해제 후 폴더 열기
Claude Code에서 `SHINHWA_CLAUDE_CODE_OPERATION_FINAL` 폴더를 프로젝트로 엽니다.

## 2. 최초 1회 설치
```bash
pip install -r requirements.txt
```

## 3. 파일 넣기
- QMS: `01_QMS_ORIGINAL`
- LOT: `11_INPUT/LOT`
- 안전: `11_INPUT/SAFETY`
- 설비: `11_INPUT/EQUIPMENT`
- 교육: `11_INPUT/TRAINING`
- 생산: `11_INPUT/PRODUCTION`
- 재고: `11_INPUT/INVENTORY`
- 품질: `11_INPUT/QUALITY`

## 4. 전체 운영
Claude Code:
```text
/full-operation
```

## 5. 결과 확인
- QMS: `02_QMS_REVIEW`
- 통합점검: `12_OUTPUT/REPORTS`
- 조치사항: `12_OUTPUT/ACTION_ITEMS`
- 대시보드 데이터: `12_OUTPUT/DASHBOARD_DATA`
- 주간/월간 보고: `13_MANAGEMENT`
- 심사 패키지: `14_AUDIT`
- 고객 대응: `15_CUSTOMER_RESPONSE`
- 백업: `16_BACKUP`

## 6. 권장 운영 주기
- 문서 추가/개정 시: `/qms-audit`
- 매주: `/full-operation`
- 월간 품질회의 전: `/monthly-report`
- 심사 전: 해당 audit 명령
- 고객 클레임 발생 시: `/customer-response`
- 큰 수정 전/후: `/backup-workspace`


## 7. MCP 연결
상세 절차는 `MCP_SETUP.md` 참고.

상태 확인:
```bash
claude mcp list
```

Claude Code에서:
```text
/mcp-health-check
/mcp-safe-start
```

MCP 인증:
Claude Code 세션에서 `/mcp`
