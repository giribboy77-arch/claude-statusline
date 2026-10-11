# 한 줄 설치: irm https://raw.githubusercontent.com/giribboy77-arch/claude-statusline/main/install.ps1 | iex
# (iex로 실행되면 exit가 창을 닫으므로 전체를 블록으로 감싸고 return으로 빠져나온다)
& {
    $ErrorActionPreference = 'Stop'
    $repo = 'https://raw.githubusercontent.com/giribboy77-arch/claude-statusline/main'

    function Find-Python {
        # Microsoft Store의 가짜 python(실행 별칭)은 걸러내려고 실제로 실행해 본다
        foreach ($c in @(@('py', '-3'), @('python'), @('python3'))) {
            try {
                $out = & $c[0] @($c | Select-Object -Skip 1) -c "import sys; print(sys.version_info[0])" 2>$null
                if ($LASTEXITCODE -eq 0 -and "$out".Trim() -eq '3') { return ,$c }
            } catch {}
        }
        return $null
    }

    Write-Host "Claude Code 상태줄 설치" -ForegroundColor Cyan

    # 압축을 풀어 실행했으면 옆의 파일을, 한 줄 설치면 GitHub에서 받은 파일을 쓴다
    $here = if ($PSCommandPath) { Split-Path -Parent $PSCommandPath } else { $null }
    if (-not $here -or -not (Test-Path (Join-Path $here 'statusline.py'))) {
        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor 3072
        $here = Join-Path ([IO.Path]::GetTempPath()) "claude-statusline-$PID"
        New-Item -ItemType Directory -Force $here | Out-Null
        foreach ($f in 'install.py', 'statusline.py') {
            Invoke-WebRequest "$repo/$f" -OutFile (Join-Path $here $f) -UseBasicParsing
        }
    }

    $py = Find-Python
    if (-not $py) {
        Write-Host "Python 3이 없습니다. 상태줄 스크립트 실행에 필요합니다." -ForegroundColor Yellow
        if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
            Write-Host "https://www.python.org/downloads/ 에서 Python을 설치한 뒤 다시 실행하세요."
            return
        }
        $ans = Read-Host "winget으로 Python 3.12를 설치할까요? (Y/n)"
        if ($ans -and $ans -notmatch '^[Yy]') { return }
        winget install -e --id Python.Python.3.12 --scope user --accept-source-agreements --accept-package-agreements
        # 새로 설치된 Python이 보이도록 PATH를 다시 읽는다
        $env:Path = [Environment]::GetEnvironmentVariable('Path', 'User') + ';' + [Environment]::GetEnvironmentVariable('Path', 'Machine')
        $py = Find-Python
        if (-not $py) {
            Write-Host "Python을 찾지 못했습니다. 새 터미널에서 다시 실행해 보세요." -ForegroundColor Red
            return
        }
    }

    & $py[0] @($py | Select-Object -Skip 1) (Join-Path $here 'install.py')
}
