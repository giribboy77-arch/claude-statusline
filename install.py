"""Claude Code 커스텀 상태줄 설치: statusline.py를 설정 폴더에 복사하고 settings.json의 statusLine을 등록한다."""
import json, os, shutil, sys, time

here = os.path.dirname(os.path.abspath(__file__))
cfg_dir = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")
os.makedirs(cfg_dir, exist_ok=True)
stamp = time.strftime("%Y%m%d-%H%M%S")

def backup(path):
    if os.path.exists(path):
        dst = f"{path}.bak-{stamp}"
        shutil.copy2(path, dst)
        print(f"  백업: {dst}")

# 1) 스크립트 복사
script = os.path.join(cfg_dir, "statusline.py")
backup(script)
shutil.copy2(os.path.join(here, "statusline.py"), script)
print(f"  복사: {script}")

# 2) settings.json에 statusLine 등록 (다른 설정은 그대로 둔다)
settings_path = os.path.join(cfg_dir, "settings.json")
settings = {}
if os.path.exists(settings_path):
    with open(settings_path, encoding="utf-8-sig") as f:
        text = f.read().strip()
    if text:
        try:
            settings = json.loads(text)
        except ValueError as e:
            sys.exit(f"settings.json을 읽을 수 없습니다({e}). 파일을 고친 뒤 다시 실행하세요.")
backup(settings_path)

# 셸(bash/cmd)에 상관없이 동작하도록 인터프리터와 스크립트를 절대경로로 지정
py = sys.executable.replace("\\", "/")
settings["statusLine"] = {
    "type": "command",
    "command": f'"{py}" "{script.replace(chr(92), "/")}"',
    "refreshInterval": 5,
}
with open(settings_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(settings, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(f"  설정: {settings_path}")
print(f"  명령: {settings['statusLine']['command']}")
print("\n완료. Claude Code에서 메시지를 하나 보내면(또는 5초 안에) 새 상태줄이 보입니다.")
