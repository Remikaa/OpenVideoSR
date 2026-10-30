# ovsr::imaging — CPU image processing (Structure.md §4.7)
# NOT wired yet — un-comment in libs/CMakeLists.txt when phase 1 starts (Structure.md §8).
# TODO(workstream B): implement the library contract.

ovsr_add_library(imaging
    SOURCES
        src/PixelConverter.cpp
        src/ColorConverter.cpp
        src/Resizer.cpp
        src/Sharpener.cpp
    PUBLIC_DEPS ovsr::base ovsr::media
)
