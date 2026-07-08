#!/usr/bin/env python3
"""CI validator for claude-agent-archetypes. Not a shipped tool; CI infrastructure only."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def frontmatter(text: str) -> str:
    parts = text.split("---")
    return parts[1] if len(parts) >= 3 else ""


def tools_of(fm: str) -> list[str]:
    tools: list[str] = []
    lines = fm.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"\s*tools:\s*(.*)$", line)
        if not m:
            continue
        inline = m.group(1).strip()
        if inline:
            tools = [t.strip() for t in inline.split(",") if t.strip()]
        else:
            for nxt in lines[i + 1:]:
                item = re.match(r"\s*-\s*(\S+)", nxt)
                if item:
                    tools.append(item.group(1).strip())
                elif nxt.strip() and not nxt.startswith((" ", "\t")):
                    break
        break
    return tools


def check_unique_names(root: Path) -> list[str]:
    errs: list[str] = []
    for d in ("code-agents", "knowledge-agents"):
        seen: dict[str, str] = {}
        for f in sorted((root / d).glob("*.md")):
            fm = frontmatter(f.read_text(encoding="utf-8"))
            m = re.search(r"^\s*name:\s*(\S+)", fm, re.MULTILINE)
            if not m:
                errs.append(f"{f}: no name field")
                continue
            name = m.group(1)
            if name in seen:
                errs.append(f"{d}: duplicate name '{name}' in {f.name} and {seen[name]}")
            seen[name] = f.name
    return errs


def check_allowlist(root: Path) -> list[str]:
    errs: list[str] = []
    agents = sorted((root / "code-agents").glob("*.md")) + sorted((root / "knowledge-agents").glob("*.md"))
    for f in agents:
        fm = frontmatter(f.read_text(encoding="utf-8"))
        if not re.search(r"^\s*tools:", fm, re.MULTILINE):
            errs.append(f"{f}: missing tools field")
    for name in ("prototyper.md", "grower.md"):
        f = root / "knowledge-agents" / name
        tools = tools_of(frontmatter(f.read_text(encoding="utf-8")))
        for banned in ("Edit", "Write"):
            if banned in tools:
                errs.append(f"knowledge-agents/{name}: must not have '{banned}' (propose, don't modify)")
    return errs


def check_boundary(root: Path) -> list[str]:
    errs: list[str] = []
    agents = sorted((root / "code-agents").glob("*.md")) + sorted((root / "knowledge-agents").glob("*.md"))
    pat = re.compile(r"\b(do not|don't|never)\b", re.IGNORECASE)
    for f in agents:
        text = f.read_text(encoding="utf-8")
        parts = text.split("---")
        body = "---".join(parts[2:]) if len(parts) >= 3 else text
        if not pat.search(body):
            errs.append(f"{f}: no boundary marker (do not / don't / never) in body")
    return errs


def check_marketplace_paths(root: Path) -> list[str]:
    errs: list[str] = []
    data = json.loads((root / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    for plugin in data.get("plugins", []):
        for rel in plugin.get("agents", []):
            if not (root / rel).is_file():
                errs.append(f"marketplace.json: '{rel}' does not resolve")
    return errs


EVAL_FIELDS = ("Setup", "Dispatch prompt", "Expected behavior", "Fail conditions", "Execution log")


def check_eval_structure(root: Path) -> list[str]:
    errs: list[str] = []
    evals = root / "docs" / "evals"
    if not evals.is_dir():
        return errs  # vacuous until M3
    for f in sorted(evals.glob("*.md")):
        if f.name == "README.md":
            continue
        text = f.read_text(encoding="utf-8")
        for field in EVAL_FIELDS:
            if not re.search(rf"^#+\s*{re.escape(field)}", text, re.MULTILINE | re.IGNORECASE):
                errs.append(f"{f}: missing '## {field}' heading")
    return errs


CHECKS = [
    ("unique agent names", check_unique_names),
    ("tool allowlist policy", check_allowlist),
    ("boundary markers", check_boundary),
    ("marketplace paths resolve", check_marketplace_paths),
    ("eval scenario structure", check_eval_structure),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root)
    failed = False
    for label, fn in CHECKS:
        errs = fn(root)
        if errs:
            failed = True
            print(f"FAIL: {label}")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"OK:   {label}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
