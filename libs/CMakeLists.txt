# OpenVideoSR — libraries (Structure.md §3, §5, §8)
# Wiring follows §8: a library is created no earlier than the libraries it
# depends on. Un-comment a line when its phase starts.

# Phase 0 — foundations:
add_subdirectory(base)
add_subdirectory(media)
add_subdirectory(infra)

# Phase 1 (M1 — walking skeleton):
# add_subdirectory(imaging)
# add_subdirectory(modelhub)
# add_subdirectory(inference)          # includes backends/classic
# add_subdirectory(inference/backends/ort)  # phase 2 (M2); option OVSR_ENABLE_ORT
# add_subdirectory(protocol)
# add_subdirectory(planning)
# add_subdirectory(pipeline)
# add_subdirectory(cache)
# add_subdirectory(mediaio)
# NOTE: inference/backends/process is (later); option OVSR_ENABLE_WORKERS.

# Phase 3 (M2 — session and player):
# add_subdirectory(session)
# add_subdirectory(transport)
