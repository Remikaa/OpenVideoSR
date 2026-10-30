# ovsr::planning — resolution plans (Structure.md §4.12)
# NOT wired yet — un-comment in libs/CMakeLists.txt when phase 1 starts (Structure.md §8).
# TODO(workstream B): implement the library contract.

ovsr_add_library(planning
    SOURCES
        src/ScalePlanner.cpp
    PUBLIC_DEPS ovsr::base ovsr::media ovsr::modelhub
)
