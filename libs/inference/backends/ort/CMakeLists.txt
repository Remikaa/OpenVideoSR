# ovsr::inference_ort - in-process ONNX Runtime backend (Structure.md 4.2/4.11/6)
# Wired from root/libs at phase 2 (Structure.md 8) behind option OVSR_ENABLE_ORT;
# the SDK comes from vcpkg or OVSR_ORT_ROOT (see FindOnnxRuntime.cmake).
# TODO(workstream B): implement.

if(NOT OVSR_ENABLE_ORT)
    return()
endif()

ovsr_find_onnx_runtime()
ovsr_add_library(inference_ort
    SOURCES
        OrtSessionFactory.cpp
        OrtProviderConfig.cpp
        OrtEngineCache.cpp
        OrtTensorBinding.cpp
        OrtPreprocess.cpp
        OrtUpscaler.cpp
    PUBLIC_DEPS ovsr::inference
)
