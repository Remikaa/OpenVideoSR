#!/usr/bin/env python3
"""Spec tool for OpenVideoSR.

    python tools/specs/specs.py new "Gap filling"   create specs/NNNN-gap-filling/ from the templates
    python tools/specs/specs.py status              show each spec's phase and the next step
    python tools/specs/specs.py check               traceability and phase-gate checks (used by CI)

Standard library only, so it runs anywhere Python 3.9+ is installed.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

SPEC_DIR_RE = re.compile(r"^(\d{4})-[a-z0-9][a-z0-9-]*$")
REQ_RE = re.compile(r"\bREQ-(\d{4})-(\d{2})\b")
TASK_HEADING_RE = re.compile(r"^##\s+(T(\d{4})-(\d{2}))\b(.*)$", re.MULTILINE)
VERIFIES_RE = re.compile(r"Verifies:\s*((?:REQ-\d{4}-\d{2}[\s,]*)+)")
PHASE_FILES = ("requirements.md", "design.md", "tasks.md")
TEST_ROOTS = ("tests", "extension/tests")
TEST_SUFFIXES = {".cpp", ".cc", ".cxx", ".h", ".hpp", ".js", ".mjs", ".ts", ".py"}


def repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "specs").is_dir() or (candidate / "Structure.md").exists():
            return candidate
    return start


def read_front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    values: dict[str, str] = {}
    for line in text[3:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.split("#", 1)[0].strip().strip('"').strip("'")
        values[key.strip()] = value
    return values


def body(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:]
    return text


@dataclass
class Task:
    task_id: str
    covers: set[str] = field(default_factory=set)
    status: str = ""


@dataclass
class Spec:
    path: Path
    spec_id: str
    statuses: dict[str, str] = field(default_factory=dict)
    requirements: set[str] = field(default_factory=set)
    tasks: list[Task] = field(default_factory=list)

    @property
    def name(self) -> str:
        return self.path.name


def parse_tasks(text: str) -> list[Task]:
    content = body(text)
    matches = list(TASK_HEADING_RE.finditer(content))
    tasks = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        block = content[match.end():end]
        task = Task(match.group(1))
        for line in block.splitlines():
            stripped = line.strip().lstrip("-").strip()
            lower = stripped.lower()
            if lower.startswith("covers:"):
                task.covers |= {m.group(0) for m in REQ_RE.finditer(stripped)}
            elif lower.startswith("status:"):
                task.status = stripped.split(":", 1)[1].split("#", 1)[0].strip().lower()
        tasks.append(task)
    return tasks


def load_specs(root: Path) -> list[Spec]:
    specs_dir = root / "specs"
    if not specs_dir.is_dir():
        return []
    specs = []
    for folder in sorted(p for p in specs_dir.iterdir() if p.is_dir()):
        match = SPEC_DIR_RE.match(folder.name)
        if not match:
            continue
        spec = Spec(folder, match.group(1))
        for file_name in PHASE_FILES:
            file_path = folder / file_name
            if not file_path.exists():
                continue
            text = file_path.read_text(encoding="utf-8")
            spec.statuses[file_name] = read_front_matter(text).get("status", "").lower()
            if file_name == "requirements.md":
                spec.requirements = {m.group(0) for m in REQ_RE.finditer(body(text))
                                     if m.group(1) == spec.spec_id}
            elif file_name == "tasks.md":
                spec.tasks = parse_tasks(text)
        specs.append(spec)
    return specs


def collect_verified(root: Path) -> dict[str, list[str]]:
    """Map each requirement ID to the test files that say 'Verifies: <id>'."""
    found: dict[str, list[str]] = {}
    for test_root in TEST_ROOTS:
        base = root / test_root
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in TEST_SUFFIXES:
                continue
            if "testdata" in path.parts or "node_modules" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for match in VERIFIES_RE.finditer(text):
                for req in REQ_RE.finditer(match.group(1)):
                    found.setdefault(req.group(0), []).append(str(path.relative_to(root)))
    return found


def is_approved(status: str) -> bool:
    return status in ("approved", "done")


def next_step(spec: Spec) -> str:
    s = spec.statuses
    if s.get("requirements.md") == "superseded":
        return "superseded"
    if s.get("requirements.md") == "done":
        return "done"
    if not is_approved(s.get("requirements.md", "")):
        return "phase 1: finish requirements.md and get it approved"
    if not is_approved(s.get("design.md", "")):
        return "phase 2: finish design.md and get it approved"
    if not is_approved(s.get("tasks.md", "")):
        return "phase 3: finish tasks.md and get it approved"
    open_tasks = [t for t in spec.tasks if t.status != "done"]
    if open_tasks:
        ready = [t for t in open_tasks if t.status in ("todo", "in-progress", "")]
        first = ready[0].task_id if ready else open_tasks[0].task_id
        return f"phase 4: {len(open_tasks)} task(s) open, next {first}"
    return "phase 5: verify, then set requirements.md to status: done"


def cmd_status(root: Path) -> int:
    specs = load_specs(root)
    if not specs:
        print("No specs yet. Create one with: python tools/specs/specs.py new \"<title>\"")
        return 0
    for spec in specs:
        phases = ", ".join(f"{name.split('.')[0]}={spec.statuses.get(name, 'missing')}"
                           for name in PHASE_FILES)
        print(f"{spec.name}: {phases}")
        print(f"    next: {next_step(spec)}")
    return 0


def cmd_check(root: Path) -> int:
    specs = load_specs(root)
    errors: list[str] = []
    warnings: list[str] = []
    known = set()
    for spec in specs:
        known |= spec.requirements
    verified = collect_verified(root)

    for spec in specs:
        s = spec.statuses
        prefix = spec.name
        for file_name in PHASE_FILES:
            if file_name not in s:
                errors.append(f"{prefix}: {file_name} is missing")
        # Phase gates: a later phase cannot be approved before an earlier one.
        if is_approved(s.get("design.md", "")) and not is_approved(s.get("requirements.md", "")):
            errors.append(f"{prefix}: design.md is approved but requirements.md is not")
        if is_approved(s.get("tasks.md", "")) and not is_approved(s.get("design.md", "")):
            errors.append(f"{prefix}: tasks.md is approved but design.md is not")

        seen_tasks = set()
        covered = set()
        for task in spec.tasks:
            if task.task_id in seen_tasks:
                errors.append(f"{prefix}: task {task.task_id} appears twice")
            seen_tasks.add(task.task_id)
            if not task.task_id.startswith(f"T{spec.spec_id}-"):
                errors.append(f"{prefix}: task {task.task_id} does not use this spec's number")
            if not task.covers:
                errors.append(f"{prefix}: task {task.task_id} has no 'Covers:' requirement")
            for req in task.covers - spec.requirements:
                errors.append(f"{prefix}: task {task.task_id} covers unknown {req}")
            covered |= task.covers
            if task.status and task.status not in ("todo", "in-progress", "done", "blocked"):
                errors.append(f"{prefix}: task {task.task_id} has unknown status '{task.status}'")

        if is_approved(s.get("tasks.md", "")):
            for req in sorted(spec.requirements - covered):
                errors.append(f"{prefix}: {req} is not covered by any task")

        all_done = bool(spec.tasks) and all(t.status == "done" for t in spec.tasks)
        missing_tests = sorted(r for r in spec.requirements if r not in verified)
        if missing_tests and (all_done or s.get("requirements.md") == "done"):
            for req in missing_tests:
                errors.append(f"{prefix}: {req} has no test marked 'Verifies: {req}'")
        elif missing_tests and is_approved(s.get("tasks.md", "")):
            warnings.append(f"{prefix}: {len(missing_tests)} requirement(s) not yet verified by a test")

    for req, files in sorted(verified.items()):
        if req not in known:
            errors.append(f"{files[0]}: 'Verifies: {req}' refers to a requirement that does not exist")

    for warning in warnings:
        print(f"warning: {warning}")
    for error in errors:
        print(f"error: {error}")
    if not specs and not errors:
        print("No specs found; nothing to check.")
    print(f"specs check: {len(specs)} spec(s), {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:48].rstrip("-") or "feature"


def cmd_new(root: Path, title: str) -> int:
    specs_dir = root / "specs"
    templates = specs_dir / "_templates"
    if not templates.is_dir():
        print(f"error: templates not found in {templates}", file=sys.stderr)
        return 1
    numbers = [int(m.group(1)) for p in specs_dir.iterdir()
               if p.is_dir() and (m := SPEC_DIR_RE.match(p.name))]
    spec_id = f"{(max(numbers) + 1) if numbers else 1:04d}"
    folder = specs_dir / f"{spec_id}-{slugify(title)}"
    folder.mkdir()
    replacements = {"{{SPEC_ID}}": spec_id, "{{TITLE}}": title.strip(),
                    "{{DATE}}": _dt.date.today().isoformat()}
    for file_name in PHASE_FILES:
        text = (templates / file_name).read_text(encoding="utf-8")
        for key, value in replacements.items():
            text = text.replace(key, value)
        (folder / file_name).write_text(text, encoding="utf-8")
    print(folder.relative_to(root))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=None, help="repository root (found automatically)")
    sub = parser.add_subparsers(dest="command", required=True)
    new = sub.add_parser("new", help="create a new spec folder from the templates")
    new.add_argument("title")
    sub.add_parser("status", help="show each spec's phase and next step")
    sub.add_parser("check", help="run traceability and phase-gate checks")
    args = parser.parse_args(argv)
    root = (args.root or repo_root(Path.cwd())).resolve()
    if args.command == "new":
        return cmd_new(root, args.title)
    if args.command == "status":
        return cmd_status(root)
    return cmd_check(root)


if __name__ == "__main__":
    sys.exit(main())
