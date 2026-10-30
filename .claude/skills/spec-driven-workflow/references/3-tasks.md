# Phase 3 — Tasks

Goal: an ordered list of small, independently reviewable steps. Design must have `status: approved`.

## Steps

1. Split the design into tasks. One task is one pull request that a reviewer can read in about half an hour (as a guide, under 400 changed lines).
2. Order them so each one builds and passes CI on its own:
   1. interfaces and their fakes,
   2. pure logic with unit tests,
   3. adapters (FFmpeg, ONNX Runtime, WebSocket, Qt),
   4. wiring in the composition root,
   5. integration tests and docs.
3. For each task fill: `Covers` (requirement IDs), `Depends on`, `Files` (real paths from `Structure.md`), `Done when` (named tests that must pass), `Status: todo`.
4. Tasks that different workstreams can do in parallel should not depend on each other; say so.
5. Run `python tools/specs/specs.py check`. It fails if a task covers an unknown requirement or an approved requirement has no task.

## Quality checks before asking for approval

- Every requirement is covered by at least one task.
- Every task names the tests that prove it.
- No task mixes an interface change with its implementation in another library.
- The last task updates the docs listed in `Structure.md` section 7 for this kind of change.
