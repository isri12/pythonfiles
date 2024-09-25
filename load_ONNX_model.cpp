/*
    C++ program to load this model and use it for predictions

- loads the model from a file.
- prepares some input data for the model.
- Inference prediction based on this input.
- prints Model prediction.

*/

#include <onnxruntime_cxx_api.h>
#include <vector>
#include <iostream>

int main() {
    try {
        // Initialize environment
        Ort::Env env(ORT_LOGGING_LEVEL_WARNING, "test");

        // Initialize session options
        Ort::SessionOptions session_options;
        session_options.SetIntraOpNumThreads(1);  

        // Create session
        const char* model_path = "../random_forest_model_v9.onnx";
        Ort::Session session(env, model_path, session_options);
        
        // Print model input layer (node names, types, shape etc.)
        Ort::AllocatorWithDefaultOptions allocator;

        // Print number of model input nodes
        size_t num_input_nodes = session.GetInputCount();
        std::vector<const char*> input_node_names(num_input_nodes);
        std::cout << "Number of inputs = " << num_input_nodes << std::endl;

        // Print input node names
        for (size_t i = 0; i < num_input_nodes; i++) {
            Ort::AllocatedStringPtr input_name = session.GetInputNameAllocated(i, allocator);
            std::cout << "Input " << i << " : name=" << input_name.get() << std::endl;
            input_node_names[i] = input_name.release();
        }

        // Print number of output nodes
        size_t num_output_nodes = session.GetOutputCount();
        std::vector<const char*> output_node_names(num_output_nodes);
        std::cout << "Number of outputs = " << num_output_nodes << std::endl;

        // Print output node names
        for (size_t i = 0; i < num_output_nodes; i++) {
            Ort::AllocatedStringPtr output_name = session.GetOutputNameAllocated(i, allocator);
            std::cout << "Output " << i << " : name=" << output_name.get() << std::endl;
            output_node_names[i] = output_name.release();
        }

        // Example: Create input tensor (adjust according to your model's input shape)
        std::vector<float> input_tensor_values{1.0f, 2.0f, 3.0f, 4.0f};
        std::vector<int64_t> input_tensor_shape{1, 4};
        Ort::MemoryInfo memory_info = Ort::MemoryInfo::CreateCpu(OrtArenaAllocator, OrtMemTypeDefault);
        Ort::Value input_tensor = Ort::Value::CreateTensor<float>(
            memory_info, input_tensor_values.data(), input_tensor_values.size(),
            input_tensor_shape.data(), input_tensor_shape.size());

        // Run inference
        auto output_tensors = session.Run(
            Ort::RunOptions{nullptr}, input_node_names.data(), &input_tensor, 1, output_node_names.data(), output_node_names.size());

        // Get pointer to output tensor float values
        float* floatarr = output_tensors[0].GetTensorMutableData<float>();

        // Print predictions
        std::cout << "Prediction: " << floatarr[0] << std::endl;

        // Clean up allocated memory
        for (const char* name : input_node_names) {
            allocator.Free(const_cast<void*>(reinterpret_cast<const void*>(name)));
        }
        for (const char* name : output_node_names) {
            allocator.Free(const_cast<void*>(reinterpret_cast<const void*>(name)));
        }
    }
    catch (const Ort::Exception& exception) {
        std::cout << "Error running model inference: " << exception.what() << std::endl;
        return -1;
    }
    return 0;
}

