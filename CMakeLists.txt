cmake_minimum_required(VERSION 3.14)
project(ONNXRuntimeExample)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

#include(FetchContent)

# # Fetch ONNX Runtime
# FetchContent_Declare(
#   onnxruntime
#   URL https://github.com/microsoft/onnxruntime/releases/download/v1.15.1/onnxruntime-linux-x64-1.15.1.tgz
#   URL_HASH SHA256=62ac371a6ba8df4f934c7cfa2b0ed38f89dea538f774b9078c1e9e8b5afdbcf3
# )
# FetchContent_MakeAvailable(onnxruntime)

# # Find ONNX Runtime package
# find_package(ONNX REQUIRED PATHS ${onnxruntime_SOURCE_DIR})

# if you manually download the package.... Set the path to the ONNX Runtime directory
set(ONNXRUNTIME_ROOT_PATH "${CMAKE_CURRENT_SOURCE_DIR}/onnxruntime-linux-x64-1.15.1" CACHE PATH "Path to ONNX Runtime directory")

# Find ONNX Runtime package
find_library(ONNXRUNTIME_LIBRARY onnxruntime PATHS "${ONNXRUNTIME_ROOT_PATH}/lib" NO_DEFAULT_PATH REQUIRED)
find_path(ONNXRUNTIME_INCLUDE_DIR onnxruntime_cxx_api.h PATHS "${ONNXRUNTIME_ROOT_PATH}/include" NO_DEFAULT_PATH REQUIRED)

# Add your executable
add_executable(load_ONNX_model load_ONNX_model.cpp)

# Link against ONNX Runtime
target_link_libraries(load_ONNX_model PRIVATE ${ONNXRUNTIME_LIBRARY})

# Include ONNX Runtime headers
target_include_directories(load_ONNX_model PRIVATE ${ONNXRUNTIME_INCLUDE_DIR})


# # Link against ONNX Runtime
# target_link_libraries(load_ONNX_model PRIVATE onnxruntime)

# # Include ONNX Runtime headers
# target_include_directories(load_ONNX_model PRIVATE ${ONNX_INCLUDE_DIRS})



