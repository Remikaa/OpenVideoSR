# ovsr::modelhub — models as data (Structure.md §4.10)
# NOT wired yet — un-comment in libs/CMakeLists.txt when phase 1 starts (Structure.md §8).
# TODO(workstream B): implement the library contract.

ovsr_add_library(modelhub
    SOURCES
        src/ModelManifest.cpp
        src/ModelRegistry.cpp
        src/ProfileDefaults.cpp
        src/ModelVerifier.cpp
    PUBLIC_DEPS ovsr::base ovsr::infra
)
