# ovsr::inference — upscaling (Structure.md §4.11)
# NOT wired yet — un-comment in libs/CMakeLists.txt when phase 1 starts (Structure.md §8).
# TODO(workstream B): implement the library contract.

ovsr_add_library(inference
    SOURCES
        src/TemporalWindow.cpp
        src/TileRunner.cpp
        src/ExecutionProviderSelector.cpp
        src/UpscalerFactory.cpp
        src/backends/classic/ClassicUpscaler.cpp
    PUBLIC_DEPS ovsr::base ovsr::media ovsr::imaging ovsr::infra ovsr::modelhub
)
