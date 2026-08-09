#!/usr/bin/env python3
"""Validate an ADR trio against the ADR schema.

One ADR is three files sharing the stem ``YYYYMMDD-title``:
``-0-summary.md``, ``-1-plan.md``, and ``-2-followups.md``. The numeric index
keeps a directory listing in the logical summary -> plan -> followups order.
Given a path to any one of them (or the bare stem), this validates the whole
trio. The rules mirror ``shared/adr-schema.md`` (the single source of truth).

Exits 0 when the trio is valid, 1 when it has validation errors, and 2 on
usage/IO errors. Every problem is printed on its own line so the output can gate
CI.

Usage:
    python validate-adr.py docs/adr/20260808-use-postgres-0-summary.md
    python validate-adr.py docs/adr/20260808-use-postgres        # bare stem
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys

ROLES = ("summary", "plan", "followups")

# On-disk suffix per role. The leading index keeps a directory listing in the
# logical order: `0-summary` sorts before `1-plan` before `2-followups`.
ROLE_SUFFIX = {"summary": "0-summary", "plan": "1-plan", "followups": "2-followups"}

REQUIRED_SECTIONS = {
    "summary": [
        "Status",
        "Context and Problem Statement",
        "Requirements",
        "Considered Options",
        "Decision Outcome",
        "Consequences",
    ],
    "plan": ["Approach", "Steps"],
    "followups": ["Overview", "Bugs", "Gaps", "Improvements", "Nice-to-have"],
}

ALLOWED_STATUS = ["Proposed", "Accepted", "Rejected", "Deprecated", "Superseded"]
ALLOWED_SOURCE = {"human", "review", "agent"}
ITEM_STATUS = {"accepted", "out-of-the-scope"}

# Maximum physical line count per file. Keeps each doc focused; the plan gets
# more room because it captures the technical approach, not a full code preview.
MAX_LINES = {"summary": 350, "plan": 600, "followups": 350}

# Follow-up groups and their item-ID prefixes.
GROUPS = {"Bugs": "B", "Gaps": "G", "Improvements": "I", "Nice-to-have": "N"}

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
STEM_RE = re.compile(r"^(\d{8})-([a-z0-9]+(?:-[a-z0-9]+)*)$")
ID_EXACT_RE = re.compile(r"^([BGIN])(\d+)$")
ID_LEAD_RE = re.compile(r"^([BGIN]\d+)\b")
SEP_ROW_RE = re.compile(r"^\|?[\s:|-]+\|?$")
FIELD_RE = re.compile(r"^\s*\*\*\s*([A-Za-z][A-Za-z ]*?)\s*:\*\*\s*(.*)$")
MD_LINK_RE = re.compile(r"\]\(([^)]+)\)")


def derive_stem(path):
    """Return (dir, stem) from any trio member path or a bare stem path."""
    directory = os.path.dirname(path) or "."
    base = os.path.basename(path)
    base = re.sub(r"\.md$", "", base, flags=re.IGNORECASE)
    for role in ROLES:
        suffix = "-" + ROLE_SUFFIX[role]
        if base.endswith(suffix):
            base = base[: -len(suffix)]
            break
    return directory, base


def parse_headings(lines):
    headings = []
    for idx, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if m:
            headings.append((len(m.group(1)), m.group(2).strip(), idx))
    return headings


def section_content(lines, headings, i):
    _, _, start = headings[i]
    end = len(lines)
    for level, _, idx in headings[i + 1:]:
        if level <= 2:
            end = idx
            break
    return lines[start + 1:end]


def norm_heading(title):
    # Drop a leading emoji/symbol prefix (e.g. "🚦 Status" -> "Status") so
    # decorative emojis in headings don't affect section matching.
    cleaned = re.sub(r"^[^0-9A-Za-z]+", "", title.strip())
    return cleaned.lower().replace(" ", "-")


def _strip_scalar(s):
    s = s.strip()
    if len(s) >= 2 and s[0] in "\"'" and s[-1] == s[0]:
        s = s[1:-1]
    return s.strip()


def _strip_inline_comment(s):
    """Drop a trailing YAML ` # comment`, ignoring '#' inside quotes or brackets."""
    in_q, depth = None, 0
    for i, ch in enumerate(s):
        if in_q:
            if ch == in_q:
                in_q = None
        elif ch in "\"'":
            in_q = ch
        elif ch == "[":
            depth += 1
        elif ch == "]":
            depth = max(0, depth - 1)
        elif ch == "#" and depth == 0 and i > 0 and s[i - 1] in " \t":
            return s[:i].rstrip()
    return s.rstrip()


def parse_front_matter(text):
    """Minimal YAML front-matter reader for the keys the schema cares about."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fm, key = {}, None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        item = re.match(r"^\s*-\s+(.*)$", line)
        if item and isinstance(fm.get(key), list):
            v = _strip_scalar(_strip_inline_comment(item.group(1)))
            if v:
                fm[key].append(v)
            continue
        m = re.match(r"^([A-Za-z0-9_]+)\s*:\s*(.*)$", line)
        if not m:
            continue
        key = m.group(1)
        raw = _strip_inline_comment(m.group(2))
        if raw == "":
            fm[key] = []  # empty scalar or a block list that may follow
        elif raw.startswith("[") and raw.endswith("]"):
            inner = raw[1:-1].strip()
            fm[key] = [_strip_scalar(x) for x in inner.split(",") if x.strip()]
        else:
            fm[key] = _strip_scalar(raw)
    return fm


