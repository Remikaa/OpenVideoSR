# OpenVideoSR — Project Understanding

This document records **how I understand the project**: its purpose, how it should behave, the decisions made so far, the model, encoding and device strategy, the assumptions I made and the questions that are still open.

The repository layout is described separately in `Structure.md`. This file contains no file-level structure.

Facts about models, codecs and hardware come from public sources found in October 2026 and from general knowledge. They change quickly and **must be verified and measured on your own machine**.

---

## 1. The project in one paragraph

OpenVideoSR lets people with slow or congested internet watch video at a low resolution (for example 360p or 720p) and see it upscaled to a sharper resolution (for example 720p, 1080p or 1440p) on their own computer. A Chrome extension captures the decoded frames and audio from the browser and sends them to a local C++ application. The application upscales the frames with a super-resolution (SR) model on the user's GPU, encodes the result into short segments with audio, and plays them in a Qt player. The video may run a few minutes behind the browser, as long as playback never stalls.

Processed video is kept in a **temporary session cache**, so going back to the beginning (or to any earlier point) is instant and never repeats the work. When the tab or the application is closed, the cache is deleted and the disk space is freed. The user keeps a video only by pressing a **Save** button.

---

## 2. Goals and non-goals

### Goals
- Smooth, uninterrupted playback (a delay of minutes is acceptable).
- Seeking back inside the session never re-upscales what was already processed.
- A **Save** button that turns the processed video into an ordinary file. Nothing is saved otherwise.
- Dynamic target resolution (360p→720p, 360p→1080p, 720p→1080p, 720p→1440p and similar).
- Several switchable models from the UI (Real-ESRGAN family, Real-ESRNet, NanoVSR and other lightweight or temporal models).
- Content profiles (anime/cartoon, live-action, screen/text) that the user picks manually.
- Windows and Linux, NVIDIA and AMD GPUs, with development and testing on a 6 GB VRAM GPU (a 3060).
- A strong software-engineering learning project: clean layering, tests, benchmarks and written decisions.

### Non-goals (for now)
- **Hardware capability probing and calibration** (benchmarking each model on the device and showing green/yellow/red feasibility). This may be implemented later if time remains after the graduation project. Until then the app shows live processing speed against source speed, and the user chooses the model and execution provider.
- Automatic content detection (the content profile is always chosen by the user).
- Keeping videos between sessions without pressing Save.
- Live, low-latency use (video calls, gaming).
- Capturing DRM-protected video: the app detects it and explains that the site cannot be captured.
- Handling ads and playlists that change the video mid-session (left for later; the user turns autoplay off).
- Training new models from scratch.

---

## 3. Decisions made so far

| ID | Decision | Reason |
|---|---|---|
| D1 | A Qt player shows the result; no browser overlay | Full control of buffering, audio and seeking |
| D2 | The goal is smooth playback, not low latency | Allows better models and avoids dropping frames |
| D3 | The browser tab is a **source**; the Qt app is the **master** | Pausing the player must not stop upscaling |
| D4 | Models are data (manifest + registry), switchable from the UI | New models need no pipeline code changes |
| D5 | ONNX is the model format; ONNX Runtime runs **in-process** by default; worker executables are an optional extra | Simplest and fastest; phones cannot spawn helper executables |
| D6 | Temporal models (several past/future frames) are supported | Better quality and less flicker |
| D7 | Output is encoded into short, keyframe-aligned segments with audio on a fixed time grid | Raw frames are far too large to buffer; the grid lets segments be reused after seeks |
| D8 | A planner turns "source size → target size" into a model run plus an exact resize | Models have fixed native scales |
| D9 | The execution provider comes from an ordered default list per platform and GPU vendor, with a user override. No automatic calibration for now | Keeps scope realistic; live fps shows whether it keeps up |
| D10 | Development and testing target a 6 GB VRAM GPU | Everything else scales from there |
| D11 | The code is split into libraries (compiled modules linked into one application, like Maven modules; not services) with one-way dependencies | Testable, enforceable architecture |
| D12 | Loopback-only server, origin check, token and size limits | A local service is still an attack surface |
| D13 | Processed segments live in a **temporary session cache** that is deleted when the session ends | The user wants disk space freed when the tab or app closes |
| D14 | Persistence happens only through an explicit **Save** button | Nothing is stored without the user asking |
| D15 | The project is licensed under **Apache License 2.0** | Decided by the project owner |
| D16 | Windows and Linux from the start; NVIDIA and AMD GPUs | Decided by the project owner |
| D17 | There is **no maximum lead** between the playhead and processing. Processing runs ahead until the video ends or the cache budget is full | Decided by the project owner |
| D18 | Segments are **fragmented MP4** and the first encoder is **H.264 hardware** (NVENC on NVIDIA, AMF on AMD) with a software H.264 fallback. HEVC and AV1 come later | Decided by the project owner. H.264 encodes on the 3060 and plays everywhere |
| D19 | When a session ends with unsaved processed video, the app asks **"Save before closing?"** | Decided by the project owner. Avoids losing a video by accident |
| D20 | The repository supports an **optional spec-driven workflow** for people and AI agents: requirements → design → tasks → implementation → verification, with a human approval after each phase | Requested by the project owner. Lets agents help with larger features without drifting from the architecture; costs nothing if unused |

