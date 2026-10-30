---
spec: "{{SPEC_ID}}"
title: {{TITLE}}
phase: tasks
status: draft            # draft | approved | superseded
owner:
approved-by:
created: {{DATE}}
---

# {{SPEC_ID}} {{TITLE}} — Tasks

Rules: one task is one pull request; tests are written first; tasks are listed in the order they can be built; every requirement is covered by at least one task. Interfaces and fakes come before their implementations.

## T{{SPEC_ID}}-01 Short title

- Covers: REQ-{{SPEC_ID}}-01
- Depends on: none
- Files: `libs/<lib>/...`, `tests/unit/<lib>/...`
- Done when: the named tests pass and …
- Status: todo           # todo | in-progress | done | blocked
