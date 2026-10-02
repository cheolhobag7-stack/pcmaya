MCP 상태와 보안을 점검한다(읽기 전용). 작업 디렉터리: `SHINHWA_QMS_WORKFLOW/`

1. `python3 scripts/qms_workflow.py mcphealth` → `12_OUTPUT/REPORTS/mcp_health_*.md`
   - `claude mcp list` 상태, 프로젝트 `.mcp.json` 의 비밀값 직접 기재, `.gitignore`, 추적 중인 민감 파일·저장소 내 비밀값 패턴, 로컬 QMS 자동화 독립 동작
2. 결과를 PASS/WARN/FAIL 로 요약한다. MCP 가 없거나 장애여도 로컬 QMS 작업은 중단하지 않는다.
3. 점검 중 MCP 로 수정·삭제·전송·승인은 하지 않는다(LEVEL 1 읽기만). 정책: `17_MCP/MCP_SECURITY_POLICY.md`.
