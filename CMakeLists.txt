cmake_minimum_required(VERSION 3.25)

project(OpenVideoSR VERSION 0.1.0 LANGUAGES C CXX)

# C++23: Result<T> uses std::expected (Structure.md §2).
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
include(OvsrOptions)
include(CompilerWarnings)
include(Sanitizers)
include(Testing)
include(OvsrAddLibrary)
include(FindOnnxRuntime)
include(OvsrInstall)

enable_testing()

# ------------------------------------------------------------------
# Phase 0 — foundations (Structure.md §8): these are wired now.
# ------------------------------------------------------------------
add_subdirectory(libs)
if(OVSR_BUILD_TESTS)
    add_subdirectory(tests)
endif()

# ------------------------------------------------------------------
# Phase-gated — wired when the phase starts (Structure.md §8).
# The folder and CMakeLists skeletons exist already; do not wire early.
# ------------------------------------------------------------------
# Phase 1 (M1):  add_subdirectory(apps)              # openvideosr-cli
# Phase 1:       add_subdirectory(benchmarks)        # option OVSR_BUILD_BENCHMARKS
# Phase 2 (M2):  libs/inference/backends/ort         # option OVSR_ENABLE_ORT; see libs/CMakeLists.txt
# Phase 3 (M2):  add_subdirectory(ui)                # option OVSR_BUILD_UI; needs the Qt SDK
# Phase 3 (M2):  add_subdirectory(apps)              # openvideosr-gui
# Later:         add_subdirectory(workers)           # option OVSR_ENABLE_WORKERS