def link_to_stem(entry):
    """Reduce an ADR reference (stem, path, or markdown link) to its bare stem."""
    e = entry.strip().strip('"').strip("'")
    m = re.search(MD_LINK_RE, e)
    if m:
        e = m.group(1)
    e = os.path.basename(e.split("#", 1)[0].strip())
    e = re.sub(r"\.md$", "", e, flags=re.IGNORECASE)
    for role in ROLES:
        suffix = "-" + ROLE_SUFFIX[role]
        if e.endswith(suffix):
            return e[: -len(suffix)]
    return e


def validate_summary_metadata(text, path, errors):
    """Validate summary front matter 'when possible' — chiefly ADR link targets."""
    directory = os.path.dirname(path) or "."
    fm = parse_front_matter(text)

    if "tags" in fm and not isinstance(fm["tags"], list):
        errors.append(f"ERROR: {path}: front-matter 'tags' must be a YAML array")

    cont = fm.get("continuation_of")
    refs = cont if isinstance(cont, list) else ([cont] if cont else [])
    for entry in refs:
        entry = str(entry).strip()
        if not entry:
            continue
        target = os.path.join(
            directory, link_to_stem(entry) + "-" + ROLE_SUFFIX["summary"] + ".md"
        )
        if not os.path.isfile(target):
            errors.append(
                f"ERROR: {path}: continuation_of references '{entry}' but "
                f"'{target}' does not exist"
            )


def entry_content(lines, headings, j):
    """Lines under the H3 at headings[j], up to the next heading of level <= 3."""
    _, _, start = headings[j]
    end = len(lines)
    for level, _, idx in headings[j + 1:]:
        if level <= 3:
            end = idx
            break
    return lines[start + 1:end]


def parse_entry_fields(content):
    """Map a detail entry's **Field:** labels to [inline_value, has_body]."""
    fields, current = {}, None
    for ln in content:
        m = FIELD_RE.match(ln)
        if m:
            current = m.group(1).strip().lower()
            fields[current] = [m.group(2).strip(), bool(m.group(2).strip())]
        elif current is not None and ln.strip():
            fields[current][1] = True
    return fields


def overview_rows(content):
    """Yield the data-row cell lists of the Overview table (skips header/separator)."""
    for ln in content:
        s = ln.strip()
        if not s.startswith("|"):
            continue
        if SEP_ROW_RE.match(s):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        lowered = [c.lower() for c in cells]
        if "group" in lowered and "id" in lowered and "title" in lowered:
            continue  # header row
        if all(c == "" for c in cells):
            continue  # blank placeholder row
        yield cells


