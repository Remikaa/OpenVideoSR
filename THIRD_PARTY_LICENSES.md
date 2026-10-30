# Third-party licenses

TODO(workstream A): record every dependency license before release
(Structure.md 2; AGENTS.md "Never"; model weights -> `models/licenses/`).

| Dependency | Used only in (containment rule, Structure.md 2) | License | Verified |
|---|---|---|---|
| TODO WebSocket library | `libs/transport/src` | TODO | TODO |
| FFmpeg (LGPL build, no GPL components such as x264/x265) | `libs/mediaio/src` | LGPL-2.1-or-later (verify) | TODO |
| ONNX Runtime (+ provider plugins) | `libs/inference/backends/ort`, `workers/ort-worker` | TODO | TODO |
| Qt (linked dynamically) | `ui/`, `apps/openvideosr-gui` | LGPL (verify terms) | TODO |
| TODO JSON library | `src/` of `infra` and `modelhub` | TODO | TODO |
| TODO test framework | `tests/` | TODO | TODO |
| TODO benchmark framework | `benchmarks/` | TODO | TODO |
