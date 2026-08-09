#!/usr/bin/env python3
"""Resolve current SHA digests for all pinned Docker images and open a PR if any changed."""

import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

FILES_TO_SCAN = [
    "app/Dockerfile",
    "app/Dockerfile.prod",
    "frontend/Dockerfile",
    "frontend/Dockerfile.prod",
    "music-labeler/Dockerfile",
    "music-labeler/Dockerfile.prod",
    "docker-compose.yml",
    "docker-compose.prod.yml",
]

# FROM image@sha256:xxx  [AS stage]
FROM_RE = re.compile(r"^FROM\s+([^@\s]+)@(sha256:[a-f0-9]+)", re.IGNORECASE)
# image: image@sha256:xxx
IMAGE_RE = re.compile(r"^\s+image:\s+([^@\s]+)@(sha256:[a-f0-9]+)")
# standalone comment line
COMMENT_RE = re.compile(r"^\s*#\s*(.+?)\s*$")


def resolve_tag(comment: str, image_base: str) -> str:
    """Derive image:tag from the comment text preceding a FROM/image line."""
    text = comment.strip()
    if ":" in text:
        # e.g. "node:26", "postgres:15.8", "grafana/loki:latest"
        return text
    if "/" in text:
        # e.g. "mailhog/mailhog" with no tag → default to latest
        return f"{text}:latest"
    # e.g. "3.14.6-slim-trixie" → tag only, combine with image name
    return f"{image_base}:{text}"


def parse_file(filepath: Path) -> list[dict]:
    """Extract all SHA-pinned image references from a file."""
    entries = []
    lines = filepath.read_text().splitlines()
    prev_comment: str | None = None

    for i, line in enumerate(lines):
        cm = COMMENT_RE.match(line)
        if cm:
            prev_comment = cm.group(1)
            continue

        fm = FROM_RE.match(line) or IMAGE_RE.match(line)
        if fm and prev_comment is not None:
            image_base = fm.group(1)
            sha = fm.group(2)
            entries.append(
                {
                    "file": filepath,
                    "line_no": i,
                    "image_base": image_base,
                    "sha": sha,
                    "tag": resolve_tag(prev_comment, image_base),
                }
            )

        # reset after any non-comment line
        prev_comment = None

    return entries


def crane_digest(image_tag: str) -> str | None:
    """Return the current manifest digest for image:tag from the registry."""
    result = subprocess.run(
        ["crane", "digest", image_tag],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(
            f"  WARNING: crane digest failed for {image_tag}: {result.stderr.strip()}",
            file=sys.stderr,
        )
        return None
    return result.stdout.strip()


def update_file(filepath: Path, old_sha: str, new_sha: str) -> None:
    content = filepath.read_text()
    filepath.write_text(content.replace(old_sha, new_sha))


def write_output(key: str, value: str) -> None:
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        delimiter = "EOF_DIGEST_REPORT"
        with open(github_output, "a") as f:
            f.write(f"{key}<<{delimiter}\n{value}\n{delimiter}\n")
    else:
        # local run fallback
        print(f"\n--- OUTPUT: {key} ---\n{value}")


def main() -> None:
    all_entries: list[dict] = []
    for rel_path in FILES_TO_SCAN:
        fp = REPO_ROOT / rel_path
        if not fp.exists():
            print(f"  SKIP (not found): {rel_path}")
            continue
        all_entries.extend(parse_file(fp))

    # group by (image_base, tag) — one crane call per unique image:tag
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for entry in all_entries:
        groups[(entry["image_base"], entry["tag"])].append(entry)

    updates: list[dict] = []

    for (image_base, tag), entries in sorted(groups.items()):
        current_sha = entries[0]["sha"]
        print(f"Checking {tag} …", end=" ", flush=True)
        new_sha = crane_digest(tag)
        if new_sha is None:
            print("SKIP (error)")
            continue
        if new_sha == current_sha:
            print("up to date")
            continue

        print(f"UPDATE  {current_sha[7:14]}… → {new_sha[7:14]}…")
        affected = sorted({str(e["file"].relative_to(REPO_ROOT)) for e in entries})
        updates.append(
            {
                "tag": tag,
                "old_sha": current_sha,
                "new_sha": new_sha,
                "files": affected,
            }
        )
        for entry in entries:
            update_file(entry["file"], current_sha, new_sha)

    if not updates:
        print("\nAll Docker image digests are up to date.")
        write_output("has_updates", "false")
        write_output("report", "All Docker image digests are up to date.")
        return

    rows = [
        "## Docker image digest updates",
        "",
        "| Image:Tag | Old digest | New digest | Files |",
        "|-----------|------------|------------|-------|",
    ]
    for u in updates:
        old_short = u["old_sha"][7:14]
        new_short = u["new_sha"][7:14]
        files_str = ", ".join(f"`{f}`" for f in u["files"])
        rows.append(f"| `{u['tag']}` | `{old_short}…` | `{new_short}…` | {files_str} |")

    rows += ["", f"_{len(updates)} image(s) updated._"]
    report = "\n".join(rows)
    print("\n" + report)

    write_output("has_updates", "true")
    write_output("report", report)


if __name__ == "__main__":
    main()