---

## 4. How it works

### 4.1 The pipeline

```text
 Browser tab (muted source; the Qt app remote-controls it)
   │  source info (duration, size, fps) once, then frames + raw audio,
   │  each stamped with media time (PTS) and an epoch
   ▼
 [1 Receive] → [2 Waiting line] ─┬─ video → [3 Upscale (model, window of ±N frames)] → [4 Post-process (resize + RGB→YUV)] → [5a Encode video] ─┐
                                 └─ audio → [5b Encode audio (AAC or Opus)] ──────────────────────────────────────────────────────────────────────┤
                                                                                                                                                  ▼
                                                                             [7 Qt player] ◄── [6 Session cache] ◄── [5c Mux into grid segments]
        ▲                                                                         │
        └── Play / Pause / Seek ◄── [Source director] ◄── playhead + coverage ◄───┘
```

The data path (stages 1–5) is the **pipeline**. The decisions about what to process and when (the source director, session lifecycle, Save) are the **session** layer, which is also the only part the UI talks to (`SessionController`).

| Stage | Job | Analogy from backend engineering |
|---|---|---|
| 1 Receive | Accept messages, validate size and structure, produce typed frames and audio | API endpoint |
| 2 Waiting line | Small bounded queue; when full it pushes back on the source | Bounded work queue with backpressure |
| 3 Upscale | Run the selected model, with tiling to fit VRAM and a sliding window for temporal models. The backend does its own tensor conversion | Worker |
| 4 Post-process | Resize the model output to the exact requested size (Lanczos) and convert RGB to the encoder's YUV format with the correct color matrix | Post-processing |
| 5a Encode video | Compress frames, forcing a keyframe at every grid boundary | Serialization |
| 5b Encode audio | The browser delivers raw samples; MP4 can hold only encoded audio, so the audio is encoded (not processed by AI) | Serialization |
| 5c Mux | Combine video and audio with the same timestamps into grid-aligned segments | Packaging |
| 6 Session cache | Grid-aligned segments of about 4 s in a temporary folder, with a coverage map of what exists | Temporary object store |
| 7 Qt player | Plays segments minutes behind the source and reports its position | Consumer |

### 4.2 The player is the master

A paused browser `<video>` produces no new frames, so the browser is treated only as a feed that the Qt app controls.

| Event | Behavior |
|---|---|
| User pauses the **Qt player** | Playback stops. Processing continues (the tab keeps playing, muted) until the video ends or the cache budget is full |
| User pauses the **browser** video | The extension reports it and the app shows a prompt: *pausing for good stops upscaling because no new frames arrive; mute the tab and let the video continue so upscaling goes on.* The prompt can offer a one-click "keep playing muted" and shows manual guidance if the page blocks it. If the user chooses to pause for good, upscaling stops |
| Cache budget reached | Ingestion pauses (the tab is paused) and the UI shows "cache full". The user can raise the budget |
| User seeks inside the processed range (including back to the beginning) | Instant: play from the cache. The tab keeps working at the processing frontier, so nothing is reprocessed |
| User seeks into a gap | The app sends `Seek(t)` aligned to the segment grid; a new epoch starts; queues are flushed; the model window is reset; the new run fills the gap |
| A run reaches a segment that already exists | The controller moves the tab to the next unprocessed position (or the end) instead of reprocessing |
| Browser stalls on its own network | The Qt player keeps playing from the processed buffer |
| Tab closed, source video changes (for example autoplay), or the app closes | The session ends. If there is unsaved processed video the app asks "Save before closing?" (Save, Discard, and Cancel when the app itself is closing). After the answer the cache is deleted |
| User presses **Save** | The processed video is written to a file the user chooses (see 4.7) |

Source playback stays at 1× because the user's network is the scarce resource. Frames are stamped with the video's **media time**, never wall-clock time, so pauses and stalls do not corrupt the timeline.

### 4.3 Epochs

An epoch is a counter that increases at every seek or source change. Every frame carries its epoch, and stages drop frames from old epochs. Without it, frames sent before a seek could arrive after it and corrupt the output.

### 4.4 Throughput

Let `p` be the source frame rate and `r` the measured processing frame rate. If `r ≥ p`, the video can play with only a short start buffer. If `r < p`, playback will eventually catch up with processing and stall: a pre-buffer of about `duration × (p − r) / r` would be needed. At `p = 30`, with `r = 27`, a 10-minute clip needs about 67 s.

