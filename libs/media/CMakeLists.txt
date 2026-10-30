# ovsr::media — domain types (Structure.md §4.6)
# Wired in phase 0 (Structure.md §8).

ovsr_add_library(media
    SOURCES
        src/VideoFrame.cpp
        src/FramePool.cpp
    PUBLIC_DEPS ovsr::base
)
