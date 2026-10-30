# Specs

A spec is a short, written agreement about one feature before it is built: **what** it must do (requirements), **how** it fits the architecture (design), and **in which steps** it is built (tasks). People and AI agents use the same files.

The workflow is **optional**. The build never reads this folder, and the CI check passes when no specs exist.

## When to write a spec

| Write a spec | No spec needed |
|---|---|
| The feature touches two or more libraries | A bug fix inside one class |
| It adds or changes an interface, a protocol message or a config key | Renames, formatting, comments |
| It changes behavior described in `ProjectUnderstanding.md` | A new test for existing behavior |
| An AI agent will do most of the implementation | A spike (use `spikes/` instead) |

## Layout

```text
specs/
├── README.md              this file
├── principles.md          rules every spec must respect
├── _templates/            requirements.md, design.md, tasks.md
└── 0001-<feature-name>/   one folder per feature, created by the tool
    ├── requirements.md
    ├── design.md
    └── tasks.md
```

## Lifecycle

| Phase | File | Gate before the next phase |
|---|---|---|
| 1 Requirements | `requirements.md` | A person sets `status: approved` and `approved-by` |
| 2 Design | `design.md` | A person approves it; an ADR is written if the design makes an architectural decision |
| 3 Tasks | `tasks.md` | A person approves the plan |
| 4 Implement | code and tests, one task per pull request | CI passes and the pull request is reviewed |
| 5 Verify | — | `specs.py check` passes; `requirements.md` is set to `status: done` |

Status values: `draft`, `approved`, `done` (requirements only), `superseded`. If implementation shows that an approved file is wrong, set it back to `draft`, fix it and approve it again. Code and spec must not silently disagree.

## IDs and tracing

| Item | Format | Example |
|---|---|---|
| Spec | four digits + name | `0007-gap-filling` |
| Requirement | `REQ-<spec>-<nn>` | `REQ-0007-03` |
| Task | `T<spec>-<nn>` | `T0007-04` |
| Test link | a comment in the test: `// Verifies: REQ-0007-03` (C++ and JavaScript) | |
| Commit / pull request | starts with the task ID | `T0007-04: add IngestPlanner gap search` |

`python tools/specs/specs.py check` verifies that every task covers known requirements, every approved requirement has a task, tests only reference requirements that exist, and finished specs have a test for every requirement.

## Commands

```bash
python tools/specs/specs.py new "Gap filling"   # creates specs/NNNN-gap-filling/ from the templates
python tools/specs/specs.py status              # each spec, its phase and the next step
python tools/specs/specs.py check               # traceability and phase-gate checks (also run in CI)
```

## Specs, docs and ADRs

- A **spec** is the plan for one feature. Once the feature is done it is kept as history and not updated.
- `docs/` describes the system **as it is now**. Phase 5 updates the docs the feature affected.
- An **ADR** in `docs/decisions/` records a decision that outlives the feature. The design links to it.

## With an AI agent

Agents follow `.claude/skills/spec-driven-workflow/SKILL.md`. An agent drafts each file, then stops and asks for approval; it never approves its own work.
