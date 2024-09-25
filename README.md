# How to build
1. make sure you have onnxruntime package and configure cmake accordingly. 
    - if you manually download the package.... Set the path to the ONNX Runtime directory on CMakeLists.txt
2. run convert_to_onnx_random_forest_IRV9.py and get the .onnx file
3. Update the model path in load_ONNX_model.cpp approx Line 13.
3. build CMake

# To manually manually download the package
#wget https://github.com/microsoft/onnxruntime/releases/download/v1.15.1/onnxruntime-linux-x64-1.15.1.tgz
#tar -xvzf onnxruntime-linux-x64-1.15.1.tgz

# cmake command
```bash
rm -rf build
mkdir build
cd build
cmake ..
cmake --build .
```
