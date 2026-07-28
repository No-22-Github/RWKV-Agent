cmake_minimum_required(VERSION 3.25)
project(rwkv_agent_runtime LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if(NOT APPLE OR NOT CMAKE_SYSTEM_PROCESSOR MATCHES "arm64|aarch64")
    message(FATAL_ERROR "rwkv_agent_runtime currently requires Apple Silicon macOS")
endif()

set(RWKV_MOBILE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../third_party/rwkv-mobile")
set(RWKV_MOBILE_SRC "${RWKV_MOBILE_DIR}/src")
set(MLX_DIR "${RWKV_MOBILE_SRC}/backends/mlx")
set(RWKV_PTH_LOADER_DIR "${CMAKE_BINARY_DIR}/pth-loader")
execute_process(
    COMMAND
        "${CMAKE_CURRENT_SOURCE_DIR}/../../scripts/prepare-pth-loader.sh"
        "${RWKV_PTH_LOADER_DIR}"
    COMMAND_ERROR_IS_FATAL ANY
)
set(
    RWKV_AGENT_MLX_LIB
    "${CMAKE_CURRENT_SOURCE_DIR}/../../build/native/mlx-ffi/libMLXModelFFI.a"
    CACHE FILEPATH
    "MLXModelFFI static library")
set(MLX_LIB "${RWKV_AGENT_MLX_LIB}")

if(NOT EXISTS "${MLX_LIB}")
    message(FATAL_ERROR
        "Direct-PTH MLXModelFFI is missing: ${MLX_LIB}. "
        "Run scripts/build-mlx-ffi.sh first.")
endif()

add_library(rwkv_agent_runtime SHARED
    rwkv_agent_runtime.cpp
    rwkv_pth_model.cpp
    "../rwkv_model_schema/rwkv7_schema.cpp"
    "${RWKV_PTH_LOADER_DIR}/pth_loader.cpp"
    "${RWKV_MOBILE_SRC}/tokenizer.cpp"
    "${RWKV_MOBILE_SRC}/sampler.cpp"
)

target_include_directories(rwkv_agent_runtime PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/../rwkv_model_schema"
    "${RWKV_PTH_LOADER_DIR}"
    "${RWKV_MOBILE_SRC}"
    "${MLX_DIR}/include"
)

find_library(FOUNDATION_FRAMEWORK Foundation REQUIRED)
find_library(METAL_FRAMEWORK Metal REQUIRED)
find_library(ACCELERATE_FRAMEWORK Accelerate REQUIRED)

execute_process(
    COMMAND xcrun --find swift
    OUTPUT_VARIABLE SWIFT_PATH
    OUTPUT_STRIP_TRAILING_WHITESPACE
    COMMAND_ERROR_IS_FATAL ANY
)
get_filename_component(SWIFT_BIN_DIR "${SWIFT_PATH}" DIRECTORY)
get_filename_component(SWIFT_USR_DIR "${SWIFT_BIN_DIR}" DIRECTORY)
set(SWIFT_RUNTIME_DIR "${SWIFT_USR_DIR}/lib/swift/macosx")

target_link_directories(rwkv_agent_runtime PRIVATE "${SWIFT_RUNTIME_DIR}")
target_link_libraries(rwkv_agent_runtime PRIVATE
    "${MLX_LIB}"
    "${FOUNDATION_FRAMEWORK}"
    "${METAL_FRAMEWORK}"
    "${ACCELERATE_FRAMEWORK}"
)

foreach(compat libswiftCompatibility56.a libswiftCompatibilityConcurrency.a libswiftCompatibilityPacks.a)
    if(EXISTS "${SWIFT_RUNTIME_DIR}/${compat}")
        target_link_libraries(rwkv_agent_runtime PRIVATE "${SWIFT_RUNTIME_DIR}/${compat}")
    endif()
endforeach()

set_target_properties(rwkv_agent_runtime PROPERTIES
    OUTPUT_NAME "rwkv_agent_runtime"
    INSTALL_NAME_DIR "@rpath"
    MACOSX_RPATH ON
    CXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN YES
)

include(CTest)
if(BUILD_TESTING)
    add_executable(rwkv_agent_runtime_lifecycle_test runtime_lifecycle_test.cpp)
    target_link_libraries(rwkv_agent_runtime_lifecycle_test PRIVATE rwkv_agent_runtime)
    add_test(NAME rwkv_agent_runtime_lifecycle COMMAND rwkv_agent_runtime_lifecycle_test)

    add_executable(
        rwkv7_index_test
        "../rwkv_model_schema/rwkv7_index_test.cpp"
        "../rwkv_model_schema/rwkv7_schema.cpp"
        "${RWKV_PTH_LOADER_DIR}/pth_loader.cpp")
    target_include_directories(rwkv7_index_test PRIVATE
        "${CMAKE_CURRENT_SOURCE_DIR}/../rwkv_model_schema"
        "${RWKV_PTH_LOADER_DIR}")
    add_test(NAME rwkv7_index_round_trip COMMAND rwkv7_index_test)
endif()
