# OpenVideoSR — Repository Structure (revised)

This document describes **only the structure of the repository**: what every folder and file is for, how the pieces depend on each other, how the build is organized, and where new code should go.

For the purpose of the project, its runtime behavior, the models, encoding, devices and the roadmap, see `ProjectUnderstanding.md`.

Entries marked **(later)** are placeholders. They are listed so the design is visible, but they are created only when their phase starts (section 8). Postponed components are listed in section 9. **Section 10 lists every change from the previous version and the reason for it.**

The repository also supports an **optional spec-driven workflow** for people and AI agents (`AGENTS.md`, `specs/`, `.claude/skills/`, `tools/specs/`). Nothing in the build depends on it, and every check passes when no specs exist. See sections 4.29–4.31.

---

## 1. Layout at a glance

| Folder | Holds | Language / build | May depend on |
|---|---|---|---|
| `cmake/` | Reusable CMake modules | CMake | — |
| `config/` | Default and example runtime settings | JSON | — |
| `apps/` | Executables: desktop GUI, CLI, mobile placeholder | C++ / CMake | `libs/`, `ui/` |
| `libs/` | All non-UI C++ code, one static library per responsibility | C++ / CMake | other `libs/` (downward only, see section 5) |
| `workers/` | Optional separate model-runner executables (later) | C++ / CMake | `workers/common`, runtime SDKs |
| `ui/` | Qt windows, widgets, player, view models | C++ / Qt / CMake | `libs/session` and a few read-only libraries |
| `extension/` | Chrome extension (capture and transport) | JavaScript / npm | none (talks to the app over the protocol) |
| `models/` | Model manifest, profiles, licenses (weights are not committed) | JSON | — |
| `tools/` | Model export, evaluation, protocol and setup scripts | Python / PowerShell / shell | — |
| `spikes/` | Throw-away experiments from the early spikes; not part of the build | Any | anything |
| `packaging/` | Installer and deployment scripts for Windows and Linux | CMake / scripts | build output |
| `benchmarks/` | Performance benchmarks | C++ / CMake | `libs/` |
| `tests/` | Shared fakes, unit, integration and test data | C++ / CMake | `libs/`, `ui/` |
| `docs/` | Design documents and decision records | Markdown | — |
| `specs/` | Optional feature specs (requirements, design, tasks), principles and templates | Markdown | — (read by people, agents and `tools/specs`) |
| `.claude/` | Shared AI agent settings and skills (the spec-driven workflow skill) | Markdown / JSON | — |
| `third_party/` | Vendored code (only when a package manager cannot provide it) | — | — |
| `build/` | Generated build output (git-ignored) | — | — |

---

## 2. Conventions

| Topic | Convention |
|---|---|
| What "library" means here | A **library is a compiled code module** (a CMake static library) linked into the application at build time, like a Maven module or JAR in Java. It is **not a service**: nothing runs on its own, there is no network call, and the application is one process |
| One library, one responsibility | Each folder in `libs/` is one library with its own `CMakeLists.txt` and a CMake target named `ovsr::<name>`. `ui/` follows the same rules as a library (`ovsr::ui`) |
| Public vs private | Public headers live in `libs/<lib>/include/openvideosr/<lib>/`. Everything in `libs/<lib>/src/` is private and cannot be included by other libraries |
| Include style | `#include <openvideosr/<lib>/File.h>` across libraries; relative includes only inside one library |
| Namespaces | `ovsr::<lib>` (for example `ovsr::pipeline`) |
| C++ standard | C++23, because `Result<T>` uses `std::expected`. Minimum compiler versions (GCC, Clang, MSVC) are written in `docs/building.md` and checked by CI |
| Interfaces | Abstract classes start with `I` (`IUpscaler`, `IMediaSource`, `ISegmentSink`) and sit in the library that *uses* them, so higher layers can be tested with fakes and lower layers can implement them |
| Fakes | Every interface gets a fake in `tests/support` (target `ovsr::testsupport`) in the same pull request that adds the interface. Workstreams build against these shared fakes |
| Third-party containment | Each heavy dependency is allowed in exactly one place: **Qt** only in `ui/` and `apps/openvideosr-gui`; **FFmpeg** only in `libs/mediaio/src`; **ONNX Runtime** only in `libs/inference/backends/ort` and `workers/ort-worker`; the **WebSocket library** only in `libs/transport/src`; the **JSON library** only in the `src/` of `infra` and `modelhub`. Public headers never include third-party headers (except Qt headers inside `ui/`) |
| File naming | One main class per file; the file is named after the class |
| Headers | `#pragma once`; header-only code only for templates and tiny types |
| Errors | Functions that can fail return `Result<T>` (`std::expected<T, Error>`); no exceptions across library boundaries |
| Tests | One test file per class, in a folder mirroring the library. CTest labels: `unit`, `integration`, `model` (tiny ONNX model, CPU), `gpu` (needs a real GPU; not run in CI) |
| Optional components | Behind CMake options; the project must build with none of them enabled |
| Platform code | Behind an interface, in a `platform/` subfolder, with a Windows and a Linux implementation where needed |
| Placeholders | Marked **(later)** in this document. A folder is created together with its `CMakeLists.txt` and a first test when its phase starts |
| Specs (optional) | A feature that touches two or more libraries, an interface, the protocol or a config key, or that an AI agent will mostly build, may get a spec in `specs/NNNN-<name>/`. Small fixes do not need one. Rules in `specs/README.md` |
| Requirement tracing | Requirement IDs `REQ-<spec>-<nn>`, task IDs `T<spec>-<nn>`. A test that proves a requirement has `// Verifies: REQ-<spec>-<nn>` on the line above it (C++ and JavaScript). Commits and pull requests start with the task ID |
| Agent instructions | One tool-neutral file, `AGENTS.md`, holds the rules for every AI agent; `CLAUDE.md` only imports it. Skills live in `.claude/skills/<name>/SKILL.md`. Agents never approve spec phases and never edit `specs/principles.md` |
| Licensing | The project is Apache License 2.0. Third-party licenses are listed in `THIRD_PARTY_LICENSES.md` and `models/licenses/` |

---

## 3. Full tree

