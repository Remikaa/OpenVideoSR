# ovsr::session — control plane (session, source, save) (Structure.md §4.14)
# NOT wired yet — un-comment in libs/CMakeLists.txt when phase 3 starts (Structure.md §8).
# TODO(workstream D): implement the library contract.

ovsr_add_library(session
    SOURCES
        src/SessionController.cpp
        src/SessionManager.cpp
        src/SourceDirector.cpp
        src/IngestPlanner.cpp
        src/PrebufferGate.cpp
        src/ThroughputMonitor.cpp
    PUBLIC_DEPS ovsr::base ovsr::media ovsr::infra ovsr::planning ovsr::pipeline
)
