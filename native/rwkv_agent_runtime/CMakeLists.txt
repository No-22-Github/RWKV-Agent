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
set(MLX_LIB "${MLX_DIR}/prebuilt/macos-arm64/libMLXModelFFI.a")

if(NOT EXISTS "${MLX_LIB}")
    message(FATAL_ERROR "Pinned MLXModelFFI library is missing: ${MLX_LIB}")
endif()

add_library(rwkv_agent_runtime SHARED
    rwkv_agent_runtime.cpp
    "${RWKV_MOBILE_SRC}/tokenizer.cpp"
    "${RWKV_MOBILE_SRC}/sampler.cpp"
)

target_include_directories(rwkv_agent_runtime PRIVATE
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
endif()