```text
OpenVideoSR/
├── CMakeLists.txt
├── CMakePresets.json
├── vcpkg.json
├── vcpkg-configuration.json
├── README.md
├── Structure.md
├── ProjectUnderstanding.md
├── AGENTS.md                            (rules for all AI coding agents)
├── CLAUDE.md                            (imports AGENTS.md)
├── LICENSE                              (Apache License 2.0)
├── NOTICE
├── THIRD_PARTY_LICENSES.md
├── .gitignore
├── .gitattributes
├── .editorconfig
├── .clang-format
├── .clang-tidy
│
├── .github/
│   ├── CODEOWNERS                       (one owner per workstream folder)
│   ├── pull_request_template.md
│   └── workflows/
│       ├── ci-cpp.yml                   (Windows and Linux matrix)
│       ├── ci-extension.yml
│       └── ci-specs.yml                 (spec traceability; passes when there are no specs)
│
├── .claude/
│   ├── settings.json                    (shared agent permissions; settings.local.json is git-ignored)
│   └── skills/
│       ├── spec-driven-workflow/
│       │   ├── SKILL.md
│       │   └── references/
│       │       ├── 1-requirements.md
│       │       ├── 2-design.md
│       │       ├── 3-tasks.md
│       │       ├── 4-implement.md
│       │       └── 5-verify.md
│       ├── add-model/                   (later)
│       ├── add-protocol-message/        (later)
│       └── add-pipeline-stage/          (later)
│
├── specs/
│   ├── README.md
│   ├── principles.md
│   ├── _templates/
│   │   ├── requirements.md
│   │   ├── design.md
│   │   └── tasks.md
│   └── NNNN-<feature-name>/             (one per feature, created by tools/specs/specs.py new)
│       ├── requirements.md
│       ├── design.md
│       └── tasks.md
│
├── cmake/
│   ├── OvsrOptions.cmake
│   ├── OvsrAddLibrary.cmake
│   ├── CompilerWarnings.cmake
│   ├── Sanitizers.cmake
│   ├── Testing.cmake
│   ├── FindOnnxRuntime.cmake
│   └── OvsrInstall.cmake
│
├── config/
│   ├── default.json
│   ├── local.example.json
│   └── config.schema.json
│
├── apps/
│   ├── CMakeLists.txt
│   ├── openvideosr-gui/
│   │   ├── CMakeLists.txt
│   │   ├── main.cpp
│   │   ├── Application.h / .cpp
│   │   ├── SingleInstanceGuard.h / .cpp
│   │   └── CompositionRoot.h / .cpp
│   ├── openvideosr-cli/
│   │   ├── CMakeLists.txt
│   │   ├── main.cpp
│   │   ├── CliOptions.h / .cpp
│   │   └── CliCompositionRoot.h / .cpp
│   └── openvideosr-mobile/              (later)
│       ├── CMakeLists.txt
│       └── README.md
│
├── libs/
│   ├── CMakeLists.txt
│   ├── base/
│   │   ├── CMakeLists.txt
│   │   └── include/openvideosr/base/
│   │       ├── Error.h
│   │       ├── Result.h
│   │       ├── Platform.h
│   │       ├── StrongId.h
│   │       ├── ITimeSource.h
│   │       └── SteadyTimeSource.h
│   ├── media/
│   │   ├── CMakeLists.txt
│   │   ├── include/openvideosr/media/
│   │   │   ├── PixelFormat.h
│   │   │   ├── ColorSpace.h
│   │   │   ├── VideoFrame.h
│   │   │   ├── AudioChunk.h
│   │   │   ├── MediaTimestamp.h
│   │   │   ├── Epoch.h
│   │   │   ├── SegmentGrid.h
│   │   │   ├── TimeRange.h
│   │   │   ├── SourceInfo.h
│   │   │   ├── SessionId.h
│   │   │   ├── MediaPacket.h
│   │   │   └── FramePool.h
│   │   └── src/
│   │       ├── VideoFrame.cpp
│   │       └── FramePool.cpp
│   ├── imaging/
│   │   ├── CMakeLists.txt
│   │   ├── include/openvideosr/imaging/
│   │   │   ├── PixelConverter.h
│   │   │   ├── ColorConverter.h
│   │   │   ├── Resizer.h
│   │   │   └── Sharpener.h
│   │   └── src/
│   │       ├── PixelConverter.cpp
│   │       ├── ColorConverter.cpp
│   │       ├── Resizer.cpp
│   │       └── Sharpener.cpp
│   ├── protocol/
│   │   ├── CMakeLists.txt
│   │   ├── include/openvideosr/protocol/
│   │   │   ├── ProtocolLimits.h
│   │   │   ├── ProtocolError.h
│   │   │   ├── MessageType.h
│   │   │   ├── MessageHeader.h
│   │   │   ├── ControlMessages.h
│   │   │   ├── SourceInfoMessage.h
│   │   │   ├── SourceCommand.h
│   │   │   ├── SourceState.h
│   │   │   ├── MessageParser.h
│   │   │   └── MessageSerializer.h
│   │   └── src/
│   │       ├── BinaryReader.h
│   │       ├── BinaryWriter.h
│   │       ├── ControlMessages.cpp
│   │       ├── MessageParser.cpp
│   │       └── MessageSerializer.cpp
│   ├── infra/
│   │   ├── CMakeLists.txt
│   │   ├── include/openvideosr/infra/
│   │   │   ├── logging/       Logger.h, LogLevel.h
│   │   │   ├── configuration/ AppConfig.h, ConfigLoader.h, ConfigValidator.h
│   │   │   ├── metrics/       MetricsRegistry.h, MetricsSnapshot.h, StageTimer.h
│   │   │   ├── paths/         AppPaths.h
│   │   │   └── platform/      GpuInfo.h
│   │   └── src/
│   │       ├── logging/Logger.cpp
│   │       ├── configuration/ConfigLoader.cpp, ConfigValidator.cpp
│   │       ├── metrics/MetricsRegistry.cpp
│   │       ├── paths/AppPaths.cpp
│   │       └── platform/Win32GpuInfo.cpp, LinuxGpuInfo.cpp
│   ├── modelhub/
│   │   ├── CMakeLists.txt
│   │   ├── include/openvideosr/modelhub/
│   │   │   ├── ModelInfo.h
│   │   │   ├── ContentProfile.h
│   │   │   ├── ProfileDefaults.h
│   │   │   ├── ModelManifest.h
│   │   │   ├── ModelRegistry.h
│   │   │   └── ModelVerifier.h
│   │   └── src/
│   │       ├── ModelManifest.cpp
│   │       ├── ModelRegistry.cpp
│   │       ├── ProfileDefaults.cpp
│   │       └── ModelVerifier.cpp
│   ├── inference/
│   │   ├── CMakeLists.txt
│   │   ├── include/openvideosr/inference/
│   │   │   ├── IUpscaler.h
│   │   │   ├── TemporalSpec.h
│   │   │   ├── TemporalWindow.h
│   │   │   ├── TileRunner.h
│   │   │   ├── ExecutionProviderSelector.h
│   │   │   └── UpscalerFactory.h
│   │   ├── src/
│   │   │   ├── TemporalWindow.cpp
│   │   │   ├── TileRunner.cpp
│   │   │   ├── ExecutionProviderSelector.cpp
│   │   │   └── UpscalerFactory.cpp
│   │   └── backends/
│   │       ├── classic/
│   │       │   ├── ClassicUpscaler.h
│   │       │   └── ClassicUpscaler.cpp
│   │       ├── ort/                       (option OVSR_ENABLE_ORT)
│   │       │   ├── CMakeLists.txt
│   │       │   ├── OrtSessionFactory.h / .cpp
│   │       │   ├── OrtProviderConfig.h / .cpp
│   │       │   ├── OrtEngineCache.h / .cpp
│   │       │   ├── OrtTensorBinding.h / .cpp
│   │       │   ├── OrtPreprocess.h / .cpp
│   │       │   └── OrtUpscaler.h / .cpp
│   │       └── process/                   (later; option OVSR_ENABLE_WORKERS)
│   │           ├── CMakeLists.txt
│   │           ├── IWorkerProcess.h
│   │           ├── WorkerSupervisor.h / .cpp
│   │           ├── ProcessUpscaler.h / .cpp
│   │           ├── FolderBatchUpscaler.h / .cpp
│   │           └── platform/
│   │               ├── Win32WorkerProcess.h / .cpp
│   │               └── PosixWorkerProcess.h / .cpp
│   ├── planning/
│   │   ├── CMakeLists.txt
│   │   ├── include/openvideosr/planning/
│   │   │   ├── Resolution.h
│   │   │   ├── UpscalePlan.h
│   │   │   └── ScalePlanner.h
│   │   └── src/
│   │       └── ScalePlanner.cpp
│   ├── pipeline/                          (data plane: frames in, segments out)
│   │   ├── CMakeLists.txt
│   │   ├── include/openvideosr/pipeline/
│   │   │   ├── OverflowPolicy.h
│   │   │   ├── BoundedQueue.h
│   │   │   ├── Stage.h
│   │   │   ├── IMediaSource.h
│   │   │   ├── IFrameEncoder.h
│   │   │   ├── IAudioEncoder.h
│   │   │   ├── ISegmentSink.h
│   │   │   ├── RunConfig.h
│   │   │   ├── RunState.h
│   │   │   ├── IPipelineObserver.h
│   │   │   ├── EpochTracker.h
│   │   │   ├── PipelineRunner.h
│   │   │   └── stages/
│   │   │       ├── IngestStage.h
│   │   │       ├── DecodeStage.h          (later)
│   │   │       ├── InferenceStage.h
│   │   │       ├── PostprocessStage.h
│   │   │       ├── VideoEncodeStage.h
│   │   │       ├── AudioEncodeStage.h
│   │   │       └── SegmentAssemblerStage.h
│   │   └── src/
│   │       ├── EpochTracker.cpp
│   │       ├── PipelineRunner.cpp
│   │       └── stages/  (one .cpp per stage header)
│   ├── session/                           (control plane: session, source, save)
│   │   ├── CMakeLists.txt
│   │   ├── include/openvideosr/session/
│   │   │   ├── SessionController.h
│   │   │   ├── SessionStatus.h
│   │   │   ├── ISessionObserver.h
│   │   │   ├── SessionManager.h
│   │   │   ├── SourceDirector.h
│   │   │   ├── ISourceRemote.h
│   │   │   ├── ISourceEvents.h
│   │   │   ├── IngestPolicy.h
│   │   │   ├── IngestPlanner.h
│   │   │   ├── PrebufferGate.h
│   │   │   ├── ThroughputMonitor.h
│   │   │   ├── ReconfigureCommand.h
│   │   │   ├── storage/
│   │   │   │   ├── ISessionStore.h
│   │   │   │   ├── ICoverageProvider.h
│   │   │   │   └── ISessionExporter.h
│   │   │   └── playback/
│   │   │       ├── ISegmentCatalog.h
│   │   │       └── ISegmentDecoder.h      (later; only if the custom player is chosen)
│   │   └── src/
│   │       ├── SessionController.cpp
│   │       ├── SessionManager.cpp
│   │       ├── SourceDirector.cpp
│   │       ├── IngestPlanner.cpp
│   │       ├── PrebufferGate.cpp
│   │       └── ThroughputMonitor.cpp
│   ├── cache/
│   │   ├── CMakeLists.txt
│   │   ├── include/openvideosr/cache/
│   │   │   ├── CachePaths.h
│   │   │   ├── CoverageMap.h
│   │   │   ├── DiskBudget.h
│   │   │   ├── SessionLock.h
│   │   │   ├── SessionCache.h
│   │   │   └── SessionCleaner.h
│   │   └── src/
│   │       ├── CachePaths.cpp
│   │       ├── CoverageMap.cpp
│   │       ├── DiskBudget.cpp
│   │       ├── SessionLock.cpp
│   │       ├── SessionCache.cpp
│   │       └── SessionCleaner.cpp
│   ├── transport/
│   │   ├── CMakeLists.txt
│   │   ├── include/openvideosr/transport/
│   │   │   ├── IConnection.h
│   │   │   ├── ConnectionPolicy.h
│   │   │   ├── AuthToken.h
│   │   │   ├── HandshakeValidator.h
│   │   │   ├── ClientSession.h
│   │   │   ├── WebSocketServer.h
│   │   │   ├── NetworkMediaSource.h
│   │   │   └── NetworkSourceRemote.h
│   │   └── src/
│   │       ├── WebSocketConnection.h / .cpp
│   │       ├── AuthToken.cpp
│   │       ├── HandshakeValidator.cpp
│   │       ├── ClientSession.cpp
│   │       ├── WebSocketServer.cpp
│   │       ├── NetworkMediaSource.cpp
│   │       └── NetworkSourceRemote.cpp
│   └── mediaio/
│       ├── CMakeLists.txt
│       ├── include/openvideosr/mediaio/
│       │   ├── VideoEncoder.h
│       │   ├── AudioEncoder.h
│       │   ├── EncoderSelector.h
│       │   ├── Muxer.h
│       │   ├── SegmentWriter.h
│       │   ├── CacheSegmentSink.h
│       │   ├── CacheCoverageAdapter.h
│       │   ├── CacheSessionAdapter.h
│       │   ├── CacheSegmentCatalog.h
│       │   ├── PlaylistBuilder.h
│       │   ├── SegmentConcatenator.h
│       │   ├── SessionExporter.h
│       │   ├── SegmentDecoder.h           (later; only if the custom player is chosen)
│       │   ├── FileMediaSource.h
│       │   └── FileMediaSink.h
│       └── src/
│           ├── FfmpegUtil.h
│           └── (one .cpp per public header)
│
├── workers/                              (later)
│   ├── CMakeLists.txt
│   ├── README.md
│   ├── common/
│   │   ├── CMakeLists.txt
│   │   ├── WorkerProtocol.h
│   │   └── StdioFraming.h
│   └── ort-worker/
│       ├── CMakeLists.txt
│       ├── main.cpp
│       └── OrtRunner.h / .cpp
│
├── ui/
│   ├── CMakeLists.txt
│   ├── windows/
│   │   ├── MainWindow.h / .cpp
│   │   ├── SettingsDialog.h / .cpp
│   │   ├── SaveDialog.h / .cpp
│   │   ├── PausePrompt.h / .cpp
│   │   ├── SaveBeforeCloseDialog.h / .cpp
│   │   └── PairingDialog.h / .cpp
│   ├── widgets/
│   │   ├── ContentProfilePicker.h / .cpp
│   │   ├── ModelPicker.h / .cpp
│   │   ├── ResolutionPicker.h / .cpp
│   │   ├── CoverageBar.h / .cpp
│   │   ├── StatsPanel.h / .cpp
│   │   └── ConnectionPanel.h / .cpp
│   ├── player/
│   │   ├── PlayerController.h / .cpp
│   │   ├── SegmentFeeder.h / .cpp
│   │   ├── PlayheadPublisher.h / .cpp
│   │   └── BufferIndicator.h / .cpp
│   ├── viewmodels/
│   │   ├── MainViewModel.h / .cpp
│   │   ├── StatsViewModel.h / .cpp
│   │   ├── SettingsViewModel.h / .cpp
│   │   ├── ModelSelectionViewModel.h / .cpp
│   │   └── SaveViewModel.h / .cpp
│   ├── adapters/
│   │   └── QtSessionObserver.h / .cpp
│   └── resources/
│       ├── resources.qrc
│       ├── icons/
│       └── styles/dark.qss
│
├── extension/
│   ├── manifest.json
│   ├── package.json
│   ├── eslint.config.js
│   ├── src/
│   │   ├── background/   serviceWorker.js, TabSessionManager.js
│   │   ├── offscreen/    offscreen.html, offscreen.js
│   │   ├── content/      contentScript.js, VideoElementDetector.js, SourceInfoReporter.js, DrmDetector.js
│   │   ├── control/      SourceCommandHandler.js, PauseWatcher.js
│   │   ├── capture/      ICaptureStrategy.js, ElementCapture.js, TabCapture.js, AudioCapture.js,
│   │   │                 MediaTimeMapper.js, FrameEncoder.js, CaptureWorker.js
│   │   ├── transport/    WebSocketClient.js, SendQueue.js, ReconnectPolicy.js
│   │   ├── protocol/     ProtocolConstants.js, MessageTypes.js, MessageEncoder.js, MessageDecoder.js
│   │   ├── storage/      Settings.js
│   │   └── popup/        popup.html, popup.js, popup.css
│   └── tests/
│       ├── MessageEncoder.test.js
│       ├── MessageDecoder.test.js
│       ├── GoldenVectors.test.js
│       ├── SendQueue.test.js
│       ├── MediaTimeMapper.test.js
│       └── PauseWatcher.test.js
│
├── models/
│   ├── README.md
│   ├── manifest.json
│   ├── profiles.json
│   ├── licenses/
│   └── .gitignore
│
├── tools/
│   ├── model/
│   │   ├── requirements.txt
│   │   ├── export_realesrgan_to_onnx.py
│   │   ├── export_nanovsr_to_onnx.py
│   │   ├── export_fixed_shapes.py
│   │   ├── quantize_fp16.py
│   │   └── validate_onnx.py
│   ├── eval/             make_test_clips.ps1, make_test_clips.sh, compute_metrics.py
│   ├── protocol/         generate_golden_vectors.py
│   ├── specs/            specs.py (new, status, check)
│   └── scripts/          setup-dev.ps1, setup-dev.sh, download-models.ps1, download-models.sh,
│                         download-onnxruntime.ps1, download-onnxruntime.sh
│
├── spikes/
│   ├── README.md                         (one line per spike: question, owner, result, link to ADR)
│   ├── model-speed-3060/
│   ├── muted-tab-capture/
│   ├── qt-growing-fmp4/
│   └── ffmpeg-segment-writer/
│
├── packaging/
│   ├── README.md
│   ├── windows/          deploy.ps1 (copies Qt, FFmpeg and ONNX Runtime DLLs), installer config
│   └── linux/            deploy.sh, AppImage or archive config
│
├── benchmarks/
│   ├── CMakeLists.txt
│   ├── README.md
│   ├── bench_bounded_queue.cpp
│   ├── bench_frame_pool.cpp
│   ├── bench_pixel_converter.cpp
│   ├── bench_resizer.cpp
│   ├── bench_tile_runner.cpp
│   ├── bench_inference.cpp
│   ├── bench_encoder.cpp
│   └── bench_pipeline.cpp
│
├── tests/
│   ├── CMakeLists.txt
│   ├── support/          (library ovsr::testsupport)
│   │                     FakeTimeSource, FakeUpscaler, FakeMediaSource, FakeFrameEncoder, FakeAudioEncoder,
│   │                     FakeSegmentSink, FakeCoverageProvider, FakeSessionStore, FakeSessionExporter,
│   │                     FakeSegmentCatalog, FakeSourceRemote, FakeWorkerProcess, InMemoryConnection, TestFrames
│   ├── unit/             base/, media/, imaging/, protocol/, infra/, modelhub/, inference/, planning/,
│   │                     pipeline/, session/, cache/, transport/, mediaio/, ui/
│   ├── integration/      WalkingSkeletonTests, PipelineEndToEndTests, SeekAndEpochTests, SeekBackNoReprocessTests,
│   │                     GapFillTests, PauseAndBackpressureTests, SessionEndCleansUpTests, SaveBeforeCloseTests,
│   │                     SaveExportTests, CrashLeftoverCleanupTests, WebSocketRoundTripTests, FileToFileCliTests
│   └── testdata/         protocol/, models/, video/
│
├── docs/
│   ├── architecture.md
│   ├── pipeline-and-threading.md
│   ├── session-and-source-control.md
│   ├── session-cache-and-saving.md
│   ├── media-protocol.md
│   ├── color-and-pixel-formats.md
│   ├── model-catalog.md
│   ├── content-profiles.md
│   ├── encoding-and-containers.md
│   ├── throughput-and-buffering.md
│   ├── security-model.md
│   ├── extension-capture.md
│   ├── licensing.md
│   ├── building.md
│   ├── packaging.md
│   ├── testing-strategy.md
│   └── decisions/        ADR-0000-template.md … (one ADR per decision D1–D19 and per spike result)
│
├── third_party/
│   └── README.md
└── build/                                (generated)
```

