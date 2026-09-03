"""Shared helpers for the exfu-marketplace release tooling. Python 3.9+, stdlib only."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / ".claude-plugin" / "marketplace.json"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def die(msg: str, code: int = 1) -> "NoReturn":
    sys.stdout.flush()
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> str:
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)}\n{p.stderr.strip()}")
    return p.stdout


def load_manifest() -> dict:
    with MANIFEST.open() as f:
        return json.load(f)


def save_manifest(d: dict) -> None:
    with MANIFEST.open("w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
        f.write("\n")


def entry(d: dict, name: str) -> dict:
    for e in d["plugins"]:
        if e["name"] == name:
            return e
    die(f"no plugin named {name!r} in {MANIFEST.relative_to(ROOT)}")


def resolve_ref(url: str, ref: str) -> str:
    """Resolve a branch, tag, or full sha at the remote to a 40-char sha."""
    if SHA_RE.match(ref):
        return ref
    out = run(["git", "ls-remote", url, ref, f"refs/heads/{ref}", f"refs/tags/{ref}"])
    lines = [l.split("\t") for l in out.splitlines() if l.strip()]
    if not lines:
        die(f"{ref!r} not found at {url}")
    # Prefer a peeled tag (^{}) if present, then heads, then whatever matched first.
    for sha, r in lines:
        if r.endswith("^{}"):
            return sha
    for sha, r in lines:
        if r.startswith("refs/heads/"):
            return sha
    return lines[0][0]


class PinnedTree:
    """A shallow fetch of one commit, with helpers to read files from a subdir."""

    def __init__(self, url: str, sha: str):
        self.url, self.sha = url, sha
        self.tmp = tempfile.TemporaryDirectory(prefix="exfu-mkt-")
        self.dir = Path(self.tmp.name)
        run(["git", "init", "-q"], cwd=self.dir)
        run(["git", "remote", "add", "origin", url], cwd=self.dir)
        try:
            run(["git", "fetch", "-q", "--depth", "1", "origin", sha], cwd=self.dir)
        except RuntimeError as e:
            die(f"cannot fetch {sha[:10]} from {url}: {e}")

    def read(self, path: str) -> str | None:
        p = subprocess.run(["git", "show", f"FETCH_HEAD:{path}"], cwd=self.dir,
                           text=True, capture_output=True)
        return p.stdout if p.returncode == 0 else None

    def ls(self, path: str) -> list[str]:
        """Top-level names under a tree path ('' for root). Dirs end with '/'."""
        spec = f"FETCH_HEAD:{path}" if path else "FETCH_HEAD"
        p = subprocess.run(["git", "ls-tree", spec], cwd=self.dir, text=True, capture_output=True)
        if p.returncode != 0:
            return []
        names = []
        for line in p.stdout.splitlines():
            meta, name = line.split("\t", 1)
            kind = meta.split()[1]
            names.append(name + "/" if kind == "tree" else name)
        return names

    def plugin_json(self, subdir: str) -> dict:
        raw = self.read(f"{subdir}/.claude-plugin/plugin.json")
        if raw is None:
            die(f"{subdir}/.claude-plugin/plugin.json missing at {self.sha[:10]} in {self.url}")
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            die(f"{subdir}/.claude-plugin/plugin.json at {self.sha[:10]} is not valid JSON: {e}")

    def close(self) -> None:
        self.tmp.cleanup()


def claude_available() -> bool:
    from shutil import which
    return which("claude") is not None
