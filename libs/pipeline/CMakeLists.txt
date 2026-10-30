# ovsr::pipeline — data plane (frames in, segments out) (Structure.md §4.13)
# NOT wired yet — un-comment in libs/CMakeLists.txt when phase 1 starts (Structure.md §8).
# TODO(workstream D): implement the library contract.

ovsr_add_library(pipeline
    SOURCES
        src/EpochTracker.cpp
        src/PipelineRunner.cpp
        src/stages/IngestStage.cpp
        src/stages/InferenceStage.cpp
        src/stages/PostprocessStage.cpp
        src/stages/VideoEncodeStage.cpp
        src/stages/AudioEncodeStage.cpp
        src/stages/SegmentAssemblerStage.cpp
    PUBLIC_DEPS ovsr::base ovsr::media ovsr::imaging ovsr::infra ovsr::inference ovsr::planning
)
