import json, sys, io, time, os, re, subprocess, tempfile, unicodedata, urllib.request
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

RST = "\033[0m"
BLD = "\033[1m"
DIM = "\033[2m"
GRN = "\033[32m"
YLW = "\033[33m"
RED = "\033[31m"
CYN = "\033[36m"
MGN = "\033[35m"
BLU = "\033[34m"

USAGE_URL = "https://api.anthropic.com/api/oauth/usage"
USAGE_CACHE = os.path.join(tempfile.gettempdir(), "claude_statusline_usage.json")
USAGE_TTL = 60

def pct_color(pct, lo=50, hi=80):
    return GRN if pct < lo else (YLW if pct < hi else RED)

def time_color(diff_sec):
    if diff_sec < 3600:
        return RED
    if diff_sec < 7200:
        return YLW
    return CYN

def gauge(pct, width=8):
    filled = round(width * pct / 100)
    c = pct_color(pct)
    return f"{c}{'█' * filled}{DIM}{'░' * (width - filled)}{RST}"

def fmt_korean(resets_at):
    """반환: (시간 숫자 부분, 접미사 문자열, diff 초)"""
    if not resets_at:
        return None, None, 0
    diff = int(resets_at) - int(time.time())
    if diff <= 0:
        return "곧", "재설정", 0
    days, h, m = diff // 86400, (diff % 86400) // 3600, (diff % 3600) // 60
    if days > 0:
        return f"{days}일 {h}시간", "후 재설정", diff
    if h > 0:
        return f"{h}시간 {m}분", "후 재설정", diff
    return f"{m}분", "후 재설정", diff

def limit_seg(label, pct, resets_at=None):
    pct = round(pct)
    seg = f"{DIM}{label}{RST} {gauge(pct)} {BLD}{pct_color(pct)}{pct}%{RST}"
    num, suffix, diff = fmt_korean(resets_at)
    if num:
        seg += f"  {time_color(diff)}{num}{RST} {DIM}{suffix}{RST}"
    return seg

def to_epoch(iso):
    try:
        return int(datetime.fromisoformat(iso).timestamp())
    except (TypeError, ValueError):
        return None

def fetch_model_limits():
    """모델별 주간 한도(예: Fable). 상태줄 입력에는 없어서 사용량 API를 직접 조회하고 USAGE_TTL초 캐시한다."""
    try:
        with open(USAGE_CACHE, encoding="utf-8") as f:
            cache = json.load(f)
    except (OSError, ValueError):
        cache = {}
    limits = cache.get("limits", [])
    if time.time() - cache.get("at", 0) < USAGE_TTL:
        return limits
    try:
        cfg_dir = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
        with open(os.path.join(cfg_dir, ".credentials.json"), encoding="utf-8") as f:
            token = json.load(f)["claudeAiOauth"]["accessToken"]
        req = urllib.request.Request(USAGE_URL, headers={
            "Authorization": f"Bearer {token}",
            "anthropic-beta": "oauth-2025-04-20",
        })
        with urllib.request.urlopen(req, timeout=3) as r:
            data = json.load(r)
        limits = []
        for lim in data.get("limits") or []:
            name = (((lim.get("scope") or {}).get("model")) or {}).get("display_name")
            if lim.get("kind") == "weekly_scoped" and name and lim.get("percent") is not None:
                limits.append({"name": name, "pct": lim["percent"], "resets_at": to_epoch(lim.get("resets_at"))})
    except Exception:
        pass  # 실패하면 직전 값을 그대로 쓰고, TTL 동안은 다시 시도하지 않는다
    try:
        with open(USAGE_CACHE, "w", encoding="utf-8") as f:
            json.dump({"at": time.time(), "limits": limits}, f)
    except OSError:
        pass
    return limits

def git_branch(path):
    try:
        r = subprocess.run(["git", "-C", path, "branch", "--show-current"],
                           capture_output=True, encoding="utf-8", errors="replace", timeout=1)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    return r.stdout.strip() or None

def cache_seg(pc):
    """프롬프트 캐시 만료까지 남은 시간. 만료 후 다음 요청은 대화 전체를 다시 캐시한다."""
    if not pc.get("caching_observed"):
        return None
    left = int(pc.get("expires_at") or 0) - int(time.time())
    if not pc.get("warm") or left <= 0:
        return f"{DIM}캐시{RST} {RED}만료{RST}"
    m = left // 60
    c = GRN if m >= 10 else (YLW if m >= 3 else RED)
    return f"{DIM}캐시{RST} {c}{m}분{RST}" if m > 0 else f"{DIM}캐시{RST} {c}{left}초{RST}"

raw = sys.stdin.buffer.read().decode("utf-8-sig", errors="replace")
d = json.loads(raw)

model = d.get("model", {}).get("display_name", "?")
ctx_pct = d.get("context_window", {}).get("used_percentage")

rl = d.get("rate_limits") or {}
fh = rl.get("five_hour") or {}
five_pct, five_reset = fh.get("used_percentage"), fh.get("resets_at")
sd = rl.get("seven_day") or {}
week_pct, week_reset = sd.get("used_percentage"), sd.get("resets_at")

effort = (d.get("effort") or {}).get("level")

parts = [f"{BLD}{CYN}{model}{RST}"]

if effort:
    parts.append(f"{MGN}{effort}{RST}")

cur_dir = (d.get("workspace") or {}).get("current_dir") or d.get("cwd")
if cur_dir:
    seg = f"{BLU}{os.path.basename(cur_dir.rstrip(chr(92) + '/')) or cur_dir}{RST}"
    branch = git_branch(cur_dir)
    if branch:
        seg += f" {DIM}({RST}{GRN}{branch}{RST}{DIM}){RST}"
    parts.append(seg)

if ctx_pct is not None:
    ctx_pct = round(ctx_pct)
    parts.append(f"{DIM}컨텍스트{RST} {pct_color(ctx_pct)}{ctx_pct}%{RST}")

cseg = cache_seg(d.get("prompt_cache") or {})
if cseg:
    parts.append(cseg)

if five_pct is not None:
    parts.append(limit_seg("세션", five_pct, five_reset))

if week_pct is not None:
    parts.append(limit_seg("주간", week_pct, week_reset))

if rl:
    for lim in fetch_model_limits():
        # 주간 전체와 재설정 시각이 같으면 시간 표시는 생략
        same_reset = week_reset and lim["resets_at"] and abs(lim["resets_at"] - week_reset) < 60
        parts.append(limit_seg(lim["name"], lim["pct"], None if same_reset else lim["resets_at"]))

ANSI_RE = re.compile(r"\033\[[0-9;]*m")
SEP = f"  {DIM}|{RST}  "

def vis_width(s):
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in ANSI_RE.sub("", s))

# 터미널 너비(COLUMNS)를 넘으면 | 단위로 다음 줄로 넘긴다
try:
    width = int(os.environ["COLUMNS"]) - 4
except (KeyError, ValueError):
    width = None

lines = [parts[0]]
for p in parts[1:]:
    cand = lines[-1] + SEP + p
    if width and vis_width(cand) > width:
        lines.append(p)
    else:
        lines[-1] = cand

print("\n".join(lines), end="")
