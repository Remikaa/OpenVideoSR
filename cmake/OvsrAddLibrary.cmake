# OpenVideoSR — ovsr_add_library (Structure.md §2, §4.2)
# Creates the static target <name> and its ovsr::<name> alias, with public
# include/ and private src/ include paths. One library, one responsibility.
function(ovsr_add_library name)
    cmake_parse_arguments(LIB "" "" "SOURCES;PUBLIC_DEPS;PRIVATE_DEPS" ${ARGN})
    add_library(${name} STATIC)
    add_library(ovsr::${name} ALIAS ${name})
    if(LIB_SOURCES)
        target_sources(${name} PRIVATE ${LIB_SOURCES})
    endif()
    target_include_directories(${name}
        PUBLIC  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)
    target_compile_features(${name} PUBLIC cxx_std_23)
    if(LIB_PUBLIC_DEPS)
        target_link_libraries(${name} PUBLIC ${LIB_PUBLIC_DEPS})
    endif()
    if(LIB_PRIVATE_DEPS)
        target_link_libraries(${name} PRIVATE ${LIB_PRIVATE_DEPS})
    endif()
    ovsr_set_warnings(${name})
endfunction()
