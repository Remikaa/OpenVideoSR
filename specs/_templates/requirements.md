---
spec: "{{SPEC_ID}}"
title: {{TITLE}}
phase: requirements
status: draft            # draft | approved | done | superseded
owner:
approved-by:
created: {{DATE}}
---

# {{SPEC_ID}} {{TITLE}} — Requirements

## 1. Problem

What is missing or wrong today, and who notices. Two to five sentences.

## 2. Scenarios

Short user stories or situations, for example: "The user seeks into an unprocessed part of the video while processing is far ahead."

## 3. Requirements

One behavior per row. Write each in the form *When <trigger>, the <component> shall <response>* (or *While <state>, …* / *If <unwanted event>, …*). Acceptance criteria must be checkable by a test.

| ID | Requirement | Acceptance criteria | Priority |
|---|---|---|---|
| REQ-{{SPEC_ID}}-01 | When …, the … shall … | Given … when … then … | Must |

## 4. Non-functional requirements

Speed, VRAM, disk, security, licensing. Write "none" if there are none.

## 5. Out of scope

## 6. Related decisions and principles

D-numbers from `ProjectUnderstanding.md`, P-numbers from `specs/principles.md`, ADRs.

## 7. Open questions

Each question must be answered before approval.
