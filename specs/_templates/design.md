---
spec: "{{SPEC_ID}}"
title: {{TITLE}}
phase: design
status: draft            # draft | approved | superseded
owner:
approved-by:
created: {{DATE}}
---

# {{SPEC_ID}} {{TITLE}} — Design

## 1. Summary

The approach in one paragraph.

## 2. Affected libraries

Check every new dependency against `Structure.md` section 5.

| Library | Change | New dependency? Allowed? |
|---|---|---|
| | | |

## 3. Interfaces

New or changed interfaces, the library each lives in, who implements it, and its fake. Mark frozen interfaces: those need a team discussion before approval.

## 4. Data flow and threads

Which thread runs the new code, which queues it touches, how epochs and media time are handled.

## 5. Protocol, config and files

New messages (with golden vectors), config keys (with schema updates), files on disk.

## 6. Errors

Error codes added to `Result<T>` and how each one is handled or shown to the user.

## 7. Test plan

Every requirement appears at least once.

| Requirement | Test level | Test |
|---|---|---|
| REQ-{{SPEC_ID}}-01 | unit | `tests/unit/<lib>/<Class>Tests.cpp` |

## 8. Decision record

Does this design make an architectural decision? If yes: ADR title and number.

## 9. Alternatives considered

## 10. Risks and spikes