---

## 4. Folder-by-folder explanation

### 4.1 Root files

| File | Purpose |
|---|---|
| `CMakeLists.txt` | Root build file. Sets the project name and C++23, includes the modules in `cmake/`, declares options, and calls `add_subdirectory()` for `libs`, `apps`, `workers`, `ui`, `benchmarks` and `tests` (guarded by options). Contains no implementation code |
| `CMakePresets.json` | Configure/build/test presets for both operating systems (`windows-ninja-debug`, `windows-ninja-release`, `linux-ninja-debug`, `linux-ninja-release`, plus `ci-*` presets without GPU providers) using Ninja and the vcpkg toolchain file |
| `vcpkg.json` | Manifest of C++ dependencies (WebSocket library, FFmpeg with LGPL features only, logging, JSON, test and benchmark frameworks). ONNX Runtime with GPU providers and Qt may come from prebuilt packages instead (see `FindOnnxRuntime.cmake` and `docs/building.md`) |
| `vcpkg-configuration.json` | Pins the vcpkg baseline so dependency versions are reproducible |
| `README.md` | Short introduction, prerequisites, build and run commands |
| `Structure.md` | This document |
| `ProjectUnderstanding.md` | Purpose, behavior, models, encoding, devices and roadmap |
| `AGENTS.md` | Instructions for every AI coding agent: what to read first, build and test commands, rules, what never to do, definition of done. Tool-neutral, so Claude Code, Copilot, Cursor, Codex and others read the same rules |
| `CLAUDE.md` | One import line (`@AGENTS.md`) plus Claude-only notes, so the rules are written once |
| `LICENSE`, `NOTICE` | Apache License 2.0 and the attribution notice |
| `THIRD_PARTY_LICENSES.md` | Licenses of dependencies (FFmpeg build type, Qt, ONNX Runtime, encoders) |
| `.gitignore` | Excludes `build/`, IDE settings, logs, `config/local.json`, model weights, `.claude/settings.local.json` |
| `.gitattributes`, `.editorconfig` | Line endings, binary handling, basic editor settings |
| `.clang-format`, `.clang-tidy` | Formatting and static-analysis rules enforced in CI |
| `.github/CODEOWNERS` | Maps each folder to its workstream owner (section 12.1 of `ProjectUnderstanding.md`), so reviews go to the right person automatically. `CompositionRoot` has a single owner. `specs/principles.md`, `AGENTS.md` and `.claude/` require review by all workstream leads, because they change how everyone (and every agent) works |
| `.github/pull_request_template.md` | Checklist: spec and task ID (or "no spec" with a reason), requirements covered, tests added first, fake added for new interfaces, dependency rules respected, docs/ADR updated, licenses recorded, whether an AI agent wrote it and a person read every line |
| `.github/workflows/ci-cpp.yml` | Configure, build and run `unit`, `integration` and `model` tests (with sanitizers) on Windows and Linux for every push. `gpu` tests are excluded |
| `.github/workflows/ci-extension.yml` | Install, lint and test the extension |
| `.github/workflows/ci-specs.yml` | Runs `tools/specs/specs.py check` when specs, tests or the tool change. Passes when no specs exist |

### 4.2 `cmake/`

| File | Purpose |
|---|---|
| `OvsrOptions.cmake` | Options: `OVSR_ENABLE_ORT`, `OVSR_ENABLE_WORKERS`, `OVSR_BUILD_UI`, `OVSR_BUILD_TESTS`, `OVSR_BUILD_BENCHMARKS` |
| `OvsrAddLibrary.cmake` | `ovsr_add_library(name SOURCES … PUBLIC_DEPS … PRIVATE_DEPS …)`: creates the target and its `ovsr::name` alias, include paths (public `include/`, private `src/`) and warnings |
| `CompilerWarnings.cmake` | One shared set of warning flags for MSVC, Clang and GCC |
| `Sanitizers.cmake` | Optional address, undefined and thread sanitizers for test builds |
| `Testing.cmake` | `ovsr_add_test(...)` and CTest labels (`unit`, `integration`, `model`, `gpu`) |
| `FindOnnxRuntime.cmake` | Locates ONNX Runtime from vcpkg **or** from a prebuilt package pointed to by `OVSR_ORT_ROOT`, because the GPU and AMD plugin providers are often distributed as separate prebuilt packages |
| `OvsrInstall.cmake` | Install rules: executables, `config/`, `models/manifest.json` and `profiles.json`, and the shared libraries that must ship next to the app |

### 4.3 `config/`

| File | Purpose |
|---|---|
| `default.json` | Committed defaults: server port, queue sizes, segment length, container (fragmented MP4), encoder order (H.264 hardware first), audio codec, start-buffer length, cache folder (inside the OS temporary location), cache budget (default 5 GB), engine-cache folder (inside the user cache location, kept between runs), execution provider order per platform and GPU vendor, log level |
| `local.example.json` | Template for per-machine overrides; the copy `local.json` is git-ignored and holds the auth token |
| `config.schema.json` | JSON schema used by `ConfigValidator` and by editors |

### 4.4 `apps/`

| Path | Purpose |
|---|---|
| `apps/CMakeLists.txt` | Adds the app subfolders |
| `openvideosr-gui/main.cpp` | Entry point: checks the single-instance guard, creates the Qt application, builds the composition root, runs the event loop |
| `openvideosr-gui/Application.h/.cpp` | Startup and shutdown order, signal handling, asks to save unsaved video before exit (then deletes the session cache), owns top-level objects |
| `openvideosr-gui/SingleInstanceGuard.h/.cpp` | Ensures only one GUI instance runs. A second instance would fail to bind the port, and its `SessionCleaner` could delete the first instance's live cache |
| `openvideosr-gui/CompositionRoot.h/.cpp` | **The only place that knows concrete classes.** Creates the model registry, provider selector, upscaler factory, session cache and its adapters, encoders, pipeline runner, session controller, transport server and UI, and connects them through interfaces |
| `openvideosr-cli/main.cpp` | Headless entry point with subcommands (`upscale`, `bench`, `list-models`) |
| `openvideosr-cli/CliOptions.h/.cpp` | Command-line parsing and validation |
| `openvideosr-cli/CliCompositionRoot.h/.cpp` | Wires file source → pipeline → file sink without Qt, the network or the session cache |
| `openvideosr-mobile/*` | (later) Qt Android/iOS app that uses a file or URL source instead of the extension |

### 4.5 `libs/base/` — foundations (depends on nothing)

| File | Purpose |
|---|---|
| `Error.h` | Error code enum and `Error` struct (code, message, context) |
| `Result.h` | `Result<T>` alias for `std::expected<T, Error>` |
| `Platform.h` | OS (Windows, Linux) and architecture detection macros |
| `StrongId.h` | Template for typed identifiers and counters, so a session id, an epoch and a sequence number cannot be mixed up |
| `ITimeSource.h` | Interface returning the current time; injected wherever time matters |
| `SteadyTimeSource.h` | Real implementation using the steady clock |

### 4.6 `libs/media/` — domain types (depends on `base`)