def validate_followups(lines, headings, errors, path):
    """Validate the Overview table, per-group detail entries, and their consistency."""
    group_by_norm = {norm_heading(name): (name, letter)
                     for name, letter in GROUPS.items()}
    overview, detail_ids = {}, set()

    # --- Overview table ---
    for i, (level, title, _) in enumerate(headings):
        if level == 2 and norm_heading(title) == "overview":
            for cells in overview_rows(section_content(lines, headings, i)):
                if len(cells) < 5:
                    errors.append(
                        f"ERROR: {path}: Overview row has fewer than 5 columns: "
                        f"'{' | '.join(cells)}'"
                    )
                    continue
                group, iid, ititle = cells[0], cells[1], cells[2]
                source, status = cells[3].lower(), cells[4].lower()
                gname = group_by_norm.get(norm_heading(group))
                if gname is None:
                    errors.append(
                        f"ERROR: {path}: Overview Group '{group}' invalid; must be "
                        f"one of: {', '.join(GROUPS)}"
                    )
                m = ID_EXACT_RE.match(iid)
                if not m:
                    errors.append(
                        f"ERROR: {path}: Overview ID '{iid}' invalid; expected a "
                        f"prefix (B/G/I/N) + number"
                    )
                else:
                    if gname and gname[1] != m.group(1):
                        errors.append(
                            f"ERROR: {path}: Overview ID '{iid}' prefix does not "
                            f"match Group '{group}'"
                        )
                    if iid in overview:
                        errors.append(f"ERROR: {path}: duplicate Overview ID '{iid}'")
                    overview[iid] = (source, status)
                if ititle == "":
                    errors.append(f"ERROR: {path}: Overview row '{iid}' has an empty Title")
                if source not in ALLOWED_SOURCE:
                    errors.append(
                        f"ERROR: {path}: Overview item '{iid}' Source '{cells[3]}' "
                        f"invalid; must be one of: {', '.join(sorted(ALLOWED_SOURCE))}"
                    )
                if status not in ITEM_STATUS:
                    errors.append(
                        f"ERROR: {path}: Overview item '{iid}' Status '{cells[4]}' "
                        f"invalid; must be one of: {', '.join(sorted(ITEM_STATUS))}"
                    )
            break

    # --- Per-group detail entries (### <ID> — Title) ---
    for gi in range(len(headings)):
        level, title, _ = headings[gi]
        if level != 2 or norm_heading(title) not in group_by_norm:
            continue
        gname, gletter = group_by_norm[norm_heading(title)]
        j = gi + 1
        while j < len(headings) and headings[j][0] > 2:
            if headings[j][0] != 3:
                j += 1
                continue
            title3 = headings[j][1]
            m = ID_LEAD_RE.match(re.sub(r"^[^A-Za-z0-9]+", "", title3))
            if not m:
                errors.append(
                    f"ERROR: {path}: {gname} item heading '### {title3}' must start "
                    f"with an ID like {gletter}1"
                )
                j += 1
                continue
            iid = m.group(1)
            if iid[0] != gletter:
                errors.append(
                    f"ERROR: {path}: item '{iid}' sits under group '{gname}' but its "
                    f"prefix is '{iid[0]}'"
                )
            if iid in detail_ids:
                errors.append(f"ERROR: {path}: duplicate detail item ID '{iid}'")
            detail_ids.add(iid)
            validate_entry_fields(iid, parse_entry_fields(entry_content(lines, headings, j)),
                                  overview.get(iid), errors, path)
            j += 1

    # --- Overview <-> detail consistency ---
    for iid in overview:
        if iid not in detail_ids:
            errors.append(
                f"ERROR: {path}: Overview lists '{iid}' but no '### {iid} …' detail "
                f"entry exists"
            )
    for iid in detail_ids:
        if iid not in overview:
            errors.append(
                f"ERROR: {path}: detail entry '### {iid} …' has no matching "
                f"Overview row"
            )


def validate_entry_fields(iid, fields, ov, errors, path):
    """Check a detail entry's Description / Source / Status and Overview agreement."""
    desc = fields.get("description")
    if not desc or not desc[1]:
        errors.append(f"ERROR: {path}: follow-up item '{iid}' is missing a non-empty **Description**")

    src = fields.get("source")
    if not src:
        errors.append(f"ERROR: {path}: follow-up item '{iid}' is missing **Source**")
    else:
        sval = src[0].split()[0].lower() if src[0] else ""
        if sval not in ALLOWED_SOURCE:
            errors.append(
                f"ERROR: {path}: follow-up item '{iid}' Source '{src[0]}' invalid; "
                f"must be one of: {', '.join(sorted(ALLOWED_SOURCE))}"
            )
        elif ov and ov[0] in ALLOWED_SOURCE and ov[0] != sval:
            errors.append(
                f"ERROR: {path}: follow-up item '{iid}' Source '{sval}' disagrees "
                f"with the Overview ('{ov[0]}')"
            )

    st = fields.get("status")
    if not st:
        errors.append(f"ERROR: {path}: follow-up item '{iid}' is missing **Status**")
    else:
        stval = st[0].split()[0].lower() if st[0] else ""
        if stval not in ITEM_STATUS:
            errors.append(
                f"ERROR: {path}: follow-up item '{iid}' Status '{st[0]}' invalid; "
                f"must be one of: {', '.join(sorted(ITEM_STATUS))}"
            )
        elif ov and ov[1] in ITEM_STATUS and ov[1] != stval:
            errors.append(
                f"ERROR: {path}: follow-up item '{iid}' Status '{stval}' disagrees "
                f"with the Overview ('{ov[1]}')"
            )


