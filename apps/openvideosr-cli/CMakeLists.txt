# openvideosr-cli (Structure.md 4.4). Wired in phase 1 (Structure.md 8).
# TODO(workstream D): implement; links the pipeline data plane only.
set(OVSR_CLI_SOURCES
    main.cpp
    CliOptions.cpp
    CliCompositionRoot.cpp
)
add_executable(openvideosr-cli ${OVSR_CLI_SOURCES})
# TODO: target_link_libraries(openvideosr-cli PRIVATE ovsr::pipeline ovsr::mediaio ...)
