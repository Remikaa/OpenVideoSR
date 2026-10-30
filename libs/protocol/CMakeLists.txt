# ovsr::protocol — wire format (Structure.md §4.8)
# NOT wired yet — un-comment in libs/CMakeLists.txt when phase 1 starts (Structure.md §8).
# TODO(workstream E): implement the library contract.

ovsr_add_library(protocol
    SOURCES
        src/ControlMessages.cpp
        src/MessageParser.cpp
        src/MessageSerializer.cpp
    PUBLIC_DEPS ovsr::base ovsr::media
)