def validate_file(path, role, errors):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        errors.append(f"ERROR: cannot read '{path}': {exc}")
        return

    raw_line_count = len(text.splitlines())
    limit = MAX_LINES.get(role)
    if limit is not None and raw_line_count > limit:
        errors.append(
            f"ERROR: {path}: {role} is {raw_line_count} lines; must be at most "
            f"{limit}"
        )

    lines = COMMENT_RE.sub("", text).splitlines()
    headings = parse_headings(lines)

    if not headings:
        errors.append(f"ERROR: {path}: no headings; expected a '# title' heading")
    elif headings[0][0] != 1:
        errors.append(
            f"ERROR: {path}: first heading must be a level-1 '# ...' title, "
            f"found level {headings[0][0]}"
        )

    # Map level-2 section title -> content (normalized keys for matching).
    h2 = {}
    for i, (level, title, _) in enumerate(headings):
        if level == 2:
            key = norm_heading(title)
            if key not in h2:
                h2[key] = section_content(lines, headings, i)

    for sec in REQUIRED_SECTIONS[role]:
        key = norm_heading(sec)
        if key not in h2:
            errors.append(f"ERROR: {path}: missing required section '## {sec}'")
            continue
        content = h2[key]
        non_blank = [ln.strip() for ln in content if ln.strip()]
        # A follow-up group counts a header-only table as legitimately empty.
        if role != "followups" and not non_blank:
            errors.append(f"ERROR: {path}: section '## {sec}' is empty")
            continue
        if role == "summary" and sec == "Status":
            first = non_blank[0] if non_blank else ""
            if not any(
                re.match(rf"^{re.escape(v)}\b", first, re.IGNORECASE)
                for v in ALLOWED_STATUS
            ):
                errors.append(
                    f"ERROR: {path}: invalid Status '{first}'; must start with one "
                    f"of: {', '.join(ALLOWED_STATUS)}"
                )
            # When a Superseded link is provided, its target must exist.
            if first.lower().startswith("superseded"):
                mlink = MD_LINK_RE.search(first)
                if mlink and "://" not in mlink.group(1):
                    directory = os.path.dirname(path) or "."
                    tgt = os.path.basename(mlink.group(1).split("#", 1)[0].strip())
                    if not os.path.isfile(os.path.join(directory, tgt)):
                        errors.append(
                            f"ERROR: {path}: Superseded link target "
                            f"'{mlink.group(1)}' does not exist"
                        )
    if role == "summary":
        validate_summary_metadata(text, path, errors)
    if role == "followups":
        validate_followups(lines, headings, errors, path)


def validate(input_path):
    errors = []
    directory, stem = derive_stem(input_path)

    m = STEM_RE.match(stem)
    if not m:
        errors.append(
            f"ERROR: bad ADR name '{stem}'; expected 'YYYYMMDD-title' or "
            f"'YYYYMMDD-group-NN-title'"
        )
    else:
        try:
            dt.datetime.strptime(m.group(1), "%Y%m%d")
        except ValueError:
            errors.append(f"ERROR: '{m.group(1)}' is not a real YYYYMMDD date")

    for role in ROLES:
        path = os.path.join(directory, f"{stem}-{ROLE_SUFFIX[role]}.md")
        if not os.path.isfile(path):
            errors.append(f"ERROR: missing trio file: '{path}'")
            continue
        validate_file(path, role, errors)

    if errors:
        print(f"INVALID: {os.path.join(directory, stem)} ({len(errors)} error(s))")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"VALID: {os.path.join(directory, stem)} (summary + plan + followups)")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate an ADR trio (summary + plan + followups)."
    )
    parser.add_argument(
        "adr",
        help="path to any trio file, or the shared 'YYYYMMDD-title' stem",
    )
    args = parser.parse_args(argv)
    return validate(args.adr)


if __name__ == "__main__":
    sys.exit(main())
