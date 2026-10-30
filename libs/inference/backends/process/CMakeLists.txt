# ovsr::inference_process - worker-process backend (LATER, Structure.md 4.11/8)
# Placeholder per owner decision; wired behind option OVSR_ENABLE_WORKERS when
# its phase starts. TODO(workstream B): implement.

if(NOT OVSR_ENABLE_WORKERS)
    return()
endif()

ovsr_add_library(inference_process
    SOURCES
        WorkerSupervisor.cpp
        ProcessUpscaler.cpp
        FolderBatchUpscaler.cpp
        platform/Win32WorkerProcess.cpp
        platform/PosixWorkerProcess.cpp
    PUBLIC_DEPS ovsr::inference
)
