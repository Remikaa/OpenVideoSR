# OpenVideoSR — shared warning flags for MSVC, Clang and GCC (Structure.md §4.2)
# TODO(workstream A): agree the final warning set with the team in phase 0.
function(ovsr_set_warnings target)
    if(MSVC)
        target_compile_options(${target} PRIVATE /W4 /permissive- /w14242 /w14254 /w14640 /w14826)
    else()
        target_compile_options(${target} PRIVATE -Wall -Wextra -Wpedantic -Wshadow
            -Wnon-virtual-dtor -Wold-style-cast -Wcast-align -Wunused
            -Woverloaded-virtual -Wconversion -Wsign-conversion -Wformat=2)
    endif()
endfunction()
