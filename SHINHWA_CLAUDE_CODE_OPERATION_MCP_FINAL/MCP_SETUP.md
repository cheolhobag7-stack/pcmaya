# MCP_SETUP — Claude Code 연동 최종 가이드

## 1. 적용 원칙

이 프로젝트는 MCP를 선택적으로 연결하도록 구성한다.

권장 우선순위:
1. Google Drive 또는 회사 문서 저장소
2. Gmail 또는 업무메일
3. Google Calendar
4. Notion/업무관리 도구
5. GitHub(자동화 스크립트 버전관리 시)

주의:
- 연결하지 않은 MCP가 있어도 로컬 QMS 자동화는 정상 운영 가능하다.
- 실제 MCP 공급자/URL/패키지는 사용자가 선택한 서비스에 맞춰 등록한다.
- API Key, OAuth Token, Client Secret은 `.mcp.json`에 직접 기록하지 않는다.
- 민감정보는 환경변수 또는 MCP 공급자의 OAuth 인증 흐름을 사용한다.

## 2. Claude Code MCP 상태 확인

터미널:

```bash
claude mcp list
```

특정 서버:

```bash
claude mcp get <server-name>
```

Claude Code 대화형 세션:

```text
/mcp
```

## 3. MCP Scope

### local
현재 프로젝트 + 현재 사용자에게만 저장.

```bash
claude mcp add <server-name> --scope local <command>
```

개인 인증정보가 포함되는 연결은 local 권장.

### project
프로젝트 루트의 `.mcp.json`에 저장되고 프로젝트 구성원과 공유 가능.

```bash
claude mcp add <server-name> --scope project <command>
```

프로젝트 공용 서버 구성에 적합.

### user
현재 PC의 모든 Claude Code 프로젝트에서 사용.

```bash
claude mcp add <server-name> --scope user <command>
```

## 4. 원격 HTTP MCP

공급자가 공식 MCP URL을 제공하는 경우 해당 공급자의 안내에 따라 등록한다.
OAuth 인증이 필요한 서버는 Claude Code에서 `/mcp`를 열어 인증한다.

민감 URL/토큰을 공유 프로젝트 파일에 하드코딩하지 않는다.

## 5. Windows 주의사항

Windows 네이티브에서 `npx` 기반 로컬 MCP 서버는 다음 형태가 필요할 수 있다.

```bash
claude mcp add my-server -- cmd /c npx -y @your-mcp/package
```

WSL을 사용하는 경우 Linux 방식으로 설정한다.

## 6. 신화 운영에서 권장하는 연결 역할

### Drive / 문서저장소
용도:
- 최신 QMS 승인본 조회
- 문서관리대장 조회
- LOT 관련 증빙 조회
- 심사 자료 수집

원칙:
- 처음에는 READ 권한 위주
- 자동 수정/삭제 권한은 연결 안정화 후 검토

### Gmail / 업무메일
용도:
- 고객사 요청 메일 검색
- 심사 요청사항 파악
- 품질 클레임 관련 자료 확인

원칙:
- 최초에는 검색/읽기 중심
- 자동 발송은 별도 승인 절차 유지

### Calendar
용도:
- 심사 일정
- 품질회의
- 개선 완료기한 확인

### Notion / 업무관리
용도:
- HOLD/FAIL Action Item 추적
- 개선과제 상태 관리

### GitHub
용도:
- Claude Code 스크립트 버전관리
- 변경이력 및 롤백

## 7. 연결 확인 체크리스트

- `claude mcp list`에 서버 표시
- 상태가 정상 연결
- `/mcp`에서 인증 상태 확인
- Claude에게 해당 서버의 리소스 1개만 읽도록 테스트
- 수정/삭제 권한은 아직 사용하지 않음
- 로그에 민감정보가 출력되지 않는지 확인

## 8. 프로젝트 `.mcp.json`

이 패키지에는 `.mcp.json.example`만 포함되어 있다.
실제 서버를 선택한 뒤:

1. `.mcp.json.example`을 참고한다.
2. `claude mcp add ... --scope project` 명령 사용을 우선한다.
3. Claude Code가 생성한 `.mcp.json`을 확인한다.
4. 토큰/비밀번호가 파일에 기록되지 않았는지 확인한다.

## 9. 운영 시작 순서

MCP 연결 전:
`/full-operation`

MCP 연결 후:
`/mcp-health-check`
→ `/full-operation`
→ 필요할 때 외부 문서/메일/일정 조회

MCP 장애가 발생해도 로컬 QMS 작업은 중단하지 않는다.
