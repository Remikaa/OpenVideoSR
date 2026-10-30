# Phase 2 — Design

Goal: decide **how** the approved requirements fit the existing architecture. Requirements must have `status: approved`.

## Steps

1. Read `Structure.md` sections 2, 4 (the libraries involved), 5 and 7, and the docs in `docs/` for the area.
2. For each requirement, find the library that owns that responsibility. Prefer extending an existing class over adding a library.
3. Fill the "Affected libraries" table. For every new include between libraries, check the dependency table. If it is forbidden, redesign (usually: an interface in the consuming library, implemented in an adapter library, wired in the composition root).
4. Describe interfaces: name, library, implementer, fake. Mark any change to a frozen interface; that needs a team discussion before approval.
5. Describe threads and queues: which thread runs the code, what blocks, how epochs and media time are carried.
6. List protocol messages (and golden vectors), config keys (and schema), and files on disk.
7. List error codes and what the user sees for each.
8. Write the test plan: every requirement maps to at least one named test and a level (unit, integration, model, gpu).
9. Decide whether this is an architectural decision. If it is, draft an ADR in `docs/decisions/` from the template with status "Proposed" and link it.
10. Record alternatives you rejected and why, and any spike needed.

## Quality checks before asking for approval

- Every requirement appears in the test plan.
- No new arrow breaks `Structure.md` section 5; no third-party header leaks into a public header.
- New interfaces live with their user and have a fake.
- The design follows every principle in `specs/principles.md`, or the conflict is listed as an open question.
- Nothing in the design is a requirement that was not approved (no scope creep). If you found a missing requirement, propose it for `requirements.md` instead.
