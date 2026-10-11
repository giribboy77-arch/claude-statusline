#!/usr/bin/env bash
# 한 줄 설치: curl -fsSL https://raw.githubusercontent.com/giribboy77-arch/claude-statusline/main/install.sh | bash
set -e
repo="https://raw.githubusercontent.com/giribboy77-arch/claude-statusline/main"

# 압축을 풀어 실행했으면 옆의 파일을, 한 줄 설치면 GitHub에서 받은 파일을 쓴다
here="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || true)"
if [ -z "$here" ] || [ ! -f "$here/statusline.py" ]; then
  here="$(mktemp -d)"
  for f in install.py statusline.py; do
    curl -fsSL "$repo/$f" -o "$here/$f"
  done
fi

for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(sys.version_info[0] != 3)'; then
    exec "$c" "$here/install.py"
  fi
done
echo "Python 3이 필요합니다. 설치한 뒤 다시 실행하세요." >&2
exit 1
