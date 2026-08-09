#!/usr/bin/env python3
"""Validate a GitHub-wiki-standard `wiki/` directory against the conventions.

Deterministic pass/fail gate for `wiki:validate`. The rules mirror
`shared/wiki-conventions.md` (the single source of truth). The wiki is a linked
set of pages, so validation runs over the whole directory, not a single file.

ERRORs fail the check (exit 1); WARNINGs are printed but do not fail (exit 0 if
there are no errors). Exit 2 is reserved for usage/IO problems. Every finding is
printed on its own line so the output can gate CI.

Usage:
    python validate-wiki.py [wiki_dir]   # wiki_dir defaults to ./wiki
"""
from __future__ import annotations

import argparse
import os
import re
import sys

SPECIAL_PAGES = {"_Sidebar.md", "_Footer.md"}
H1_RE = re.compile(r"^#\s+\S")
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
CODE_FENCE_RE = re.compile(r"^\s*```")
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
MDLINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")


def stem_to_page(name):
    """Normalize a link target to a page filename stem (spaces -> hyphens)."""
    name = name.strip().strip("/")
    # Drop an optional #anchor and a trailing .md extension.
    name = name.split("#", 1)[0]
    name = re.sub(r"\.md$", "", name, flags=re.IGNORECASE)
    name = name.replace(" ", "-")
    return name


def is_external(target):
    t = target.strip()
    return (
        "://" in t
        or t.startswith("#")
        or t.startswith("mailto:")
        or t.startswith("//")
    )


def read_no_comments(path):
    with open(path, "r", encoding="utf-8") as fh:
        return COMMENT_RE.sub("", fh.read())


def extract_links(text):
    """Return internal page-link targets (stems) found in the text."""
    targets = []
    # Strip fenced code blocks so example links don't count.
    lines, in_fence = [], False
    for line in text.splitlines():
        if CODE_FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(line)
    body = "\n".join(lines)

    for m in WIKILINK_RE.finditer(body):
        inner = m.group(1)
        target = inner.split("|", 1)[1] if "|" in inner else inner
        targets.append(stem_to_page(target))

    for m in MDLINK_RE.finditer(body):
        target = m.group(1).strip()
        # Only follow relative page links; skip external and pure anchors.
        if is_external(target):
            continue
        # Skip links to non-markdown assets (images, files with other suffixes).
        base = target.split("#", 1)[0]
        ext = os.path.splitext(base)[1].lower()
        if ext and ext != ".md":
            continue
        targets.append(stem_to_page(target))
    return [t for t in targets if t]


def validate(wiki_dir):
    errors, warnings = [], []

    if not os.path.isdir(wiki_dir):
        print(f"error: wiki directory not found: '{wiki_dir}'", file=sys.stderr)
        return 2

    # Collect pages (flat) and detect pages nested in subdirectories.
    page_stems = set()
    top_level_md = []
    for entry in sorted(os.listdir(wiki_dir)):
        full = os.path.join(wiki_dir, entry)
        if os.path.isfile(full) and entry.lower().endswith(".md"):
            top_level_md.append(entry)
            page_stems.add(os.path.splitext(entry)[0])

    for root, _dirs, files in os.walk(wiki_dir):
        if os.path.abspath(root) == os.path.abspath(wiki_dir):
            continue
        for f in files:
            if f.lower().endswith(".md"):
                rel = os.path.relpath(os.path.join(root, f), wiki_dir)
                errors.append(
                    f"ERROR: page in a subdirectory: '{rel}' — GitHub wiki is "
                    f"flat; move it to '{wiki_dir}/' root"
                )

    # Required special pages.
    if "Home.md" not in top_level_md:
        errors.append("ERROR: missing required page 'Home.md'")
    if "_Sidebar.md" not in top_level_md:
        errors.append("ERROR: missing required page '_Sidebar.md'")

    # Per-page heading checks + collect links for resolution.
    for entry in top_level_md:
        text = read_no_comments(os.path.join(wiki_dir, entry))
        # Special '_' pages (Sidebar/Footer) are navigation chrome, not content
        # pages, so they are exempt from the level-1-heading requirement.
        if entry not in SPECIAL_PAGES:
            code = False
            h1_count = 0
            for line in text.splitlines():
                if CODE_FENCE_RE.match(line):
                    code = not code
                    continue
                if code:
                    continue
                if H1_RE.match(line):
                    h1_count += 1
            if h1_count == 0:
                errors.append(f"ERROR: page '{entry}' has no level-1 heading ('# Title')")
            elif h1_count > 1:
                warnings.append(f"WARNING: page '{entry}' has {h1_count} level-1 headings; expected one")

        for target in extract_links(text):
            if target not in page_stems:
                errors.append(
                    f"ERROR: broken internal link in '{entry}': "
                    f"'{target}' does not match any page"
                )

    # Sidebar coverage.
    sidebar = os.path.join(wiki_dir, "_Sidebar.md")
    if os.path.isfile(sidebar):
        referenced = set(extract_links(read_no_comments(sidebar)))
        content_pages = [
            e for e in top_level_md
            if e != "Home.md" and e not in SPECIAL_PAGES
        ]
        for entry in content_pages:
            stem = os.path.splitext(entry)[0]
            if stem not in referenced:
                warnings.append(
                    f"WARNING: page '{entry}' is not linked from _Sidebar.md"
                )

    for w in warnings:
        print(w)
    for e in errors:
        print(e)

    if errors:
        print(f"INVALID: {wiki_dir} ({len(errors)} error(s), {len(warnings)} warning(s))")
        return 1
    print(f"VALID: {wiki_dir} ({len(warnings)} warning(s))")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate a GitHub-wiki-standard wiki/ directory."
    )
    parser.add_argument(
        "wiki_dir", nargs="?", default="wiki",
        help="path to the wiki directory (default: ./wiki)",
    )
    args = parser.parse_args(argv)
    return validate(args.wiki_dir)


if __name__ == "__main__":
    sys.exit(main())
