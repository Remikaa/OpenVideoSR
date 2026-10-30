# ovsr::mediaio — encoding, files and saving (Structure.md §4.17)
# NOT wired yet — un-comment in libs/CMakeLists.txt when phase 1 starts (Structure.md §8).
# TODO(workstream C): implement the library contract.

ovsr_add_library(mediaio
    SOURCES
        src/VideoEncoder.cpp
        src/AudioEncoder.cpp
        src/EncoderSelector.cpp
        src/Muxer.cpp
        src/SegmentWriter.cpp
        src/CacheSegmentSink.cpp
        src/CacheCoverageAdapter.cpp
        src/CacheSessionAdapter.cpp
        src/CacheSegmentCatalog.cpp
        src/PlaylistBuilder.cpp
        src/SegmentConcatenator.cpp
        src/SessionExporter.cpp
        src/FileMediaSource.cpp
        src/FileMediaSink.cpp
    PUBLIC_DEPS ovsr::base ovsr::media ovsr::infra ovsr::pipeline ovsr::session ovsr::cache
)
