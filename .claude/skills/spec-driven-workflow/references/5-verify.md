# Phase 5 — Verify

Goal: show the finished feature meets every approved requirement, and leave the docs describing the new state of the system.

## Steps

1. Confirm every task in `tasks.md` is `done`.
2. Run `python tools/specs/specs.py check`. With all tasks done it fails if any approved requirement has no test marked `// Verifies: REQ-…`.
3. Run the full test suite, and list `gpu`-labelled tests that a person still has to run on real hardware.
4. Walk through each requirement's acceptance criteria and write a short verification table in the conversation: requirement → test(s) → result.
5. Update the docs the feature changed (`docs/*.md`, `Structure.md` if folders or files were added, `ProjectUnderstanding.md` if behavior or decisions changed). Mark a drafted ADR as ready for the team to accept.
6. Ask the person to set `status: done` in `requirements.md` (or set it for them if they say so).

## Done means

- `specs.py check` passes.
- CI is green on Windows and Linux.
- Every requirement has at least one passing test, or a written reason approved by a person (for example: verified manually on an AMD GPU on a given date).
- The spec folder is now history; future changes get a new spec.
