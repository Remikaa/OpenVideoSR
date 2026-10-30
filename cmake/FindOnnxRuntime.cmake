# OpenVideoSR — locate ONNX Runtime (Structure.md §4.2, §6)
# From vcpkg OR from a prebuilt package pointed to by OVSR_ORT_ROOT, because the
# GPU and AMD plugin providers are often distributed as separate prebuilt packages.
# TODO(workstream A/B): implement in phase 2; verified on the 3060 machine.
function(ovsr_find_onnx_runtime)
    # TODO: if(OVSR_ORT_ROOT) find include/lib dirs and define an imported target
    #       else use the vcpkg port via find_package(onnxruntime CONFIG)
endfunction()
