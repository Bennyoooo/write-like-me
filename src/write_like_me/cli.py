from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from . import __version__
from .analyze import analyze, profile_markdown
from .capture import capture
from .config import Config, load_config, save_config
from .hooks import extract_prompt
from .paths import home
from .storage import Store


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wlm", description="Local-first writing voice memory for AI agents")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="opt in and initialize local storage")
    init.add_argument("--yes", action="store_true", help="accept the local storage notice without a prompt")

    capture_parser = sub.add_parser("capture", help="capture a writing sample")
    capture_parser.add_argument("text", nargs="?", help="sample text; reads stdin when omitted")
    capture_parser.add_argument("--source", default="manual")
    capture_parser.add_argument("--channel", choices=("typed", "spoken", "imported"), default="typed")
    capture_parser.add_argument("--quiet", action="store_true")

    hook = sub.add_parser("hook", help="capture a prompt from an agent hook on stdin")
    hook.add_argument("--agent", default="auto")

    profile = sub.add_parser("profile", help="show the learned voice profile")
    profile.add_argument("--json", action="store_true", dest="as_json")

    context = sub.add_parser("context", help="print agent-ready writing instructions")
    context.add_argument("--json", action="store_true", dest="as_json")

    sub.add_parser("status", help="show capture state and sample count")
    sub.add_parser("pause", help="stop capturing new samples")
    sub.add_parser("resume", help="resume capturing new samples")

    export = sub.add_parser("export", help="export redacted samples and profile as JSON")
    export.add_argument("path", type=Path)

    forget = sub.add_parser("forget", help="delete all learned samples")
    forget.add_argument("--yes", action="store_true")
    return parser


def _profile() -> dict[str, object]:
    return analyze(Store().texts())


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "init":
        if not args.yes:
            print(f"Write Like Me stores redacted prompts locally in {home()}.")
            if input("Enable capture? [y/N] ").strip().lower() not in {"y", "yes"}:
                print("Not enabled.")
                return 1
        config = load_config()
        config.initialized = True
        config.enabled = True
        save_config(config)
        Store().connect().close()
        print(f"Capture enabled. Data stays in {home()}.")
        return 0
    if args.command == "capture":
        text = args.text if args.text is not None else sys.stdin.read()
        result = capture(text, args.source, args.channel)
        if not args.quiet:
            print(result.reason)
            if result.redactions:
                print("redacted: " + ", ".join(result.redactions))
        return 0 if result.captured or result.reason in {"duplicate", "sample too short", "sample is mostly code"} else 1
    if args.command == "hook":
        try:
            text = extract_prompt(sys.stdin.read(), args.agent)
            if text:
                capture(text, source=args.agent, channel="typed")
        except Exception:
            pass
        return 0
    if args.command in {"profile", "context"}:
        profile = _profile()
        if args.as_json:
            print(json.dumps(profile, indent=2, ensure_ascii=False))
        else:
            print(profile_markdown(profile), end="")
        return 0
    if args.command == "status":
        config = load_config()
        state = "enabled" if config.enabled and config.initialized else "paused" if config.initialized else "not initialized"
        print(f"Capture: {state}\nSamples: {Store().count() if config.initialized else 0}\nData: {home()}")
        return 0
    if args.command in {"pause", "resume"}:
        config = load_config()
        if not config.initialized:
            print("Run `wlm init` first.", file=sys.stderr)
            return 1
        config.enabled = args.command == "resume"
        save_config(config)
        print("Capture resumed." if config.enabled else "Capture paused.")
        return 0
    if args.command == "export":
        store = Store()
        payload = {"version": 1, "profile": analyze(store.texts()), "samples": store.rows()}
        args.path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Exported {len(payload['samples'])} samples to {args.path}.")
        return 0
    if args.command == "forget":
        if not args.yes and input("Delete every learned sample? [y/N] ").strip().lower() not in {"y", "yes"}:
            print("Nothing deleted.")
            return 1
        print(f"Deleted {Store().clear()} samples.")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