| File | Purpose |
|---|---|
| `PixelFormat.h` | Supported formats (I420, NV12, RGB24, RGBA, planar float RGB) and plane size/stride helpers |
| `ColorSpace.h` | Color matrix (BT.601, BT.709), range (limited, full) and transfer. Carried by every frame so conversions and encoder tags are correct |
| `VideoFrame.h` | Immutable frame: size, format, color space, planes, strides, media time, epoch, sequence number. Memory comes from the pool |
| `AudioChunk.h` | Audio samples with rate, channels, sample format and media time |
| `MediaTimestamp.h` | Microsecond time type and rescaling helpers shared by audio and video |
| `Epoch.h` | Strong type for the epoch counter |
| `SegmentGrid.h` | Fixed time grid for output segments (for example 4 s): media time ↔ segment index |
| `TimeRange.h` | Half-open media-time interval; shared by coverage, planning of gaps and the UI |
| `SourceInfo.h` | What is known about the source video: duration (or live), native size, frame rate, title. Needed by the coverage bar, the throughput monitor, the planner and the Save file name |
| `SessionId.h` | Identifier of one session; used by `session`, `cache` and `mediaio`, which do not depend on each other |
| `MediaPacket.h` | `variant<VideoFramePtr, AudioChunk>`; the unit that flows into the pipeline |
| `FramePool.h` (+ `.cpp`) | Pre-allocated frame buffers; frames return to the pool when released |

### 4.7 `libs/imaging/` — CPU image processing (depends on `base`, `media`)

| File | Purpose |
|---|---|
| `PixelConverter.h` | Conversions between pixel layouts (I420, NV12, RGB, planar float); fallback path and ground truth in tests |
| `ColorConverter.h` | RGB ↔ YUV with the frame's matrix and range, so colors do not shift between a 360p (often BT.601) source and a 1080p (BT.709) output |
| `Resizer.h` | Exact final resize (Lanczos, also bilinear for tests) |
| `Sharpener.h` | Unsharp-mask sharpening; the screen/text baseline and the CPU-only mode use "high-quality scaling plus sharpening" |

### 4.8 `libs/protocol/` — wire format (depends on `base`, `media`)

| File | Purpose |
|---|---|
| `ProtocolLimits.h` | Maximum payload size, frame dimensions and message rates; checked before any allocation |
| `ProtocolError.h` | Parser/validator error codes |
| `MessageType.h` | Enum of all message kinds |
| `MessageHeader.h` | Header fields (magic, version, type, flags, epoch, sequence, media time, payload size) |
| `ControlMessages.h` | Payloads for Hello, HelloAck, Config, Stats, BufferStatus, Error, Goodbye |
| `SourceInfoMessage.h` | Extension → app: duration or live flag, native video size, frame rate, title. Sent at session start and when it changes |
| `SourceCommand.h` | App → extension: Play, Pause, Seek (aligned to the segment grid), SetRate |
| `SourceState.h` | Extension → app: playing, paused by page, ended, source changed, protected content |
| `MessageParser.h`, `MessageSerializer.h` | Bounds-checked parsing and building of messages |
| `src/BinaryReader.h`, `BinaryWriter.h` | Private little-endian readers/writers with bounds checks; the only code that touches raw bytes |

### 4.9 `libs/infra/` — technical utilities (depends on `base`)

| Path | Purpose |
|---|---|
| `logging/Logger.h`, `LogLevel.h` | Logging facade (levels, sinks, optional file output) |
| `configuration/AppConfig.h` | Typed settings structure |
| `configuration/ConfigLoader.h` | Loads `default.json`, then `local.json`, then environment overrides |
| `configuration/ConfigValidator.h` | Validates settings against limits and the schema |
| `metrics/MetricsRegistry.h`, `MetricsSnapshot.h`, `StageTimer.h` | Counters, gauges, latency histograms; immutable snapshots; RAII scope timer |
| `paths/AppPaths.h` | One place that resolves OS locations: temporary root (session cache), user cache (compiled model engines), config folder, log folder, installed data folder |
| `platform/GpuInfo.h` | Lists GPUs with vendor and memory (DXGI on Windows, sysfs on Linux). The provider selector needs the vendor to pick its ordered list. This is detection only, not calibration |

### 4.10 `libs/modelhub/` — models as data (depends on `base`, `infra`)

| File | Purpose |
|---|---|
| `ModelInfo.h` | Everything about one model: id, name, file, native scale, input convention, temporal window, tiling, shapes, precision, preferred providers, profiles, license |
| `ContentProfile.h` | Profiles (anime, live, screen, quality), chosen manually by the user |
| `ProfileDefaults.h` | Reads `models/profiles.json`: default model per profile |
| `ModelManifest.h` | Parses and validates `models/manifest.json` |
| `ModelRegistry.h` | Lists, filters (by profile, available file) and looks up models |
| `ModelVerifier.h` | Checks that files exist, checksums match and a license record is present |

### 4.11 `libs/inference/` — upscaling (depends on `base`, `media`, `imaging`, `infra`, `modelhub`)

| File | Purpose |
|---|---|
| `IUpscaler.h` | Streaming interface: `open`, `submit`, `poll`, `reset(epoch)`, `flush`, `temporal()`. Takes and returns `VideoFrame`s; **each backend owns its own tensor conversion and normalization**, so a GPU backend can do it on the GPU |
| `TemporalSpec.h`, `TemporalWindow.h` | Past/future frame counts; sliding window with edge padding and reset, shared by all backends |
| `TileRunner.h` | Splits large inputs into overlapping tiles, runs them, blends the result (VRAM control) |
| `ExecutionProviderSelector.h` | Reads which providers ONNX Runtime reports, applies the ordered list for the platform and GPU vendor (from `GpuInfo` and the config), honors a user override, and falls back. No benchmarking |
| `UpscalerFactory.h` | Creates the right `IUpscaler` for a model and plan |
| `backends/classic/ClassicUpscaler` | Non-AI upscaler (bilinear or Lanczos, optional sharpening) built on `imaging`. Used as the CPU-only mode, the screen/text baseline, the quality baseline in evaluations, and the deterministic backend in integration tests |
| `backends/ort/*` | **Default real backend**: in-process ONNX Runtime. Session creation, provider options, device-memory tensor binding, preprocessing, `OrtUpscaler` |
| `backends/ort/OrtEngineCache` | Stores compiled engines (TensorRT, MIGraphX) in the user cache location so the one-time compile is not repeated at every start. Separate from the session cache, which is deleted |
| `backends/process/*` | (later) Backend that talks to worker executables |

### 4.12 `libs/planning/` — resolution plans (depends on `base`, `media`, `modelhub`)

| File | Purpose |
|---|---|
| `Resolution.h` | Width/height type with aspect-ratio and even-size helpers |
| `UpscalePlan.h` | Chosen model, native scale, model output size, target size, final resize |
| `ScalePlanner.h` | Turns (source info, target size, model) into an `UpscalePlan` or an error |

### 4.13 `libs/pipeline/` — data plane (depends on `base`, `media`, `imaging`, `infra`, `inference`, `planning`)

The pipeline only moves frames: packets in, finished segments out. It knows nothing about sessions, the browser tab, the cache or saving.

| File | Purpose |
|---|---|
| `OverflowPolicy.h`, `BoundedQueue.h` | Overflow policy enum; thread-safe bounded queue with stop support |
| `Stage.h` | Base for a stage: owns a thread, an input queue, start/stop |
| `IMediaSource.h` | Produces `MediaPacket`s (network or file) |
| `IFrameEncoder.h` | Turns frames into encoded video; supports forcing a keyframe at each grid boundary |
| `IAudioEncoder.h` | Turns raw audio into an encoded stream that MP4 can hold |
| `ISegmentSink.h` | Receives finished, grid-aligned segments |
| `RunConfig.h` | Queue sizes, segment grid, plan, encoder settings for one run |
| `RunState.h` | Idle, running, flushing, stopped, error |
| `IPipelineObserver.h` | Callbacks for run state, per-stage metrics and committed segments |
| `EpochTracker.h` | Advances epochs and discards stale packets |
| `PipelineRunner.h` | Starts a run at a media time with a new epoch, stops, flushes and resets, applies a new plan. Used by `session`, not by the UI |
| `stages/IngestStage` | Routes video and audio from the source into the pipeline |
| `stages/DecodeStage` | (later) For encoded input |
| `stages/InferenceStage` | Feeds the `IUpscaler` (which does its own pre-processing) and collects results |
| `stages/PostprocessStage` | Final Lanczos resize to the target and conversion to the encoder's YUV format with the correct color matrix |
| `stages/VideoEncodeStage` | Sends frames to `IFrameEncoder`, forcing keyframes on the grid |
| `stages/AudioEncodeStage` | Encodes captured audio through `IAudioEncoder`, keeping timestamps |
| `stages/SegmentAssemblerStage` | Groups encoded video and audio into grid-aligned segments, hands complete ones to `ISegmentSink`, and discards a half-finished segment when a run ends |

### 4.14 `libs/session/` — control plane (depends on `base`, `media`, `infra`, `planning`, `pipeline`)

Everything that decides *what* to process and *when*: the session lifecycle, remote control of the browser tab, ingest planning, the start buffer and Save. This is the **single facade the UI calls**.

| File | Purpose |
|---|---|
| `SessionController.h` | The UI facade: start and end a session, seek, set player paused, reconfigure, save, change cache budget. Also implements `ISourceEvents` for the transport |
| `SessionStatus.h` | Status snapshot for the UI: buffering, running, seeking, cache full, paused by page, protected content, error, plus coverage ranges and source info |
| `ISessionObserver.h` | Callbacks to the UI: status, coverage changed, "too slow", unsaved session ending |
| `SessionManager.h` | Owns the session lifecycle. If unsaved processed video exists when a session ends, it raises `onUnsavedSessionEnding` and deletes the cache only after the user answered. After a crash there is no prompt; leftovers are deleted at the next start |
| `SourceDirector.h` | Decides Play/Pause/Seek/SetRate for the browser tab from the playhead, the coverage and the cache budget, so the tab skips ranges that are already processed. Sends them through `ISourceRemote` |
| `ISourceRemote.h` | Sends commands to the source (implemented in `transport`) |
| `ISourceEvents.h` | Receives source info and state from the source (playing, paused by page, ended, source changed, protected) |
| `IngestPolicy.h` | When ingestion pauses (cache budget reached) and resumes. No maximum lead |
| `IngestPlanner.h` | Which time range to process next: the playhead's gap first, then later gaps, then the end |
| `PrebufferGate.h` | Holds playback start until a configured number of seconds of output exist |
| `ThroughputMonitor.h` | Compares measured processing fps with the source fps (from `SourceInfo`) and raises "too slow" |
| `ReconfigureCommand.h` | A model or target change: discard old segments and restart from the playhead |
| `storage/ISessionStore.h` | Create and delete a session's cache |
| `storage/ICoverageProvider.h` | What is already processed |
| `storage/ISessionExporter.h` | The Save action: turn the processed segments into one file |
| `playback/ISegmentCatalog.h` | What the player can play: the ordered list of committed segments with gaps, and change notifications |
| `playback/ISegmentDecoder.h` | (later) Decodes segments to frames, only if the custom player wins the phase-4 spike |

### 4.15 `libs/cache/` — temporary session cache (depends on `base`, `media`, `infra`)

