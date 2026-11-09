"""Verify every curated repository exists (git ls-remote over HTTPS, no API quota); write data/tools_verified.json."""
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
tools = yaml.safe_load((HERE / "tools_curated.yaml").read_text())


def check(t):
    r = subprocess.run(["git", "ls-remote", "--heads", f"https://github.com/{t['repo']}.git"], capture_output=True, text=True,
                       timeout=40, env={"GIT_TERMINAL_PROMPT": "0", "PATH": "/usr/bin:/bin:/opt/homebrew/bin"})
    return t["repo"], r.returncode == 0 and bool(r.stdout.strip())


with ThreadPoolExecutor(16) as ex:
    ok = dict(ex.map(check, tools))
bad = [r for r, v in ok.items() if not v]
print(len(tools), "tools,", len(bad), "unreachable:", bad)
(HERE / "data" / "tools_verified.json").write_text(json.dumps({t["repo"]: ok[t["repo"]] for t in tools}, indent=1))
