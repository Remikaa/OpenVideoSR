# openvideosr-gui (Structure.md 4.4). Wired in phase 3 (Structure.md 8).
# TODO(workstream F): find_package(Qt6 ...) - components decided with the
# player spike (QMediaPlayer vs custom player, open question 1).
set(OVSR_GUI_SOURCES
    main.cpp
    Application.cpp
    SingleInstanceGuard.cpp
    CompositionRoot.cpp
)
add_executable(openvideosr-gui ${OVSR_GUI_SOURCES})
# TODO: target_link_libraries(openvideosr-gui PRIVATE ovsr::ui ovsr::session ...)
