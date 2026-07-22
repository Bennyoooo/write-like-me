#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path


AGENTS = ("codex", "claude", "opencode", "gemini", "cursor")
ROOT = Path(__file__).resolve().parents[1]


def state_home() -> Path:
    if value := os.environ.get("WLM_HOME"):
        return Path(value).expanduser()
    if value := os.environ.get("XDG_STATE_HOME"):
        return Path(value).expanduser() / "write-like-me"
    return Path.home() / ".write-like-me"


def executable(name: str) -> str | None:
    return shutil.which(name)


def detected(agent: str) -> bool:
    if executable(agent):
        return True
    if agent == "cursor":
        return (Path.home() / ".cursor").exists() or Path("/Applications/Cursor.app").exists()
    if agent == "opencode":
        config_home = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
        return (config_home / "opencode").exists()
    return False


def run(command: list[str], *, tolerate_failure: bool = False) -> bool:
    print("+ " + " ".join(command))
    result = subprocess.run(command, check=False)
    if result.returncode and not tolerate_failure:
        raise RuntimeError(f"Command failed with exit code {result.returncode}: {' '.join(command)}")
    return result.returncode == 0


def install_runtime(yes: bool) -> Path:
    home = state_home()
    runtime = home / "runtime"
    home.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        home.chmod(0o700)
    except OSError:
        pass
    if not runtime.exists():
        print(f"Creating private runtime at {runtime}")
        venv.EnvBuilder(with_pip=True).create(runtime)
    python = runtime / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    wlm = runtime / ("Scripts/wlm.exe" if os.name == "nt" else "bin/wlm")
    run([str(python), "-m", "pip", "install", "--quiet", "--upgrade", str(ROOT)])
    if yes:
        run([str(wlm), "init", "--yes"])
    else:
        run([str(wlm), "init"])
    return wlm


def install_codex() -> None:
    command = executable("codex")
    if not command:
        print("skip codex: command not found")
        return
    run([command, "plugin", "marketplace", "add", str(ROOT)], tolerate_failure=True)
    run([command, "plugin", "add", "write-like-me@write-like-me"], tolerate_failure=True)


def install_claude() -> None:
    command = executable("claude")
    if not command:
        print("skip claude: command not found")
        return
    run([command, "plugin", "marketplace", "add", str(ROOT)], tolerate_failure=True)
    run([command, "plugin", "install", "write-like-me@write-like-me", "--scope", "user"], tolerate_failure=True)


def install_gemini() -> None:
    command = executable("gemini")
    if not command:
        print("skip gemini: command not found")
        return
    run([command, "extensions", "link", str(ROOT / "adapters/gemini")], tolerate_failure=True)


def install_opencode() -> None:
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    target = config_home / "opencode/plugins/write-like-me.js"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "adapters/opencode/write-like-me.js", target)
    skill_target = config_home / "opencode/skills/write-like-me"
    if skill_target.exists():
        shutil.rmtree(skill_target)
    shutil.copytree(ROOT / "plugins/write-like-me/skills/write-like-me", skill_target)
    print(f"installed opencode adapter: {target}")
    print(f"installed opencode skill: {skill_target}")


def install_cursor() -> None:
    target = Path.home() / ".cursor/hooks.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    current: dict[str, object] = {}
    if target.exists():
        try:
            current = json.loads(target.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError(f"Cannot safely merge invalid JSON at {target}: {error}") from error
    current["version"] = 1
    hooks = current.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise RuntimeError(f"Cannot safely merge non-object hooks at {target}")
    entries = hooks.setdefault("beforeSubmitPrompt", [])
    if not isinstance(entries, list):
        raise RuntimeError(f"Cannot safely merge non-array beforeSubmitPrompt at {target}")
    hook = {
        "command": f"{state_home() / 'runtime/bin/wlm'} hook --agent cursor",
        "timeout": 5,
        "failClosed": False,
    }
    entries[:] = [entry for entry in entries if not (isinstance(entry, dict) and "wlm hook --agent cursor" in str(entry.get("command", "")))]
    entries.append(hook)
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
    temporary.replace(target)
    skill_target = Path.home() / ".cursor/skills/write-like-me"
    if skill_target.exists():
        shutil.rmtree(skill_target)
    shutil.copytree(ROOT / "plugins/write-like-me/skills/write-like-me", skill_target)
    print(f"merged cursor hook: {target}")
    print(f"installed cursor skill: {skill_target}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install Write Like Me for one or more AI agents")
    parser.add_argument("--agent", action="append", choices=("all", "auto", *AGENTS), default=[])
    parser.add_argument("--yes", action="store_true", help="explicitly accept local prompt capture without an interactive prompt")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    selected = args.agent or ["auto"]
    wlm = install_runtime(args.yes)
    if "all" in selected:
        selected_agents = list(AGENTS)
    elif "auto" in selected:
        selected_agents = [agent for agent in AGENTS if detected(agent)]
    else:
        selected_agents = list(dict.fromkeys(selected))
    installers = {
        "codex": install_codex,
        "claude": install_claude,
        "opencode": install_opencode,
        "gemini": install_gemini,
        "cursor": install_cursor,
    }
    for agent in selected_agents:
        installers[agent]()
    print("\nInstalled for: " + ", ".join(selected_agents))
    print(f"Run `{wlm} status` to inspect capture state.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError) as error:
        print(f"install failed: {error}", file=sys.stderr)
        raise SystemExit(1)