Without automatic calibration, the app **measures `r` while running** and shows it next to `p` in the stats panel, with a "too slow" warning when `r < p`. The user can then pick a lighter model or a lower target resolution.

The slowest link also includes the viewer's network. If the browser cannot sustain the source at 1×, ingestion is limited by the network, not by the model.

### 4.5 Sizes that drive the design

| Item | Size |
|---|---|
| Raw RGBA 1280×720 | 3,686,400 B per frame (about 110 MB/s at 30 fps) |
| Raw I420/NV12 1280×720 | 1,382,400 B per frame (about 41 MB/s at 30 fps) |
| Raw RGBA 1920×1080 | 8,294,400 B per frame (about 249 MB/s at 30 fps) |
| 1 minute of raw 1080p RGBA | about 14.9 GB (impossible to buffer) |
| 1 minute encoded at about 15 Mbps | about 112 MB |
| 1 hour encoded at about 15 Mbps | about 6.75 GB (about 3.6 GB at 8 Mbps) |

Consequences: reuse frame buffers from a pool, prefer YUV from the extension, and encode before caching. A 5 GB cache holds roughly 45 minutes at 15 Mbps or 1.5 hours at 8 Mbps, so the bitrate choice and the "cache full" behavior matter.

### 4.6 Temporal models

A temporal model needs frames `t−P … t+F` to produce frame `t`.
- Frames arrive strictly in order within an epoch.
- At the start of an epoch missing past frames are padded by repeating the first frame; at the end missing future frames are padded by repeating the last.
- Recurrent or chunk-based video models run on overlapping chunks; overlapped outputs are discarded so there are no seams.
- Five future frames add only about 0.17 s at 30 fps. The real costs are VRAM and speed.

### 4.7 The session cache and the Save button

| Concept | Meaning |
|---|---|
| Session | Starts when the extension connects and a video is chosen. Ends when the tab closes, the source video changes, or the app closes |
| Session cache | A temporary folder with the session's processed segments, deleted when the session ends |
| Segment grid | A fixed time grid (for example 4 s). Segment `k` covers `[k·4 s, (k+1)·4 s)`. Every run produces grid-aligned segments, so segments from different runs fit together |
| Coverage map | The set of time ranges whose segments exist. It answers: is time `t` ready, where is the next gap, how far does the contiguous range extend |

How it behaves:
1. **Process.** Ingest at the frontier. Only complete grid segments are committed. A half-finished segment is discarded when a run ends, which loses at most one segment length of work.
2. **Commit.** A segment is written to a temporary file, then moved into the session folder with an atomic rename. A crash never leaves a half-written segment.
3. **Seek back or replay.** If the time is covered, play straight from the cache. Nothing is reprocessed.
4. **Seek into a gap.** The tab seeks to the grid start of that segment and processing fills forward until it meets an existing segment.
5. **Lead.** Processing is not capped by a maximum lead. Only the cache budget (default assumption: 5 GB) limits how far ahead it goes.
6. **Session end.** If there is unsaved processed video, the app asks "Save before closing?". A closed tab cannot be vetoed, so the app keeps the cache and the Qt player usable until the user answers. After the answer the session folder is deleted. If the app crashed there is no prompt, and leftover folders are deleted at the next start.
7. **Save.** A button exports the processed video to an ordinary file (MP4 by default) at a location the user picks, by joining the segments without re-encoding. Saving is the only way a video survives the session.
8. **Changing model or target resolution.** The old setting's segments are discarded (they cannot be mixed with the new look, and freeing space is a goal) and processing restarts from the playhead.

| Situation | Handling |
|---|---|
| Save pressed while parts are missing | The save dialog offers to keep processing the missing parts first, or to save only what exists (open question) |
| Adaptive streaming changes the source quality mid-video | The output size stays at the target; no segment replacement is planned. Tip for users: fix the source quality in the player |
| Live streams | Only captured content is cached; there are no gaps to fill beyond the available window |
| Autoplay starts another video | The extension reports a source change and the session ends. The user is asked to turn autoplay off |
| Cache folder location | Inside the operating system's temporary location, never in the project folder |

---

## 5. Models, content profiles and resolutions

### 5.1 Models are data

Each model has a manifest entry describing its id, display name, content profiles, file, native scale, input convention, temporal window, tiling, shape policy, precision, preferred providers and license. Adding a model means exporting it to ONNX and adding an entry.

```json
{
  "id": "realesr-animevideov3",
  "displayName": "Real-ESRGAN AnimeVideo v3 (fast, anime/cartoon)",
  "profiles": ["anime"],
  "file": "realesr-animevideov3-x4.onnx",
  "format": "onnx",
  "nativeScale": 4,
  "input": { "layout": "NCHW", "channels": "RGB", "range": "0-1" },
  "temporal": { "past": 0, "future": 0 },
  "tiling": { "enabled": true, "size": 256, "overlap": 16 },
  "shapes": "dynamic",
  "precision": ["fp16", "fp32"],
  "providersPreferred": ["tensorrt", "cuda", "migraphx", "directml", "cpu"],
  "license": { "model": "see models/licenses/", "checkedOn": "" },
  "sha256": ""
}
```