Holds the processed segments of the **current session** so seeking back never repeats work. Deleted when the session ends unless the user saved. Pure storage logic: no FFmpeg, no Qt, no networking.

| File | Purpose |
|---|---|
| `CachePaths.h` | Disk layout: a cache root inside the OS temporary location (from `AppPaths`), one folder per session, a temporary subfolder for segments being written |
| `CoverageMap.h` | Interval set of processed segments: is `t` ready, where is the next gap, how far does the contiguous range extend |
| `DiskBudget.h` | Cache size limit (default 5 GB) and current usage |
| `SessionLock.h` | A lock file inside each session folder held while the session lives. `SessionCleaner` deletes only folders whose lock is not held, so a live session is never deleted |
| `SessionCache.h` | Facade: create a session, register a committed segment, query coverage, list playable ranges, delete the session |
| `SessionCleaner.h` | Deletes a session's folder at session end, and unlocked leftover folders from earlier crashes at the next start |

### 4.16 `libs/transport/` — network side (depends on `base`, `media`, `protocol`, `infra`, `pipeline`, `session`)

| File | Purpose |
|---|---|
| `IConnection.h` | Abstract byte connection so sessions can be tested without sockets |
| `ConnectionPolicy.h` | Loopback binding, allowed origin, limits, single-session rule |
| `AuthToken.h` | Generates a random token on first start, stores it through the config, and compares tokens in constant time |
| `HandshakeValidator.h` | Validates `Hello` (version, token, origin) |
| `ClientSession.h` | One client: reads and validates messages, pushes media into `NetworkMediaSource`, forwards source info and state to `ISourceEvents` |
| `WebSocketServer.h` | Starts and stops the local listener and creates sessions |
| `NetworkMediaSource.h` | `IMediaSource` fed by the client session |
| `NetworkSourceRemote.h` | `ISourceRemote` that serializes `SourceCommand`s to the client |
| `src/WebSocketConnection.*` | Private adapter from the WebSocket library to `IConnection` |

### 4.17 `libs/mediaio/` — encoding, files and saving (depends on `base`, `media`, `infra`, `pipeline`, `session`, `cache`)

