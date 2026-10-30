# Phase 4 — Implement one task

Goal: finish exactly one task from an approved `tasks.md`. Tasks must have `status: approved`.

## Steps

1. Pick the task the person named, or the first `todo` task whose dependencies are `done`. Set it to `in-progress`.
2. Re-read the requirements it covers and the design sections it touches.
3. Write the tests first. Mark each test that proves a requirement with a comment on the line above it:
   ```cpp
   // Verifies: REQ-0007-01
   TEST(CoverageMapTests, SeekInsideCoveredRangeNeedsNoSourceSeek) { ... }
   ```
   ```js
   // Verifies: REQ-0007-04
   test('PauseWatcher reports a page pause once', () => { ... });
   ```
4. Run the tests and see them fail for the right reason.
5. Implement until they pass. Stay inside the files the task lists; if you need others, say why.
6. Build and test:
   ```bash
   cmake --build --preset linux-ninja-debug
   ctest --preset linux-ninja-debug -LE gpu
   ```
   (and `npm run lint && npm test` in `extension/` if you touched it).
7. Run `python tools/specs/specs.py check`.
8. Set the task to `done`, commit with the task ID first (`T0007-03: …`), and report: what changed, the test results, anything you could not verify (for example `gpu` tests).

## Rules

- One task per pull request. Do not start the next task in the same change.
- Never delete, skip or loosen a test to get green. If a test is wrong, explain why and ask.
- If the task cannot be done as designed, stop: set it to `blocked`, explain, and propose a design change. Do not invent a different design.
- Follow `Structure.md` conventions: public headers in `include/openvideosr/<lib>/`, `Result<T>`, `#pragma once`, one class per file, third-party code only where section 2 allows it.
