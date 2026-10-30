# ovsr::transport — network side (Structure.md §4.16)
# NOT wired yet — un-comment in libs/CMakeLists.txt when phase 3 starts (Structure.md §8).
# TODO(workstream E): implement the library contract.

ovsr_add_library(transport
    SOURCES
        src/WebSocketConnection.cpp
        src/AuthToken.cpp
        src/HandshakeValidator.cpp
        src/ClientSession.cpp
        src/WebSocketServer.cpp
        src/NetworkMediaSource.cpp
        src/NetworkSourceRemote.cpp
    PUBLIC_DEPS ovsr::base ovsr::media ovsr::protocol ovsr::infra ovsr::pipeline ovsr::session
)