### 5.2 Candidate models by content (benchmark before committing)

| Profile | First candidate | Other candidates | Notes |
|---|---|---|---|
| Anime/cartoon | realesr-animevideov3 | Real-CUGAN or waifu2x-style models | Compact network built for video. Anime weights can produce glitchy faces on real people |
| Live-action | realesr-general-x4v3 | NanoVSR (temporal, MIT, ONNX/TensorRT-friendly, 4× only), lightweight real-time image models | Mostly trained on clean camera footage; test on compressed streamed input |
| Screen/text (lectures, slides) | A high-quality scaler with sharpening as the baseline | Screen-content research models (ITSRN++, BTC, PixelSR); a fine-tuned compact model | No mature drop-in model found. GAN-style models can invent wrong letter shapes. A 360p source may not contain readable text at all |
| Heavy quality models | RealESRGAN_x4plus, RealESRNet_x4plus | — | Too slow to keep up with playback; see below. Optional, short clips only |

**What "heavy models are not practical for streaming" means.** Every model here runs on your own machine. The issue is speed. A 2026 guide reports about 1.7 fps for ×4 at 720p input on an RTX 5090, so a 3060 at 360p input would likely reach about 1 fps or less (my extrapolation). A 10-minute video at 30 fps has 18,000 frames, which would take hours. Playback cannot keep up with processing, so these models only make sense for very short clips where the user accepts a long wait.

Real-ESRGAN x4plus and RealESRNet x4plus use the same heavy architecture; they differ in training (adversarial versus pixel loss), not in speed. Per-frame models can flicker; temporal models reduce that at the cost of VRAM and speed.

**NanoVSR and live streams.** NanoVSR reports 27 fps on a Jetson Orin NX at 180×320 input. Your 360p input has four times as many pixels but a 3060 is a much stronger GPU, so its speed at 360p on the 3060 must be measured. If it reaches 30+ fps, it is a good candidate for live streams because there is no wait. For live content the model must be at least as fast as the source, because there is no buffer to hide a slow model.

### 5.3 The scale planner

Most models have one native scale (×2 or ×4). The planner runs the model at its native scale and then **downsizes** with a Lanczos filter to the exact target.

| Request | Plan |
|---|---|
| 360p → 720p | ×2 model, or ×4 then Lanczos down |
| 360p → 1080p | ×4 → 1440p, Lanczos down to 1080p |
| 720p → 1080p | ×2 → 1440p, Lanczos down to 1080p |
| 720p → 1440p | ×2 model |

**Why cost depends mostly on the input size.** A convolutional network does work for every pixel it processes. Compact networks do almost all of their layers at the *low input resolution* and only rearrange channels into a bigger image in the last step (a cheap operation). So a ×4 model costs only a little more than a ×2 model on the same input, and a 720p input costs about four times a 360p input, because it has four times the pixels (921,600 versus 230,400). Heavy RRDB-style networks add convolutions after enlarging, so their cost does grow with the scale. Keep the aspect ratio when computing the target, and use **even** output width and height, because H.264/HEVC/AV1 with 4:2:0 chroma store color at half resolution and encoders reject odd sizes.

```cpp
struct Resolution { int w, h; };

struct UpscalePlan {
    std::string  modelId;
    int          modelScale;      // native scale
    Resolution   modelOutput;     // input * modelScale
    Resolution   target;          // requested
    ResizeFilter finalResize;     // Lanczos if modelOutput > target, else None
};
```

---

## 6. Devices, execution providers and encoding

### 6.1 One model format, many backends

ONNX is the interchange format and ONNX Runtime executes it through execution providers (EPs). The app asks ONNX Runtime which providers are available, tries an ordered default list for the platform and GPU vendor, and lets the user override the choice in the settings. There is no automatic benchmarking for now.

| Platform | Provider candidates (verify; they change) |
|---|---|
| Windows + NVIDIA | TensorRT (or the TensorRT RTX provider), CUDA |
| Windows + AMD | MIGraphX (RDNA 3 or newer, via Windows ML), DirectML (labeled legacy by Microsoft) |
| Linux + NVIDIA | CUDA, TensorRT |
| Linux + AMD | MIGraphX or the generic AMDGPU provider (both on the ROCm stack); ONNX Runtime lists the older ROCm provider as deprecated |
| Any | CPU provider (always available, very slow for SR) |

Only NVIDIA can be verified on the development machine. AMD support is expected but needs testing on real AMD hardware (see the open questions).

