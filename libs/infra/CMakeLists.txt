# ovsr::infra — technical utilities (Structure.md §4.9)
# Wired in phase 0 (Structure.md §8).

ovsr_add_library(infra
    SOURCES
        src/logging/Logger.cpp
        src/configuration/ConfigLoader.cpp
        src/configuration/ConfigValidator.cpp
        src/metrics/MetricsRegistry.cpp
        src/paths/AppPaths.cpp
        src/platform/Win32GpuInfo.cpp
        src/platform/LinuxGpuInfo.cpp
    PUBLIC_DEPS ovsr::base
)