| File | Purpose |
|---|---|
| `VideoEncoder.h` | `IFrameEncoder` with FFmpeg; writes color tags from the frame's `ColorSpace` |
| `AudioEncoder.h` | `IAudioEncoder` with FFmpeg (resampling included). Codec choice (FFmpeg's built-in AAC or Opus) is recorded in `docs/encoding-and-containers.md`; verify its license for the LGPL build |
| `EncoderSelector.h` | Chooses the video encoder from an ordered list by trying to open each one: H.264 hardware (NVENC, AMF), then software H.264; HEVC and AV1 added later. No benchmarking |
| `Muxer.h` | Combines video and audio with matching timestamps |
| `SegmentWriter.h` | Writes one grid-aligned segment to a temporary file as a fragmented-MP4 segment that starts on a keyframe and plays on its own |
| `CacheSegmentSink.h` | `ISegmentSink`: moves a finished segment into the session folder with an atomic rename and registers it in `SessionCache` |
| `CacheCoverageAdapter.h` | `ICoverageProvider` over `SessionCache` |
| `CacheSessionAdapter.h` | `ISessionStore`: creates (and locks) and deletes the session cache |
| `CacheSegmentCatalog.h` | `ISegmentCatalog` over `SessionCache` and `PlaylistBuilder`, for the player |
| `PlaylistBuilder.h` | Builds the playlist of processed segments with gaps marked |
| `SegmentConcatenator.h` | Joins segments into one file without re-encoding |
| `SessionExporter.h` | `ISessionExporter`: writes an ordinary video file where the user chose |
| `SegmentDecoder.h` | (later) `ISegmentDecoder`, only if the custom player is chosen |
| `FileMediaSource.h`, `FileMediaSink.h` | Read a video file as a source (CLI and tests); write the output to a single file |
| `src/FfmpegUtil.h` | Private FFmpeg helpers and RAII wrappers |

### 4.18 `workers/` — optional model-runner executables (later)

| Path | Purpose |
|---|---|
| `README.md` | When to use workers, how to add one, license notes |
| `common/WorkerProtocol.h` | Binary message format between app and worker (target `ovsr::workerproto`, shared with `libs/inference/backends/process`) |
| `common/StdioFraming.h` | Length-prefixed reading/writing on stdin/stdout |
| `ort-worker/*` | Worker executable that runs an ONNX model with ONNX Runtime |

### 4.19 `ui/` — Qt interface (target `ovsr::ui`; depends on `session`, `planning`, `modelhub`, `infra`, `media`)

| Path | Purpose |
|---|---|
| `windows/MainWindow` | Main window layout, including the Save button |
| `windows/SettingsDialog` | Server port, cache budget, encoder and execution provider choice |
| `windows/SaveDialog` | Destination and format, progress, and handling an incomplete video |
| `windows/PausePrompt` | Shown when the browser video is paused: explains that upscaling stops and offers to keep the tab playing muted |
| `windows/SaveBeforeCloseDialog` | Save, Discard, or Cancel (Cancel only when the app itself is closing) |
| `windows/PairingDialog` | Shows the auth token and port so the user can paste them into the extension once |
| `widgets/*` | Content profile, model and resolution pickers; coverage bar; stats panel; connection panel |
| `player/PlayerController` | Play, pause, seek, speed. Seeks inside processed ranges are instant; seeks into gaps go to `SessionController` |
| `player/SegmentFeeder` | Gives the player the growing playlist from `ISegmentCatalog` |
| `player/PlayheadPublisher` | Reports the playhead to `SessionController` |
| `player/BufferIndicator` | Player-side buffer state |
| `viewmodels/*` | UI state and commands, separate from widget layout (main, stats, settings, model selection, save). Tested with Qt Test in `tests/unit/ui` |
| `adapters/QtSessionObserver` | Moves `ISessionObserver` callbacks onto the UI thread as Qt signals |
| `resources/*` | Resource file, icons, stylesheets |

### 4.20 `extension/` — Chrome extension (separate JavaScript project)

| Path | Purpose |
|---|---|
| `manifest.json` | Extension metadata and minimal permissions |
| `package.json`, `eslint.config.js` | Tooling, scripts, lint rules |
| `background/serviceWorker.js` | Thin coordinator: start/stop, messaging |
| `background/TabSessionManager.js` | Tracks which tab is the active source and reports tab close |
| `offscreen/offscreen.html/.js` | Hosts the socket (and tab capture if that strategy is chosen); the service worker is suspended too often to do it |
| `content/contentScript.js` | Runs in the page; finds and controls the video element |
| `content/VideoElementDetector.js` | Chooses the right `<video>` and detects source changes (for example autoplay) |
| `content/SourceInfoReporter.js` | Reports duration or live, native size, frame rate and title (the `SourceInfo` message) |
| `content/DrmDetector.js` | Detects encrypted playback so the app can explain the site cannot be captured |
| `control/SourceCommandHandler.js` | Applies Play/Pause/Seek/SetRate received from the app (renamed from `SourceController.js` so it is not confused with the C++ `SourceDirector`, which *decides* those commands) |
| `control/PauseWatcher.js` | Detects a pause the app did not cause and reports it; never resumes by itself |
| `capture/ICaptureStrategy.js` | Common interface for the two capture approaches below; the week 1–2 spike decides which one is the default |
| `capture/ElementCapture.js` | Captures frames from the `<video>` element itself, at the video's own resolution, with its media time |
| `capture/TabCapture.js` | Captures the rendered tab; may deliver the page's display size rather than the video's own resolution (verify in the spike) |
| `capture/AudioCapture.js` | Audio capture |
| `capture/MediaTimeMapper.js` | Converts capture timestamps to the video's **media time**, so seeks, pauses and stalls never corrupt the timeline |
| `capture/FrameEncoder.js` | Packages frames (YUV) for sending |
| `capture/CaptureWorker.js` | Moves capture work off the page's main thread |
| `transport/*` | WebSocket client, bounded send queue, reconnection with backoff |
| `protocol/*` | Constants, message types, encoder and decoder (mirror of the C++ side, checked by golden vectors) |
| `storage/Settings.js` | Port and token storage |
| `popup/*` | Toolbar popup UI |
| `tests/*` | Encoder/decoder, golden vectors, send queue, media-time mapper, pause watcher |

### 4.21 `models/`

| File | Purpose |
|---|---|
| `README.md` | How to obtain models, where files go, how to add one |
| `manifest.json` | All model entries (the data `modelhub` reads) |
| `profiles.json` | Default model per content profile |
| `licenses/` | One file per model: license, source URL, date checked |
| `.gitignore` | Keeps weights (`*.onnx`, `*.engine`, `*.pth`) out of Git |

### 4.22 `tools/`

| Path | Purpose |
|---|---|
| `model/*` | Export Real-ESRGAN and NanoVSR to ONNX, fixed shapes, FP16 conversion, validation against the original model |
| `eval/*` | Build low-resolution test clips (Windows and Linux); compute PSNR, SSIM, LPIPS |
| `protocol/generate_golden_vectors.py` | Generates the shared protocol test files |
| `specs/specs.py` | `new` creates `specs/NNNN-<name>/` from the templates; `status` shows each spec's phase and next step; `check` verifies requirement and task IDs, phase gates and `// Verifies:` links in tests. Python standard library only |
| `scripts/*` | Developer setup, model download, ONNX Runtime prebuilt download (PowerShell and shell) |

### 4.23 `spikes/`

| Path | Purpose |
|---|---|
| `README.md` | For each spike: the question, owner, result and the ADR that records the decision |
| `<spike>/` | Throw-away code for the four week 1–2 spikes. Not built by the root `CMakeLists.txt` and never included by `libs/`. Kept so the evidence behind decisions stays visible |

### 4.24 `packaging/`

| Path | Purpose |
|---|---|
| `windows/` | Copies the Qt, FFmpeg and ONNX Runtime shared libraries next to the executable (Qt and FFmpeg are linked dynamically for LGPL) and builds an installer or zip |
| `linux/` | The same for Linux (archive or AppImage) |
| `README.md` | How to produce a build that runs on a machine without the developer tools |

### 4.25 `benchmarks/`

| File | Measures |
|---|---|
| `bench_bounded_queue.cpp` | Queue throughput under each overflow policy |
| `bench_frame_pool.cpp` | Allocation cost with and without the pool |
| `bench_pixel_converter.cpp`, `bench_resizer.cpp` | Conversion and Lanczos resize speed |
| `bench_tile_runner.cpp` | Tiling overhead |
| `bench_inference.cpp` | Model fps and peak memory per provider (run by hand, label `gpu`) |
| `bench_encoder.cpp` | Encoder throughput and GPU contention |
| `bench_pipeline.cpp` | End-to-end fps and per-stage latency |

### 4.26 `tests/`

| Folder | Contents | Verifies |
|---|---|---|
| `support/` | Library `ovsr::testsupport`: one fake per interface, in-memory connection, test frames | Every workstream builds against the same fakes; tests run without hardware or network |
| `unit/base`, `unit/media` | Result helpers, pool, timestamps, segment grid, time ranges | Memory reuse, time-to-segment mapping |
| `unit/imaging` | Pixel and color conversion, resizer, sharpener | Correct conversions per color matrix; resize accuracy |
| `unit/protocol` | Parser, serializer, limits, golden vectors | Malformed input is rejected; C++ matches JavaScript |
| `unit/infra` | Config loader, metrics, paths | Overrides, counters, OS locations |
| `unit/modelhub`, `unit/planning` | Manifest, registry, profile defaults; scale planner | Parsing, filtering, all resolution cases |
| `unit/inference` | Classic upscaler, temporal window, tile runner, provider selector, factory | Edge padding, seams, fallback order |
| `unit/pipeline` | Queue, epoch tracker, stages, runner | Backpressure, stale-packet dropping, partial-segment handling |
| `unit/session` | Session manager, source director, ingest planner, prebuffer gate, throughput monitor, controller | Pause/resume rules, gap selection, session end, save flow |
| `unit/cache` | Coverage map, disk budget, session lock, session cache, cleaner | Interval math, budget, deletion rules, live folders never deleted |
| `unit/transport` | Auth token, handshake validator, client session | Token/origin checks, limits |
| `unit/mediaio` | Segment writer, cache sink, catalog, concatenator, encoder selector, audio encoder | Keyframe-aligned segments, atomic commit, lossless joining, encoder fallback |
| `unit/ui` | View models (Qt Test) | UI logic without widgets |
| `integration/` | Walking skeleton (all fakes, week 3), pipeline end to end, seek and epoch, seek back without reprocessing, gap filling, pause and backpressure, session end cleanup, save before close, save export, crash leftover cleanup, WebSocket round trip, file-to-file CLI | Components working together; nothing is reprocessed; nothing is left on disk unless saved |
| `testdata/` | Protocol samples, a tiny ONNX model, a tiny clip | Shared with the extension tests; ONNX and CLI tests without downloads |

### 4.27 `docs/`

| File | Purpose |
|---|---|
| `architecture.md` | Components, layers, data flow, lifecycle |
| `pipeline-and-threading.md` | Threads, queues, shutdown order |
| `session-and-source-control.md` | Session lifecycle, pause, cache budget, seek, epoch and gap-filling rules |
| `session-cache-and-saving.md` | Cache layout, locks, deletion rules and the Save action |
| `media-protocol.md` | Byte-level protocol contract |
| `color-and-pixel-formats.md` | Pixel formats at each stage, color matrices and ranges, encoder tags |
| `model-catalog.md`, `content-profiles.md` | Supported models and their status; profile definitions and defaults |
| `encoding-and-containers.md` | Video and audio codec and container decisions, encoder availability |
| `throughput-and-buffering.md` | Start buffer, formulas, disk use |
| `security-model.md` | Threats and mitigations, token pairing |
| `extension-capture.md` | Capture strategies, media-time mapping, DRM and site limits |
| `licensing.md` | Apache 2.0, FFmpeg and Qt licensing rules, model licenses |
| `building.md` | Compilers, dependencies (vcpkg and prebuilt ONNX Runtime), presets on Windows and Linux |
| `packaging.md` | Producing a runnable build for another machine |
| `testing-strategy.md` | Test levels, labels, fakes, conventions |
| `decisions/` | ADRs from `ADR-0000-template.md`: one per decision D1–D19 that needs a record, and one per spike result |

### 4.28 `third_party/` and `build/`

| Path | Purpose |
|---|---|
| `third_party/README.md` | Vendored code only when vcpkg cannot provide it; list each item and its license |
| `build/` | Generated by CMake and Ninja; safe to delete; git-ignored |

### 4.29 `specs/` — optional feature specs

A spec is a short written agreement about one feature before it is built. People and AI agents use the same files. The build never reads this folder.

| Path | Purpose |
|---|---|
| `README.md` | When to write a spec (and when not), the five phases and their approval gates, ID formats, commands, and how specs relate to `docs/` and ADRs |
| `principles.md` | The non-negotiable rules every spec and change must respect (P1–P23), each pointing to its source in this document, `ProjectUnderstanding.md` or a decision D1–D19. Changed only by team agreement with an ADR; agents may not edit it |
| `_templates/requirements.md` | Problem, scenarios, requirements in "When …, the … shall …" form with testable acceptance criteria, non-functional requirements, out of scope, related decisions, open questions |
| `_templates/design.md` | Affected libraries (checked against section 5), interfaces and fakes, threads, protocol and config changes, errors, test plan mapping every requirement to a test, ADR needed or not, alternatives, risks |
| `_templates/tasks.md` | Ordered tasks, each one pull request: requirements covered, dependencies, files, tests that prove it, status |
| `NNNN-<name>/` | One folder per feature. Each file has front matter with `status` (`draft`, `approved`, `done`, `superseded`) and `approved-by`. A phase starts only when the previous file is approved |

How the three kinds of documents differ: a **spec** is the plan for one feature and becomes history when the feature is done; `docs/` describes the system **as it is now** and is updated in the spec's last phase; an **ADR** records a decision that outlives the feature and is linked from the design.

### 4.30 `.claude/` — agent settings and skills

| Path | Purpose |
|---|---|
| `settings.json` | Shared agent permissions: build, test and spec commands are allowed; reading `config/local.json` (the auth token) and editing `specs/principles.md` are denied. Personal overrides go in the git-ignored `settings.local.json` |
| `skills/spec-driven-workflow/SKILL.md` | The workflow an agent follows: orient (read `AGENTS.md` and the principles, run `specs.py status`), find the current phase, check the gate, do one phase, then stop for human approval. Lists when to stop and ask (principle conflict, frozen interface, forbidden dependency, new dependency, unclear requirement, spike needed) |
| `skills/spec-driven-workflow/references/` | One file per phase (requirements, design, tasks, implement, verify) with steps and quality checks. The agent loads only the file for the current phase, which keeps its context small |
| `skills/add-model/`, `add-protocol-message/`, `add-pipeline-stage/` | (later) The recipes from section 7 written as agent-executable steps, for changes too small to need a spec |

Skills use the `SKILL.md` format (a name and a "when to use" description in front matter, instructions below). Agents that do not load skills automatically are pointed to the file by `AGENTS.md`.

### 4.31 How the spec workflow fits the rest of the repository

| Phase | Writes to | Checked by |
|---|---|---|
| 1 Requirements | `specs/NNNN-<name>/requirements.md` | Person approves |
| 2 Design | `design.md`; an ADR draft in `docs/decisions/` if needed | Person approves; dependency rules in section 5 |
| 3 Tasks | `tasks.md` | Person approves; `specs.py check` (every requirement has a task) |
| 4 Implement | Code in `libs/`, `ui/`, `apps/`, `extension/`; tests with `// Verifies:` | CI (`ci-cpp`, `ci-extension`, `ci-specs`), one reviewer |
| 5 Verify | `docs/`, this document if folders changed, `ProjectUnderstanding.md` if behavior changed | `specs.py check` (every requirement has a test); person sets `status: done` |

---

## 5. Dependency rules

### 5.1 Layers

A library may depend only on libraries in **lower** layers (and on the ones listed for it below). Libraries in the same layer do not depend on each other unless listed.

```text
Layer 6  apps          openvideosr-gui, openvideosr-cli          composition roots: know every concrete class
Layer 5  ui            ovsr::ui                                  talks only to session (+ read-only model/plan data)
Layer 4  adapters      transport, mediaio                        implement session/pipeline interfaces with real libraries
Layer 3  control       session                                   lifecycle, source control, ingest planning, save
Layer 2  processing    pipeline                                  stages, queues, epochs
Layer 1  domain        imaging, protocol, modelhub, inference, planning, cache
Layer 0  foundation    base, media, infra
```

### 5.2 Table

| Module | May depend on | Must not depend on |
|---|---|---|
| `base` | — | everything |
| `media` | `base` | Qt, networking, inference |
| `infra` | `base` | `media` and everything above |
| `imaging` | `base`, `media` | `inference`, `pipeline` and above |
| `protocol` | `base`, `media` | Qt, networking library |
| `modelhub` | `base`, `infra` | inference, pipeline, UI |
| `inference` | `base`, `media`, `imaging`, `infra`, `modelhub` | pipeline, session, transport, UI |
| `planning` | `base`, `media`, `modelhub` | pipeline, session, transport, UI |
| `cache` | `base`, `media`, `infra` | pipeline, session, FFmpeg, Qt, transport |
| `pipeline` | `base`, `media`, `imaging`, `infra`, `inference`, `planning` | session, transport, cache, mediaio, UI, Qt |
| `session` | `base`, `media`, `infra`, `planning`, `pipeline` | transport, cache, mediaio, UI, Qt |
| `transport` | `base`, `media`, `protocol`, `infra`, `pipeline`, `session` | mediaio, cache, UI, Qt |
| `mediaio` | `base`, `media`, `infra`, `pipeline`, `session`, `cache` | transport, UI |
| `ui` | `session`, `planning`, `modelhub`, `infra`, `media` | pipeline, cache, mediaio, transport, inference |
| `apps/*` | everything | — |

How it is enforced: each library declares its dependencies in CMake, so an illegal `#include` fails to compile. The UI can only reach `SessionController`, the planner, the model views and the player interfaces, because those are the only libraries it links. Every interface the upper layers need from storage, encoding or the network (`IFrameEncoder`, `IAudioEncoder`, `ISegmentSink`, `ISessionStore`, `ICoverageProvider`, `ISessionExporter`, `ISegmentCatalog`, `ISourceRemote`) lives in the library that uses it and is implemented in `mediaio` or `transport`. All concrete classes are wired in a composition root.

`specs/`, `.claude/`, `AGENTS.md`, `CLAUDE.md` and `tools/specs/` are outside the dependency graph: no CMake target reads them, and deleting them would not change the build. The spec workflow follows these rules; it never adds to them.

---

## 6. CMake target map

| Target | Kind | Source |
|---|---|---|
| `ovsr::base`, `media`, `imaging`, `protocol`, `infra`, `modelhub`, `inference`, `planning`, `pipeline`, `session`, `cache`, `transport`, `mediaio` | static libraries | `libs/<name>` |
| `ovsr::inference_ort` | static library (option `OVSR_ENABLE_ORT`) | `libs/inference/backends/ort` |
| `ovsr::inference_process` | static library (option `OVSR_ENABLE_WORKERS`) | `libs/inference/backends/process` |
| `ovsr::workerproto` | static library (option `OVSR_ENABLE_WORKERS`) | `workers/common` |
| `ovsr_ort_worker` | executable (option `OVSR_ENABLE_WORKERS`) | `workers/ort-worker` |
| `ovsr::ui` | static library (option `OVSR_BUILD_UI`) | `ui/` |
| `ovsr::testsupport` | static library (option `OVSR_BUILD_TESTS`) | `tests/support` |
| `openvideosr-gui`, `openvideosr-cli` | executables | `apps/*` |
| `ovsr_tests_*`, `ovsr_bench_*` | test and benchmark executables | `tests/`, `benchmarks/` |

| Option / cache variable | Default | Effect |
|---|---|---|
| `OVSR_ENABLE_ORT` | ON | Builds the ONNX Runtime backend |
| `OVSR_ORT_ROOT` | empty | Path to a prebuilt ONNX Runtime package (GPU providers); empty means use vcpkg |
| `OVSR_ENABLE_WORKERS` | OFF | Builds worker executables and the process backend |
| `OVSR_BUILD_UI` | ON | Builds the Qt UI and GUI app |
| `OVSR_BUILD_TESTS` | ON | Builds tests and fakes and registers them with CTest |
| `OVSR_BUILD_BENCHMARKS` | OFF | Builds benchmarks |

Build commands:

```powershell
# Windows
cmake --preset windows-ninja-debug
cmake --build --preset windows-ninja-debug
ctest --preset windows-ninja-debug -LE gpu
```

```bash
# Linux
cmake --preset linux-ninja-debug
cmake --build --preset linux-ninja-debug
ctest --preset linux-ninja-debug -LE gpu
```

---

## 7. Where does new code go?

| Task | Steps and files touched |
|---|---|
| Add a model | Export with a script in `tools/model/`; add an entry to `models/manifest.json`; add its license in `models/licenses/`; optionally make it a profile default in `models/profiles.json`. No C++ change if it uses the standard input convention |
| Add an inference backend | New folder `libs/inference/backends/<name>/` implementing `IUpscaler` (including its own pre/post-processing); register it in `UpscalerFactory`; add a CMake option; test with the tiny model |
| Add a pipeline stage | Header and source in `libs/pipeline/.../stages/`; insert it in `PipelineRunner`'s stage list; unit test with fake neighbors |
| Change when or what is processed | `libs/session` (`IngestPlanner`, `IngestPolicy`, `SourceDirector`); the pipeline stays unchanged |
| Add a protocol message | `MessageType.h`, a payload header, parse/serialize code in `protocol/src`, the JS mirror in `extension/src/protocol`, new golden vectors, a section in `docs/media-protocol.md` |
| Add a source command or source event | The protocol message (above), `ISourceRemote` or `ISourceEvents` in `session`, the transport implementation, the extension handler, and a fake update in `tests/support` |
| Add an encoder or container | `EncoderSelector`, `VideoEncoder`/`AudioEncoder`/`Muxer` in `libs/mediaio`; update `docs/encoding-and-containers.md` |
| Change how processed video is stored | `libs/cache` (layout, coverage, budget, locks) and `libs/mediaio` (files). `session` and `pipeline` only see interfaces |
| Add a new interface | Header in the library that uses it, implementation in an adapter library, a fake in `tests/support`, wiring in the composition root |
| Add a UI control | A widget in `ui/widgets`, state in a view model, wiring in `MainWindow`; it calls `SessionController`, never lower layers |
| Add a platform-specific feature | An interface in the owning library and Windows/Linux implementations under its `platform/` folder |
| Add a dependency | Add it to `vcpkg.json` (or `FindXxx.cmake` for prebuilt packages), link it only in the library allowed by the containment rule, record its license in `THIRD_PARTY_LICENSES.md`, and add it to `packaging/` if it ships as a shared library |
| Try something risky | A folder in `spikes/`; move the result into `libs/` only after an ADR |
| Record a decision | A new file in `docs/decisions/` from `ADR-0000-template.md` |
| Build a larger feature from a spec | `python tools/specs/specs.py new "<title>"`; fill and approve `requirements.md`, `design.md`, `tasks.md` in that order; implement one task per pull request; finish with `specs.py check` and doc updates. An AI agent does the same through `.claude/skills/spec-driven-workflow` |
| Give AI agents a new rule | One line in `AGENTS.md` (all agents). If it is a project principle, propose it for `specs/principles.md` with an ADR instead |
| Turn a recurring recipe into an agent skill | A folder `.claude/skills/<name>/` with a `SKILL.md` whose description says when to use it; keep long details in `references/` files |
| Change the spec process | `specs/README.md`, the templates, the skill and `tools/specs/specs.py` together, so the files, the agent and the CI check stay in step |

---

## 8. Creation order

The workstreams in `ProjectUnderstanding.md` (section 12) run in parallel, so phases overlap. The only hard rule is: **a library is created no earlier than the libraries it depends on**, and its interfaces and fakes exist before anyone implements them.

| Phase | Weeks | Create | Milestone |
|---|---|---|---|
| 0 Foundations and spikes | 1–2 | Root files, `cmake/`, CI, `CODEOWNERS`, `libs/base`, `libs/media`, `libs/infra`, `tests/support` (`ovsr::testsupport`), `spikes/` (four spikes), `docs/decisions/` with the first ADRs. **Interface headers frozen:** `IUpscaler`, `IMediaSource`, `IFrameEncoder`, `IAudioEncoder`, `ISegmentSink`, `ISessionStore`, `ICoverageProvider`, `ISessionExporter`, `ISegmentCatalog`, `ISourceRemote`, `ISourceEvents`, and `docs/media-protocol.md` | Spike results; interfaces frozen |
| 1 Walking skeleton and libraries | 3–6 | `libs/imaging`, `libs/modelhub`, `libs/inference` (classic backend, temporal window, tiling), `libs/planning` (single-model plans), `libs/pipeline`, `libs/cache`, `libs/mediaio` (video and audio encoders, muxer, segment writer, file source and sink), `libs/protocol`, `extension/` skeleton, `apps/openvideosr-cli`, `benchmarks/`. Week 3: the walking-skeleton integration test with fakes end to end | **M1** CLI file → upscaled MP4 |
| 2 Real model | 3–9 (parallel) | `libs/inference/backends/ort`, `OrtEngineCache`, `ExecutionProviderSelector`, `GpuInfo`, `models/`, `tools/model`, `tools/eval` | A real model on the 3060 |
| 3 Session and player | 7–9 | `libs/session`, the cache adapters and catalog in `libs/mediaio`, `libs/transport`, `ui/player`, `ui/windows` (main, save, pairing), `apps/openvideosr-gui` with `SingleInstanceGuard` | **M2** Qt player plays segments with seek-back |
| 4 Browser end to end | 10–12 | Source control end to end, `PausePrompt`, `SaveBeforeCloseDialog`, `DrmDetector`, golden vectors complete | **M3** browser → upscale → player → Save |
| 5 Features and packaging | 13–14 | Remaining widgets and view models, settings, full planner, second model and profiles, `packaging/`, `config/` polish | **M4** feature complete; runs on another machine |
| 6 Hardening | 15–16 | Tests, `docs/` fill-in, demo | Final demo |
| Later | — | `workers/`, `backends/process`, `ISegmentDecoder` + `SegmentDecoder` (only if the custom player is chosen), `DecodeStage`, `apps/openvideosr-mobile` | — |
| Any time (optional) | — | `AGENTS.md`, `CLAUDE.md`, `specs/` (README, principles, templates), `.claude/` (settings, spec-driven-workflow skill), `tools/specs/specs.py`, `ci-specs.yml`. Cheapest to add in phase 0 together with `CODEOWNERS`, but nothing else waits for them. The recipe skills (`add-model` and others) come after the first time each recipe is done by hand | — |

If the team adopts specs, the first good candidates are the features with the most cross-library rules: seek and gap filling (session, pipeline, transport, extension), Save and Save-before-close (session, mediaio, ui), and the pause prompt (extension, protocol, session, ui).

---

## 9. Deferred components (not part of the current scope)

| Component | What it would add | Where it would go |
|---|---|---|
| Capability probing and calibration | Benchmark each model on the device and cache results | `libs/capability/` (`Calibrator`, `CapabilityReport`, `CapabilityCache`, `DeviceTier`). It would reuse `infra/platform/GpuInfo` for detection |
| Feasibility and pre-buffer estimates | Green / yellow / red before playback; computed start wait | `libs/planning/FeasibilityEstimator`, `PrebufferEstimator`; `ui/widgets/FeasibilityBadge`; `ui/windows/DeviceInfoDialog`; CLI `calibrate`; `docs/device-tiers.md` |
| Automatic content detection | Pick the content profile automatically | Not planned. The user always chooses |
| Persistent library across sessions | Remembering videos between runs | Not planned. Persistence only through Save |
| ncnn (Vulkan) backend | Fallback for AMD GPUs that the ONNX Runtime AMD providers do not cover | `libs/inference/backends/ncnn/` behind `OVSR_ENABLE_NCNN`; decision pending |

Until calibration exists, `ThroughputMonitor` shows live fps against the source fps, and `ExecutionProviderSelector` uses an ordered default list (per vendor from `GpuInfo`) that the user can override in the settings.

---

## 10. Revision log: what changed and why

### 10.1 Changes that fix inconsistencies

These were contradictions inside the previous structure or between the structure and `ProjectUnderstanding.md`. Left as they were, they would have caused compile errors under the dependency rules or blocked work.

| # | Change | Why it is an improvement | Sections |
|---|---|---|---|
| 1 | `ISessionExporter` moved from `cache` to `session` | `PipelineController` was supposed to offer "save", but `pipeline` was forbidden to depend on `cache`, where the exporter interface lived. Save could not be called without breaking a rule. It also broke the convention that an interface lives with its *user*. `cache` is now pure storage with no interfaces for others | 4.14, 4.15, 5 |
| 2 | UI no longer depends on `cache`; new `ISegmentCatalog` interface | `SegmentFeeder` needed the playlist from `PlaylistBuilder` in `mediaio`, but `ui` was not allowed to depend on `mediaio`. The UI also reached into `cache` directly, contradicting "the UI talks only to `PipelineController`". Now the player reads an interface and the rule is enforced by CMake, not by discipline | 4.14, 4.17, 4.19, 5 |
| 3 | Audio encoding added (`IAudioEncoder`, `AudioEncoder`, `AudioEncodeStage` replacing `AudioPassthroughStage`) | The extension captures raw audio samples (`AudioChunk`), but MP4 can only hold encoded audio (AAC, Opus). "Passthrough" to the muxer would not produce a valid file, and no class did the encoding | 4.13, 4.17 |
| 4 | `SourceInfo` type and protocol message added | The coverage bar needs the video duration, `ThroughputMonitor` needs the source fps `p`, the planner needs the native size, live streams need a "live" flag and Save needs a file name. No message carried any of this from the extension | 4.6, 4.8, 4.20 |
| 5 | `PostprocessStage` (resize + RGB → YUV) replaces `ResizeStage`; `PreprocessStage` folded into the backend | Nothing converted the model's RGB output back to the YUV the H.264 encoder needs. And pre-processing existed twice (`PreprocessStage` and `OrtPreprocess`). Letting each backend own its tensor conversion also keeps the GPU path open, so frames do not need to go back to the CPU between stages | 4.11, 4.13 |
| 6 | Creation order rebuilt around dependencies and the 16-week schedule | The old order was impossible: `inference` (phase 1) depends on `modelhub` (phase 2); `pipeline` (phase 1) depends on `planning` (phase 3); `mediaio` (phase 1) depends on `cache` (phase 4); `protocol` was phase 5 while the browser workstream starts in week 3. The new table matches milestones M1–M4 | 8 |
| 7 | `SessionId` moved from `cache` to `media` | `session`, `cache` and `mediaio` all need it, and `session` may not depend on `cache` | 4.6 |
| 8 | `ui` becomes a normal library target `ovsr::ui` | It was `ovsr_ui`, the only target outside the `ovsr::` naming convention | 2, 6 |
| 9 | Persistent engine cache (`OrtEngineCache`, `AppPaths`) | `ProjectUnderstanding.md` says the TensorRT/MIGraphX compile step "should be cached", but there was no place for it. It must not go in the session cache, which is deleted at every session end | 4.9, 4.11 |
| 10 | GPU vendor detection (`infra/platform/GpuInfo`) | Decision D9 picks the provider list "per platform and GPU vendor", but the vendor was only detectable in the deferred calibration library. Detection is cheap; only benchmarking is deferred | 4.9, 4.11, 9 |

### 10.2 Structural improvements

| # | Change | Why it is an improvement | Sections |
|---|---|---|---|
| 11 | `pipeline` split into `pipeline` (data plane) and `session` (control plane) | The old `pipeline` held two responsibilities: moving frames (queues, stages, epochs) and deciding what to process (session lifecycle, source control, ingest planning, prebuffer, save). This breaks "one library, one responsibility", made it the largest library for one workstream, and was the root cause of fixes 1 and 2. After the split, the data plane can be finished and tested for M1 (CLI) without any session logic, and the control plane can be tested with a fake runner | 4.13, 4.14, 5 |
| 12 | `PipelineController` renamed `PipelineRunner`; the UI facade is `SessionController` | With the split, having two "controllers" would blur which one the UI calls. The name now says that the runner only runs | 4.13, 4.14 |
| 13 | New `imaging` library (pixel conversion, color conversion, Lanczos resize, sharpening) | `Resizer` sat in `inference` but runs *after* inference; `PixelConverter` sat in `media` next to plain data types. The "high-quality scaling plus sharpening" needed for the screen/text baseline and CPU-only mode had no home at all. Grouping CPU image algorithms gives one place to test and benchmark them | 4.7, 4.11 |
| 14 | `ColorSpace` carried by every frame, `ColorConverter`, color tags in the encoder | SD sources usually use the BT.601 color matrix and HD outputs BT.709. If 360p → 1080p ignores this, colors shift visibly. It is a classic bug that is cheap to prevent in the structure and hard to find later | 4.6, 4.7, 4.17 |
| 15 | `BilinearUpscaler` generalized to `ClassicUpscaler` (bilinear or Lanczos, optional sharpening) | One backend now covers the test fake, the evaluation baseline, the CPU-only mode and the screen/text baseline, instead of only the first two | 4.11 |
| 16 | `ISourceRemote` and `ISourceEvents` interfaces between `session` and `transport` | The session decides commands without knowing about WebSockets, so source control can be tested with `FakeSourceRemote` before the extension works (useful because the browser side lands in weeks 10–12) | 4.14, 4.16 |
| 17 | Third-party containment rule (Qt, FFmpeg, ONNX Runtime, WebSocket, JSON each allowed in one place) | Makes the licensing audit simple (where is FFmpeg used? one folder), keeps build times down, and lets a dependency be swapped without touching other libraries | 2 |
| 18 | `tests/support` becomes the `ovsr::testsupport` library with a fake for **every** interface; new fakes added together with interfaces | `ProjectUnderstanding.md` 12.1 says each workstream builds against fakes, but the old list had only five fakes (no encoder, sink, coverage, store fakes). Shared fakes mean teams do not each write slightly different ones | 2, 4.26 |
| 19 | Explicit layer diagram in section 5 | The table alone made it hard to see the shape. Layers make the "downward only" rule easy to check in reviews | 5.1 |

### 10.3 Robustness and security additions

| # | Change | Why it is an improvement | Sections |
|---|---|---|---|
| 20 | `SessionLock` in each session folder; `SessionCleaner` skips locked folders | "Delete leftover folders at start" would otherwise delete a live session if a second instance or a quick restart overlapped. Losing an unsaved video silently contradicts D19 | 4.15 |
| 21 | `SingleInstanceGuard` in the GUI app | Two instances would compete for the port and the cache. One-session-at-a-time (D12) is easier to keep with one instance | 4.4 |
| 22 | `AuthToken` (generation, storage, constant-time comparison) and `PairingDialog` | D12 requires a token, but nothing generated it or showed it to the user to paste into the extension. Constant-time comparison avoids leaking the token through timing | 4.16, 4.19 |
| 23 | `MediaTimeMapper.js` in the extension | The project depends on frames carrying **media time**, never wall-clock time. Capture APIs produce capture timestamps, so a dedicated, unit-tested mapper is needed; otherwise every seek and pause risks timeline bugs (risk 6 in `ProjectUnderstanding.md`) | 4.20 |
| 24 | Two capture strategies behind `ICaptureStrategy.js` (`ElementCapture`, `TabCapture`) | Capturing the rendered tab may give the page's display size, not the video's real resolution (verify in the spike). Capturing from the element gives native resolution and media time but has its own limits. The spike can pick one without restructuring | 4.20 |
| 25 | `SourceController.js` renamed `SourceCommandHandler.js`; C++ `SourceController` renamed `SourceDirector` | Two classes with the same name doing opposite jobs (one decides, one obeys) cause confusion in a six-person team | 4.14, 4.20 |
| 26 | `IFrameEncoder` documents forced keyframes at grid boundaries | Segments must start on a keyframe to be playable and reusable after seeks (D7). Putting it in the frozen interface avoids a late interface change | 4.13 |

### 10.4 Process and build additions

| # | Change | Why it is an improvement | Sections |
|---|---|---|---|
| 27 | `spikes/` folder | The four week 1–2 spikes need a place that does not pollute `libs/` and keeps the evidence for each ADR | 4.23 |
| 28 | `packaging/` and `OvsrInstall.cmake` | Qt and FFmpeg must be linked dynamically (LGPL), so their DLLs must ship next to the app. Without a packaging step the demo works only on developer machines | 4.2, 4.24 |
| 29 | `FindOnnxRuntime.cmake` and `OVSR_ORT_ROOT` | ONNX Runtime with GPU providers (and AMD's plugin providers) is often used as a prebuilt package; relying only on vcpkg may not give the providers you need. Verify during setup | 4.2, 6 |
| 30 | `gpu` test label, excluded in CI | CI runners have no GPU; without a label, GPU tests either fail CI or are never written | 2, 4.1, 6 |
| 31 | `CODEOWNERS` and a pull-request template | Implements the working rules in `ProjectUnderstanding.md` 12.4 (one owner per area, one reviewer, CompositionRoot single owner) with tooling instead of memory | 4.1 |
| 32 | C++23 stated as the standard | `std::expected` (used by `Result<T>`) is C++23; stating it avoids a confusing compile failure on an older compiler | 2 |
| 33 | `CliCompositionRoot` | The CLI also needs concrete wiring, without Qt or the network; a separate root keeps `main.cpp` tiny like the GUI one | 4.4 |
| 34 | New docs: `color-and-pixel-formats.md`, `packaging.md`; `source-control-and-seeking.md` renamed `session-and-source-control.md`; ADRs per decision and per spike | Each new area above gets one written home | 4.27 |

### 10.5 Kept as they were, on purpose

| Item | Reason |
|---|---|
| Static libraries in one process | Matches D11; simplest to debug for a student team |
| Interfaces in the consuming library | Still the right rule; the fixes above apply it consistently |
| Fragmented MP4, H.264 first, session cache deleted at session end, Save as the only persistence | Owner decisions D13, D14, D18 |
| `workers/` and the process backend | Kept as (later); they do not affect the core structure |
| Separate `extension/` project | It has its own toolchain; golden vectors keep the two protocol implementations in step |

### 10.6 Matching updates in `ProjectUnderstanding.md` (applied)

These have been made in `ProjectUnderstanding.md`, together with small consistency fixes there (classic upscaler instead of bilinear, the full list of frozen interfaces in 12.4, the `gpu` test label in section 11).

| Section | Update |
|---|---|
| 4.1 pipeline diagram | Show the audio encode step and the post-processing (resize + YUV) step |
| 8 protocol table | Add `SourceInfo` (extension → app) |
| 9 threads | Audio encoding runs on the encode thread; name `SessionController` as the UI's entry point |
| 12.1 workstreams | `session` belongs to workstream D (pipeline) or F (Qt app); `imaging` to B |
| 15 risks | Add "color matrix mismatch between SD input and HD output" and "capture resolution and media-time mapping" |

### 10.7 Second revision: optional spec-driven AI agent workflow

| # | Change | Why it is an improvement | Sections |
|---|---|---|---|
| 35 | `specs/` with a README, three templates and one folder per feature | Agents work best from a written, approved target; without one they guess scope and drift from the architecture. A fixed folder and templates make specs look the same whoever writes them, person or agent | 3, 4.29 |
| 36 | Five phases with a **human approval gate** after each, recorded as `status`/`approved-by` in front matter | Keeps people in control of *what* is built and *how* it fits, while agents do the drafting and typing. A gate in the file (not only in chat) is visible in review and checkable by a tool | 4.29, 4.31 |
| 37 | `specs/principles.md` (P1–P23), which agents may not edit | The rules were spread across two long documents. One short list, each line pointing to its source, is something an agent can check every design against, and a designated "do not edit" file stops an agent from relaxing a rule to make its work pass | 4.29 |
| 38 | `AGENTS.md` as the single rule file, with `CLAUDE.md` only importing it | Different agents read different file names. Writing the rules once avoids two copies drifting apart; `AGENTS.md` is the name most tools look for | 2, 4.1 |
| 39 | Skill folder `.claude/skills/spec-driven-workflow/` with one reference file per phase | The skill gives the agent the procedure (orient, check the gate, do one phase, stop). Splitting phase details into references means the agent loads only what the current phase needs, which keeps its context small and its instructions focused | 3, 4.30 |
| 40 | Requirement and task IDs, `// Verifies: REQ-…` in tests, task ID first in commits | Traceability makes "is this requirement done?" answerable by a script instead of by reading code, and shows reviewers which requirement a test exists for | 2, 4.29 |
| 41 | `tools/specs/specs.py` (`new`, `status`, `check`) and the `ci-specs.yml` job | The tool gives people and agents the same entry points; `status` tells an agent where it is; `check` catches the common failures (an approved requirement with no task, a test for a requirement that does not exist, a phase approved out of order, a finished spec with an untested requirement). It passes with no specs, so the workflow stays optional | 4.22, 4.1 |
| 42 | `.claude/settings.json` that denies reading `config/local.json` and editing the principles | The auth token and the core rules are protected by configuration, not only by an instruction the agent might not follow | 4.30 |
| 43 | Pull request template asks for the spec/task and whether an agent wrote the change | Reviewers know what to check against, and AI-written code is reviewed line by line by a person | 4.1 |
| 44 | `CODEOWNERS` requires all leads to review `AGENTS.md`, `.claude/` and the principles | These files change how every person and agent works, so one workstream should not change them alone | 4.1 |
| 45 | Placeholder recipe skills (`add-model`, `add-protocol-message`, `add-pipeline-stage`) | Section 7's recipes are already step lists; as skills, an agent can do small changes correctly without a full spec. They are written only after each recipe has been done once by hand, so the skill describes what actually works | 4.30, 8 |
| 46 | The whole workflow sits outside the build and the dependency graph | "If we ever need it": adopting it costs a few small files, and ignoring it costs nothing. Nothing in `libs/`, `ui/` or CMake reads it | 5, 8 |
