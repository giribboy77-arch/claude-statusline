# claude-statusline

Claude Code용 커스텀 상태줄입니다.

```
Opus 5.5  |  high  |  myproj (main)  |  컨텍스트 6%  |  캐시 42분  |  세션 ██░░░░░░ 28%  3시간 25분 후 재설정  |  주간 ████░░░░ 46%  2일 0시간 후 재설정  |  Fable ███████░ 90%
```

- 모델 | effort | 폴더 (git 브랜치) | 컨텍스트 | 프롬프트 캐시 남은 시간 | 세션(5시간) | 주간 | 모델별 주간(Fable 등)
- 창이 좁으면 `|` 단위로 자동 줄바꿈, 5초마다 갱신

## 설치

**Windows** (PowerShell)

```powershell
irm https://raw.githubusercontent.com/giribboy77-arch/claude-statusline/main/install.ps1 | iex
```

**macOS / Linux**

```bash
curl -fsSL https://raw.githubusercontent.com/giribboy77-arch/claude-statusline/main/install.sh | bash
```

압축 파일로 받았다면 Windows는 `install.cmd` 더블클릭, macOS/Linux는 `bash install.sh`.

설치하면:
- `statusline.py`를 `~/.claude/`에 복사합니다.
- `~/.claude/settings.json`의 `statusLine` 항목만 바꾸고 나머지 설정은 그대로 둡니다.
- 기존 파일은 `*.bak-날짜시간`으로 백업합니다.
- Python 3이 필요합니다. Windows에서 없으면 winget으로 설치할지 물어봅니다.

## 참고

- 세션/주간 사용량은 Claude 구독(Pro/Max) 로그인일 때만 나옵니다.
- 모델별 주간(Fable) 사용량은 `~/.claude/.credentials.json`의 로그인 토큰으로 사용량 API를 60초마다 조회합니다. 토큰은 Anthropic API 외에는 어디에도 보내지 않습니다. macOS는 토큰이 키체인에 있어서 이 칸이 표시되지 않습니다.
- 되돌리기: `settings.json.bak-*` 백업을 `settings.json`으로 되돌리면 됩니다.
