#!/usr/bin/env python3
"""Validate the edgeless-stack skills catalog.

Catches the drift modes that have actually bitten this bundle:
  - missing/invalid frontmatter
  - missing required fields (name, description, metadata.{tags,tier,domain}, when_to_apply)
  - personal-path leaks in skill bodies (/Users/djm, com.djm.*)
  - manifest drift (a skill file not listed in _manifest.md, or vice versa)
  - manifest totals out of sync with file counts

Stdlib only. Exits 1 on any failure.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
DOMAINS_DIR = SKILLS_DIR / "domains"
CORE_DIR = SKILLS_DIR / "core"
MANIFEST = SKILLS_DIR / "_manifest.md"

REQUIRED_FIELDS = ("name", "description", "when_to_apply")
REQUIRED_META = ("tags:", "tier:", "domain:")
LEAK_PATTERN = re.compile(r"/Users/djm|\bcom\.djm\.")


def split_frontmatter(text: str) -> tuple[str, str] | None:
    if not text.startswith("---"):
        return None
    m = re.search(r"\n---\s*\n", text[3:])
    if not m:
        return None
    return text[3:3 + m.start()], text[3 + m.end():]


def check_skill(path: Path) -> list[str]:
    errs: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"unreadable: {e}"]
    parts = split_frontmatter(text)
    if parts is None:
        return ["missing or malformed YAML frontmatter delimiters"]
    fm, body = parts
    for field in REQUIRED_FIELDS:
        if not re.search(rf"(?m)^{field}:", fm):
            errs.append(f"missing required field `{field}`")
    if "metadata:" not in fm:
        errs.append("missing `metadata:` block")
    else:
        for meta in REQUIRED_META:
            if meta not in fm:
                errs.append(f"missing `metadata.{meta.rstrip(':')}`")
    if LEAK_PATTERN.search(body):
        errs.append("body contains personal-path leak (/Users/djm or com.djm.*)")
    return errs


def discover_skills(root: Path) -> list[Path]:
    return sorted(p for p in root.glob("*.md") if p.name != "_manifest.md")


def main() -> int:
    failures: list[tuple[Path, str]] = []
    domain_skills = discover_skills(DOMAINS_DIR)
    core_skills = discover_skills(CORE_DIR)
    all_skills = core_skills + domain_skills

    for sk in all_skills:
        for e in check_skill(sk):
            failures.append((sk, e))

    manifest_text = MANIFEST.read_text(encoding="utf-8")

    # Each skill listed in the manifest table as `` `<name>` ``
    listed = set(re.findall(r"`([a-z0-9][a-z0-9._-]*)`", manifest_text))
    file_names = {p.stem for p in all_skills}

    unlisted = file_names - listed
    # `listed` matches every backticked identifier in the README (including prose like
    # `tier`, `domain`, etc.). Only flag manifest rows we can't find files for —
    # restrict orphan checking to actual table rows.
    table_rows = re.findall(r"^\|\s*`([a-z0-9][a-z0-9._-]*)`\s*\|", manifest_text, re.MULTILINE)
    table_names = set(table_rows)
    real_orphans = table_names - file_names
    if real_orphans:
        for o in sorted(real_orphans):
            failures.append((MANIFEST, f"manifest lists `{o}` but no skill file exists"))
    if unlisted:
        for u in sorted(unlisted):
            failures.append((Path(f"skills/.../{u}.md"), f"skill file not listed in _manifest.md table"))

    # Totals header
    m = re.search(r"\*\*Total skills\*\*:\s*(\d+)\s*\|\s*\*\*Core\*\*:\s*(\d+)\s*\|\s*\*\*Domain\*\*:\s*(\d+)",
                  manifest_text)
    if m:
        total, core, domain = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if core != len(core_skills):
            failures.append((MANIFEST, f"Core count mismatch: header says {core}, files={len(core_skills)}"))
        if domain != len(domain_skills):
            failures.append((MANIFEST, f"Domain count mismatch: header says {domain}, files={len(domain_skills)}"))
        if total != core + domain:
            failures.append((MANIFEST, f"Total mismatch: header says {total}, expected {core + domain}"))
    else:
        failures.append((MANIFEST, "missing or malformed `**Total skills**` header"))

    # Report
    if failures:
        print(f"validation FAILED ({len(failures)} issue(s)):\n", file=sys.stderr)
        for path, msg in failures:
            print(f"  {path.relative_to(ROOT) if path.is_absolute() else path}  →  {msg}", file=sys.stderr)
        return 1
    print(f"OK — {len(all_skills)} skills validated, manifest in sync ({len(core_skills)} core + {len(domain_skills)} domain).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