**AMD and ONNX: does AMD need Vulkan?** No. ONNX is only the model file; what makes it fast on AMD is the execution provider. MIGraphX is AMD's graph compiler: it takes the ONNX graph and compiles it into kernels for the specific AMD GPU, the same idea as TensorRT on NVIDIA, so expect a one-time compile step per model that should be cached. DirectML is the generic Windows option for any DirectX 12 GPU. AMD also publishes plugin providers for ONNX Runtime 1.24 and newer (generic AMDGPU on ROCm, MIGraphX, DirectML). Limits: the MIGraphX route depends on ROCm, whose list of supported GPUs is narrower than "every AMD card" (check AMD's list), and the Windows ML MIGraphX path needs RDNA 3 or newer. DirectML is Windows-only, so an AMD GPU on Linux that ROCm does not support has no ONNX Runtime GPU path. Vulkan comes into play only if we add ncnn (or test ONNX Runtime's WebGPU provider) as a fallback. That is the main reason to keep ncnn as an optional fallback.

### 6.2 What to expect from different hardware (informational, not detected automatically)

| Hardware | Expectation |
|---|---|
| Desktop or laptop GPU with 6 GB+ VRAM | Compact models in real time, temporal models at 360p input |
| Integrated GPUs and laptop NPUs | Light models at low resolutions |
| Phones | Ultra-light ×2 models at best; heat and battery limit sustained use |
| CPU only | No AI; high-quality scaling plus sharpening |

### 6.3 6 GB VRAM budget

Keep the working set (model, tiles, temporal window, buffers) well below the card's total so the OS compositor, the Qt renderer and the hardware encoder still fit. Use tiling for heavy models, FP16 where tolerated, and fixed tile shapes where engines need them. Watch peak memory while testing.

### 6.4 Codecs and containers

| Codec | Hardware encoding | Strengths | Weaknesses |
|---|---|---|---|
| H.264 | Almost every GPU, including the RTX 3060 | Plays everywhere; fast | Least efficient (bigger files) |
| HEVC | Most modern GPUs | Better efficiency than H.264 | Licensing and some player limits |
| AV1 | **Only** newer GPUs: NVIDIA RTX 40 series and newer, AMD RX 7000 and newer, Intel Arc. The RTX 30 series (including the 3060) can decode AV1 but **cannot encode it** | Best compression efficiency | Software AV1 encoding needs a strong CPU and competes with the rest of the app |

**Decision:** the first release uses **H.264 hardware encoding** (NVENC on NVIDIA, AMF on AMD, with a software H.264 fallback) inside **fragmented MP4** segments. H.264 encodes on the development GPU and plays everywhere. Quality at the same bitrate is best with AV1, then HEVC, then H.264, so AV1 and HEVC can be added later as extra entries in the `EncoderSelector` list, which tries to open each encoder in order and falls back automatically. The bitrate must be high enough that the encoder does not erase the detail the model added.

**Container for segments.** Fragmented MP4 was chosen. It is also the usual container for segmented AV1 later, and saved files are MP4 too, so Save is a simple remux. MPEG-TS was considered, but AV1 in MPEG-TS follows a draft specification with incomplete tool support. The container is a configuration value, so it can change.

**Container for saved files.** A container is the file format that wraps the video and audio streams (MP4, MKV, TS). MP4 is the default for Save because it plays almost everywhere; MKV is a possible option. Joining segments into one file is a remux, not a re-encode.

### 6.5 Licensing rules for dependencies

The project is Apache 2.0. Use an LGPL build of FFmpeg without GPL-only components (such as x264 and x265), prefer hardware encoders and permissively licensed software encoders, link Qt dynamically (it is LGPL), and record every dependency and model license in `THIRD_PARTY_LICENSES.md` and `models/licenses/`. Verify each license before release.

### 6.6 What "any device" means in practice

The extension capture path exists on **desktop Chrome**. Chrome on phones does not run extensions as far as I know. A phone version needs another source, such as playing a URL or a local file inside the app. The pipeline accepts any media source, so this is a new source, not a redesign.

---

## 7. Sites, capture and protected video

The goal is to work on almost all sites with a standard video element, such as YouTube, Udemy, Coursera, Crunchyroll and anime sites. Some of these sites protect part of their content with DRM, where captured frames can come out black. The extension detects encrypted playback, the app reports that the site cannot be captured, and nothing else is attempted. Audio capture is assumed to work even when the tab is muted (stated by the project owner; verify on real sites).

---

## 8. Protocol overview

All integers are little-endian. Messages are parsed field by field with bounds checks, never by casting raw buffers.

```cpp
struct MessageHeader {
    std::uint32_t magic;        // 'OVSR'
    std::uint8_t  version;
    std::uint8_t  type;
    std::uint16_t flags;
    std::uint32_t epoch;
    std::uint32_t sequence;
    std::int64_t  ptsMicros;    // media time
    std::uint32_t payloadSize;  // checked against limits before allocating
};
```

| Direction | Messages |
|---|---|
| Extension → app | Hello (version, capabilities, token), SourceInfo (duration or live flag, native video size, frame rate, title), VideoFrame, AudioChunk, SourceState (playing, paused by page, ended, source changed, protected content), Stats, Goodbye |
| App → extension | HelloAck, Config (resolution, pixel format, fps), SourceCommand (Play, Pause, Seek aligned to the segment grid, SetRate), BufferStatus, Error |

`SourceInfo` is sent after the handshake and again when it changes. The app needs it for the coverage bar (duration), the throughput check (source fps `p` in 4.4), the scale planner (native size), live-stream handling and the default Save file name.

Frame timestamps must be the video's **media time**. Capture APIs give capture timestamps, so the extension converts them (`MediaTimeMapper`) before sending.

The C++ and JavaScript implementations share **golden test vectors** so they cannot drift apart silently.

---

## 9. Threads and data ownership

| Thread | Owns | Notes |
|---|---|---|
| Qt main (UI) | Widgets, player, view models | Never blocked by pipeline work. Calls only `SessionController`; session callbacks reach it as Qt signals |
| Network | WebSocket server and sessions | Validates, then pushes packets to the ingest queue and source events to the session |
| Inference | Model session, window, tiles, the backend's own pre-processing | One thread per model session |
| Post-process/Encode | Resizer, RGB→YUV conversion, video encoder, audio encoder, muxer | A hardware encoder shares the GPU; measure contention. Audio encoding is light and shares this thread |
| Segment I/O | Segment commits and the coverage map | Commits segments atomically and publishes them to the player |

Session decisions (source commands, ingest planning) run on the thread that delivers the event and must be quick; they never wait on pipeline work.

Frames are immutable shared objects from a pool, handed over through bounded queues. Later queues block instead of dropping frames, because dropped frames would hurt quality when delay is acceptable. Shutdown requests stop, wakes the queues, joins the threads, deletes the unsaved session cache and releases resources in reverse order.

---

## 10. Security and privacy

- Bind to `127.0.0.1` only.
- Validate the `Origin` header (the extension's id) and require a token in the handshake.
- Allow a single active session.
- Enforce maximum payload and frame dimensions before allocating.
- Never log tokens or frame content; verify model files by checksum.
- Processed video exists on disk only in the session cache (deleted at the end) or in a file the user explicitly saved.

---

## 11. Testing and quality

| Level | What | How |
|---|---|---|
| Unit | Each library | Shared fakes, one per interface (`ovsr::testsupport`) |
| Golden | Protocol | Shared byte vectors read by C++ and JavaScript tests |
| Integration | Whole pipeline, seeks, pause and backpressure, session end, save | Fake source → classic upscaler → fake or file sink, with no GPU or network |
| Model | ONNX Runtime integration | A tiny test model so no downloads are needed |
| Quality | PSNR, SSIM, LPIPS | Downscale a reference clip, upscale it, compare |
| Performance | Per-stage fps and latency | Benchmarks run by hand |

CI builds, tests and lints on Windows and Linux for every push, with sanitizers where available. Tests that need a real GPU carry the `gpu` label and are run by hand, because CI machines have no GPU.

---

## 12. Roadmap

| Phase | Build | Prove |
|---|---|---|
| 0 | Build system, CI on both OSes, foundations | A clean build with passing tests |
| 1 | Classic upscaler (bilinear/Lanczos), temporal window, tiling, pipeline, H.264 and audio encoders with fragmented-MP4 segment writer, CLI | File → file works and fps is measured |
| 2 | Model manifest, ONNX Runtime backend, provider selection, export tools | A real model runs on the 6 GB GPU |
| 3 | Scale planner | All four resolution cases |
| 4 | Session cache (coverage map, grid segments, atomic commit), Save, Qt player | Smooth playback; seeking back is instant; closing deletes the cache; Save produces a normal file |
| 5 | Protocol, WebSocket server, extension capture, source control, pause prompt | Browser → app → player; pause and seek behave |
| 6 | UI pickers, stats, settings | Everything switchable from the UI |
| 7 (if time remains) | Capability probing and calibration, feasibility display, more providers, mobile experiments | Portability claims verified on real hardware |

### 12.1 Team and workstreams (6 people)

The libraries and interfaces in `Structure.md` let six people work in parallel. Each workstream owns a few libraries and builds them against the shared fakes in `ovsr::testsupport` (one per interface) and the classic upscaler, so nobody waits for the others.

| # | Workstream | Owns | First deliverable |
|---|---|---|---|
| A | Build and core | CMake, vcpkg, CI on Windows and Linux, packaging, `base`, `media`, `infra`, `ovsr::testsupport`, later Linux and AMD checks | A green CI build and the shared frame types |
| B | Inference and models | `modelhub`, `imaging`, `inference` (ONNX Runtime backend, tiling, temporal window, engine cache), `planning`, export tools | One model running on the 3060 with measured fps and VRAM |
| C | Encoding and cache | `mediaio` (H.264 and audio encoders, fragmented-MP4 segments, muxing, Save, segment catalog), `cache` | Segments written and joined into a playable file |
| D | Pipeline and session | `pipeline` (queues, stages, epochs, runner), `session` (session manager, source director, ingest planner, `SessionController`), CLI | File → upscaled MP4 from the command line |
| E | Browser side | `extension/` (capture strategies, media-time mapping), `protocol`, `transport` | Frames and audio from a real site arriving in the app |
| F | Qt app | `ui/`, player, save, pause and pairing dialogs, `apps/openvideosr-gui` | A Qt player playing segments with seek-back |

`session` sits with D because it drives the pipeline runner directly. If D is overloaded after M1, `session` can move to F, which is its main user.

### 12.2 Scope priorities

Rough effort for Must and Should is 30–40 person-weeks of full-time work. Six students at about 12–15 hours a week provide about 32 full-time-equivalent weeks over 16 weeks, so plan for Must and Should and treat Could as a bonus.

| Priority | Include |
|---|---|
| Must | One model, H.264 fragmented-MP4 segments, session cache with seek-back, Qt player, browser capture, pause prompt, Save, Save before closing |
| Should | Resolution planner, a second model (Real-ESRGAN family), content profile picker, stats panel |
| Could | Temporal models (NanoVSR), gap filling beyond "restart at the seek point", Linux testing beyond CI builds |
| Later | AMD verification, ncnn, workers, mobile, AV1, calibration |

### 12.3 Sample 16-week schedule (adjust to the real deadline)

| Weeks | Goal | Milestone |
|---|---|---|
| 1–2 | Four spikes: model speed on the 3060 (B), browser capture with a muted background tab (E), playing growing fragmented-MP4 segments in Qt (F), writing segments with FFmpeg (C). Build skeleton and CI (A). Freeze the interfaces and the protocol document (all) | Spike results; interfaces frozen |
| 3–6 | Each workstream builds its libraries against fakes. In week 3 a thin **walking skeleton** connects every piece with fakes, end to end | **M1**: command line file → upscaled MP4 |
| 7–9 | Integration: the Qt player with seek-back, the extension sending to the server | **M2**: Qt player plays the segments |
| 10–12 | End to end from the browser: pause prompt, Save, Save before closing | **M3**: browser → upscale → player → Save |
| 13–14 | Second model, planner and resolutions, profiles; temporal model if on track; Linux testing | **M4**: feature complete |
| 15–16 | Hardening, tests, documentation, demo | Final demo |

### 12.4 Rules for working in parallel

1. Freeze interfaces early (`IUpscaler`, `IMediaSource`, `IFrameEncoder`, `IAudioEncoder`, `ISegmentSink`, `ICoverageProvider`, `ISessionStore`, `ISessionExporter`, `ISegmentCatalog`, `ISourceRemote`, `ISourceEvents`) and the protocol document. Each interface gets its fake in the same pull request. Changes need a short team discussion.
2. One owner for `CompositionRoot`, to avoid constant merge conflicts.
3. Integrate weekly. Every pull request passes CI and has one reviewer.
4. If a spike fails, change the plan immediately, not later.
5. Add folders when their phase starts, not before.
6. If the team uses specs (D20), a feature that touches several libraries starts with an approved spec in `specs/`. AI agents follow `AGENTS.md` and the spec-driven-workflow skill, never approve their own work, and every line they write is reviewed by a person.

---

## 13. Assumptions and your answers

| # | Assumption or answer | Status |
|---|---|---|
| 1 | One source tab is active at a time | Confirmed |
| 2 | Windows and Linux are both targeted from the start (the build tools are cross-platform); Windows is the main development machine | Updated by you |
| 3 | The user controls playback in the Qt player; the source tab is muted. If the browser video is paused, the app asks; pausing for good stops upscaling; the app guides the user to mute and let the video continue | Confirmed, with the prompt details |
| 4 | Audio is captured by the extension and muxed into the output, not processed by AI | Confirmed |
| 5 | Target resolution and content profile are chosen by the user; no automatic content detection | Confirmed |
| 6 | Processed segments are kept only in a temporary session cache; they are deleted when the tab or app closes unless the user pressed Save. The app asks "Save before closing?" when unsaved processed video exists | Changed by you |
| 7 | On-demand video is the priority. Live streams may work with fast models such as NanoVSR so there is no wait (to be measured) | Updated by you |
| 8 | License: Apache 2.0 | Confirmed |
| 9 | NVIDIA and AMD GPUs on Windows and Linux at first release | Confirmed |
| 10 | The user turns autoplay off, so the source video does not change mid-session | Confirmed |
| 11 | No maximum lead | Confirmed |
| 12 | The default cache budget is 5 GB | My assumption (you said "maybe 5 GB") |
| 13 | One processed version per session: changing the model or target discards the old segments and restarts from the playhead | My assumption |
| 14 | Muting the tab does not silence the captured audio | Stated by you; verify |
| 15 | If a site cannot be captured (DRM), the app detects it and explains | Confirmed |
| 16 | Segments are fragmented MP4; the first encoder is H.264 hardware; AV1 and HEVC come later | Confirmed by you |
| 17 | The app asks "Save before closing?" when a session ends with unsaved processed video | Confirmed by you |

---

## 14. Open questions

1. **How the Qt player consumes segments.** Options: `QMediaPlayer` with a local playlist, or a small custom player that decodes segments with FFmpeg and feeds Qt's video and audio sinks. Recommendation: spend a short spike in phase 4 trying `QMediaPlayer` first; if seeking across gaps or a growing playlist is unreliable, write the custom player.
2. **Which models ship in the first release**, and what are the licenses of their weights and exported files?
3. **Save with gaps.** Should Save wait until the whole video is processed, offer to continue processing the rest, or allow saving only what exists?
4. **When the cache budget is reached.** Pause ingestion and show "cache full" (current plan), or trim the oldest watched segments (which would break going back to the start)?
5. **AMD support.** MIGraphX and DirectML cover recent AMD GPUs, but an AMD GPU on Linux that ROCm does not support has no ONNX Runtime GPU path. Do we add ncnn (Vulkan) as an optional fallback, and who tests on AMD hardware?
6. **Ads and playlists** that change the video mid-session are postponed; the user turns off autoplay.
7. **Live streams.** Require a model at least as fast as the source and show a warning when it is not.

---

## 15. Risks to test early

1. **Muted source tab:** frame delivery in a background tab may be throttled; verify that audio capture works with the tab muted.
2. **Qt playing a growing set of segments** with gaps; decide between `QMediaPlayer` and a custom player early.
3. **Model robustness on compressed streamed input:** many SR models are trained on clean downscaled images, while streams carry codec damage.
4. **Flicker and temporal consistency** for single-frame models.
5. **VRAM headroom on 6 GB** with the encoder and the Qt renderer running at the same time.
6. **Seek and epoch correctness**, the most bug-prone area; it needs dedicated integration tests.
7. **Licenses** for model weights, FFmpeg and encoders (Apache 2.0 project).
8. **DRM:** some sites listed (for example streaming and course sites) may protect content, so capture will not work everywhere.
9. **AMD and Linux paths** are unverified until tested on real hardware.
10. **Cache growth:** about 3.6 to 6.75 GB per hour of output; the budget and the "cache full" behavior must be clear to the user.
11. **Seams between separately processed runs** (different epochs).
12. **Hardware encoder and the upscaler sharing one GPU.**
13. **Color matrix mismatch:** low-resolution sources usually use the BT.601 color matrix and HD outputs BT.709. If the conversion or the encoder tags ignore this, colors shift visibly after 360p → 1080p. Carry the color space with every frame and check it in tests.
14. **Capture resolution and media time:** capturing the rendered tab may give the page's display size instead of the video's own resolution, and capture timestamps are not media time. The week 1–2 capture spike must compare element capture with tab capture and verify the media-time mapping across pause and seek.

---

## 16. Glossary

| Term | Meaning |
|---|---|
| SR | Super-resolution: enlarging an image or video while reconstructing detail |
| Library (in this project) | A compiled code module linked into the one application, like a Maven module; not a running service |
| Native scale | The scale factor a model is trained for (×2, ×4) |
| Temporal model | A model that uses neighboring frames to produce each output frame |
| Tiling | Processing an image in overlapping pieces to fit in VRAM |
| Epoch | A counter that increases at every seek; used to discard stale frames |
| PTS | Presentation timestamp: the video's own media time for a frame |
| Segment | A short, independently playable piece of encoded output (about 4 s) |
| Segment grid | The fixed time grid on which segments are cut |
| Coverage map | The set of time ranges already processed in the session |
| Session cache | The temporary folder holding the session's processed segments |
| Save | The explicit action that exports the processed video to a normal file |
| Execution provider (EP) | An ONNX Runtime backend for a specific hardware or library |
| Container | The file format that wraps video and audio (MP4, MKV, TS) |
| Backpressure | Slowing down a producer when a consumer's queue is full |
| Spec | A short written agreement about one feature (requirements, design, tasks) that is approved before it is built |
| Requirement ID | `REQ-<spec>-<nn>`; tests that prove it are marked `// Verifies: REQ-<spec>-<nn>` |
| Agent skill | A folder with a `SKILL.md` file that tells an AI agent how to do one kind of task in this repository |
