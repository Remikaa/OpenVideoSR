# Phase 1 — Requirements

Goal: an agreed, testable description of **what** the feature does. No classes, files or libraries yet.

## Steps

1. Create the spec if needed: `python tools/specs/specs.py new "<title>"`. Fill `owner` with the person who asked.
2. Read the parts of `ProjectUnderstanding.md` that describe this behavior (section 4 for runtime behavior, 3 for decisions, 13–14 for assumptions and open questions).
3. Write the problem and the scenarios first, then the requirements.
4. Write each requirement as one row:
   - EARS form: *When <trigger>, the <component> shall <response>* / *While <state>, …* / *If <unwanted event>, then …*.
   - Acceptance criteria in Given/When/Then that a test can check. Use numbers ("within one segment length", "no segment is encoded twice"), not "fast" or "smooth".
   - Priority: Must, Should or Could, matching `ProjectUnderstanding.md` 12.2.
5. Add non-functional requirements that apply (VRAM on 6 GB, disk budget, latency, security, licensing).
6. List what is out of scope, the related D-numbers and P-numbers, and open questions.
7. Ask the person the open questions. Do not invent answers.

## Quality checks before asking for approval

- Every requirement describes behavior a user or another component can observe.
- No requirement names a class, file or library (that belongs in the design).
- No two requirements contradict each other or a principle.
- Edge cases are covered: seek, pause, epoch change, session end, cache full, protected content, live stream — whichever apply.
- IDs are sequential and never reused; a removed requirement is struck through, not renumbered.

## Example

| ID | Requirement | Acceptance criteria | Priority |
|---|---|---|---|
| REQ-0007-01 | When the user seeks to a time that is already processed, the player shall play from the cache without sending a seek to the source | Given segments 0–20 exist, when the user seeks to 40 s, then playback starts from the cache and no `Seek` command is sent | Must |
