# ovsr::cache — temporary session cache (Structure.md §4.15)
# NOT wired yet — un-comment in libs/CMakeLists.txt when phase 1 starts (Structure.md §8).
# TODO(workstream C): implement the library contract.

ovsr_add_library(cache
    SOURCES
        src/CachePaths.cpp
        src/CoverageMap.cpp
        src/DiskBudget.cpp
        src/SessionLock.cpp
        src/SessionCache.cpp
        src/SessionCleaner.cpp
    PUBLIC_DEPS ovsr::base ovsr::media ovsr::infra
)
