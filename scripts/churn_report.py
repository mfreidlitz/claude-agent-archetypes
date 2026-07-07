#!/usr/bin/env python3
"""churn_report.py: git-history evidence for the Sweeper archetype.

The Sweeper's rule is "evidence per item, never vibes". This script produces
language-agnostic evidence from git history: which files have not been touched
in months, and which files are large relative to how often they change. Both
are unship/simplification candidates, not verdicts; the human keeps the
judgment of what to delete.

Usage:
  python scripts/churn_report.py [--stale-months 6] [--top 20] [pathspec ...]

Output: a markdown report on stdout with two sections:
  1. Stale files: not modified in more than --stale-months months.
  2. Low-churn heavyweights: highest line-count per commit ratio.

Requires git and Python 3.8+. No dependencies. Line counts skip binary files.
"""

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def git_lines(*args):
    result = subprocess.run(
        ["git", *args], capture_output=True, text=True, encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        sys.exit(f"git {' '.join(args[:3])} ... failed:\n{result.stderr.strip()}")
    return result.stdout.splitlines()


def collect_history(pathspec):
    """One pass over git log: newest-first, so the first timestamp seen per
    file is its last-touched time; every mention increments its commit count."""
    log_args = ["log", "--format=%ct", "--name-only"]
    if pathspec:
        log_args += ["--", *pathspec]
    last_touched, commit_count = {}, {}
    current_ts = None
    for line in git_lines(*log_args):
        line = line.strip()
        if not line:
            continue
        if line.isdigit():
            current_ts = int(line)
            continue
        if current_ts is None:
            continue
        last_touched.setdefault(line, current_ts)
        commit_count[line] = commit_count.get(line, 0) + 1
    return last_touched, commit_count


def count_lines(path):
    try:
        data = Path(path).read_bytes()
    except OSError:
        return None
    if b"\x00" in data[:8192]:
        return None  # binary
    return data.count(b"\n") + (0 if data.endswith(b"\n") or not data else 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pathspec", nargs="*",
                        help="optional git pathspecs to limit the report")
    parser.add_argument("--stale-months", type=int, default=6,
                        help="staleness threshold in months (default 6)")
    parser.add_argument("--top", type=int, default=20,
                        help="rows per section (default 20)")
    args = parser.parse_args()

    tracked = git_lines("ls-files", *(["--", *args.pathspec] if args.pathspec else []))
    tracked = [f for f in tracked if f.strip()]
    last_touched, commit_count = collect_history(args.pathspec)
    now = datetime.now(timezone.utc).timestamp()
    stale_seconds = args.stale_months * 30.44 * 86400

    rows = []
    for f in tracked:
        ts = last_touched.get(f)
        if ts is None:
            continue
        lines = count_lines(f)
        rows.append({
            "file": f,
            "lines": lines,
            "commits": commit_count.get(f, 0),
            "age_days": int((now - ts) / 86400),
            "stale": (now - ts) > stale_seconds,
        })

    stale = sorted((r for r in rows if r["stale"]),
                   key=lambda r: -r["age_days"])[: args.top]
    heavy = sorted(
        (r for r in rows if r["lines"] and r["commits"]),
        key=lambda r: -(r["lines"] / r["commits"]),
    )[: args.top]

    print(f"# Churn report ({datetime.now(timezone.utc).date()})")
    print(f"\nTracked files analyzed: {len(rows)}. "
          f"Staleness threshold: {args.stale_months} months.\n")

    print(f"## Stale files (untouched > {args.stale_months} months)\n")
    if stale:
        print("| File | Lines | Commits | Days since last touch |")
        print("|---|---:|---:|---:|")
        for r in stale:
            lines = r["lines"] if r["lines"] is not None else "bin"
            print(f"| {r['file']} | {lines} | {r['commits']} | {r['age_days']} |")
    else:
        print("None. Nothing has gone stale within the threshold.")

    print("\n## Low-churn heavyweights (most lines per commit)\n")
    if heavy:
        print("| File | Lines | Commits | Lines/commit |")
        print("|---|---:|---:|---:|")
        for r in heavy:
            ratio = r["lines"] / r["commits"]
            print(f"| {r['file']} | {r['lines']} | {r['commits']} | {ratio:.0f} |")
    else:
        print("No text files with history found.")

    print("\n*Evidence, not verdicts: cross-check candidates against runtime "
          "usage before proposing removal.*")


if __name__ == "__main__":
    main()
