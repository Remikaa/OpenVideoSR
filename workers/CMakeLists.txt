# OpenVideoSR - optional model-runner executables (LATER, Structure.md 4.18/8).
# Placeholder per owner decision; wired behind option OVSR_ENABLE_WORKERS when
# its phase starts.

if(NOT OVSR_ENABLE_WORKERS)
    return()
endif()

add_subdirectory(common)      # ovsr::workerproto
add_subdirectory(ort-worker)  # target ovsr_ort_worker
