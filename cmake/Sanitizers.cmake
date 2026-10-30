# OpenVideoSR — optional sanitizers for test builds (Structure.md §4.2)
# TODO(workstream A): enable in the CI matrix on Linux; hooks stay unused until then.
option(OVSR_ENABLE_SANITIZERS "Enable address/undefined sanitizers for targets" OFF)
function(ovsr_set_sanitizers target)
    # TODO(workstream A): apply -fsanitize flags when the option is set.
endfunction()
