#!/usr/bin/env python3
"""spike.py: throwaway-worktree helper for the Prototyper archetype.

Encodes the Prototyper discipline as mechanism instead of instruction:
spikes live in isolated git worktrees, carry a `.spike` marker file that
verification hooks can check to exempt spike code from quality gates, and
are expected to be deleted ("most ideas don't ship").

Usage:
  python scripts/spike.py new <slug> [--question "What are we answering?"]
  python scripts/spike.py list
  python scripts/spike.py reap [--days 14] [--all] [--yes]

Spikes are created as sibling worktrees: <repo>-spikes/<slug>, on branch
spike/<slug>. Requires git 2.5+ and Python 3.8+. No dependencies.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

MARKER = ".spike"


def git(*args, cwd=None):
    """Run a git command and return stripped stdout; exit loudly on failure."""
    result = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True
    )
    if result.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed:\n{result.stderr.strip()}")
    return result.stdout.strip()


def repo_root():
    return Path(git("rev-parse", "--show-toplevel"))


def spikes_dir(root):
    return root.parent / f"{root.name}-spikes"


def cmd_new(args):
    root = repo_root()
    target = spikes_dir(root) / args.slug
    branch = f"spike/{args.slug}"
    if target.exists():
        sys.exit(f"Spike already exists: {target}")
    target.parent.mkdir(exist_ok=True)
    git("worktree", "add", "-b", branch, str(target), "HEAD", cwd=root)
    marker = {
        "slug": args.slug,
        "question": args.question or "",
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "note": "Throwaway spike. Exempt from verify gates. Expected to be reaped.",
    }
    (target / MARKER).write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")
    print(f"Spike worktree ready: {target}  (branch {branch})")
    print("Reminder: the deliverable is a findings note in docs/spikes/, not this code.")


def iter_spikes(root):
    base = spikes_dir(root)
    if not base.is_dir():
        return
    for path in sorted(base.iterdir()):
        marker = path / MARKER
        if not marker.is_file():
            continue
        try:
            meta = json.loads(marker.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            meta = {}
        created = meta.get("created", "")
        try:
            age_days = (
                datetime.now(timezone.utc) - datetime.fromisoformat(created)
            ).days
        except ValueError:
            age_days = -1
        yield path, meta, age_days


def cmd_list(args):
    root = repo_root()
    rows = list(iter_spikes(root))
    if not rows:
        print("No spikes.")
        return
    for path, meta, age in rows:
        question = meta.get("question") or "(no question recorded)"
        age_str = f"{age}d" if age >= 0 else "?"
        print(f"{path.name:24} {age_str:>5}  {question}")


def cmd_reap(args):
    root = repo_root()
    victims = [
        (path, age)
        for path, _meta, age in iter_spikes(root)
        if args.all or (age >= args.days)
    ]
    if not victims:
        print("Nothing to reap.")
        return
    for path, age in victims:
        print(f"reap candidate: {path.name} ({age}d old)")
    if not args.yes:
        answer = input("Remove these worktrees and their branches? [y/N] ")
        if answer.strip().lower() != "y":
            print("Aborted.")
            return
    for path, _age in victims:
        git("worktree", "remove", "--force", str(path), cwd=root)
        branch = f"spike/{path.name}"
        subprocess.run(
            ["git", "branch", "-D", branch], cwd=root,
            capture_output=True, text=True,
        )
        print(f"reaped: {path.name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new", help="create a throwaway spike worktree")
    p_new.add_argument("slug", help="short kebab-case name for the spike")
    p_new.add_argument("--question", help="the one question this spike answers")
    p_new.set_defaults(func=cmd_new)

    p_list = sub.add_parser("list", help="list existing spikes with age")
    p_list.set_defaults(func=cmd_list)

    p_reap = sub.add_parser("reap", help="remove old spike worktrees")
    p_reap.add_argument("--days", type=int, default=14,
                        help="reap spikes older than N days (default 14)")
    p_reap.add_argument("--all", action="store_true", help="reap every spike")
    p_reap.add_argument("--yes", action="store_true", help="skip confirmation")
    p_reap.set_defaults(func=cmd_reap)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
