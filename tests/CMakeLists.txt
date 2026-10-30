# OpenVideoSR - tests (Structure.md 4.26). Wired in phase 0: ovsr::testsupport.
add_library(ovsr_testsupport STATIC
    support/FakeTimeSource.cpp
    support/FakeUpscaler.cpp
    support/FakeMediaSource.cpp
    support/FakeFrameEncoder.cpp
    support/FakeAudioEncoder.cpp
    support/FakeSegmentSink.cpp
    support/FakeCoverageProvider.cpp
    support/FakeSessionStore.cpp
    support/FakeSessionExporter.cpp
    support/FakeSegmentCatalog.cpp
    support/FakeSourceRemote.cpp
    support/FakeWorkerProcess.cpp
    support/InMemoryConnection.cpp
    support/TestFrames.cpp
)
add_library(ovsr::testsupport ALIAS ovsr_testsupport)
target_include_directories(ovsr_testsupport PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/support)
target_link_libraries(ovsr_testsupport PUBLIC ovsr::base ovsr::media ovsr::infra)
target_compile_features(ovsr_testsupport PUBLIC cxx_std_23)
ovsr_set_warnings(ovsr_testsupport)

# unit/ and integration/ suites are wired when their libraries are (phase 1+;
# see Structure.md 8). One fake per interface, in the change that adds it.
