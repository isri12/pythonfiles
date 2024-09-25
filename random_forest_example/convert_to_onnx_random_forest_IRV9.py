#Create and train a Random Forest model.
#Convert it to ONNX format.


import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import onnx
import onnxruntime as rt

# Read the data from the CSV file
df = pd.read_csv('sample_data.csv')
X = df.drop('target', axis=1).values
y = df['target'].values

# Create and train a Random Forest classifier
rf_classifier = RandomForestClassifier(n_estimators=10, max_depth=5, random_state=42)
rf_classifier.fit(X, y)

# Specify the input feature shape
initial_type = [('float_input', FloatTensorType([None, 4]))]

# Convert the model to ONNX
onnx_model = convert_sklearn(rf_classifier, initial_types=initial_type)

# Manually set the IR version to 9
onnx_model.ir_version = 9

# Update the opset import to version 9
for opset in onnx_model.opset_import:
    if opset.domain == '' or opset.domain == 'ai.onnx':
        opset.version = 9

# Save the ONNX model
onnx.save(onnx_model, "random_forest_model_v9.onnx")

print("Random Forest model has been converted to ONNX format (IR version 9) and saved as 'random_forest_model_v9.onnx'")

# Verify the model
sess = rt.InferenceSession("random_forest_model_v9.onnx")
input_name = sess.get_inputs()[0].name
label_name = sess.get_outputs()[0].name

# Test prediction
test_input = X[:1].astype(np.float32)
pred_onnx = sess.run([label_name], {input_name: test_input})[0]
print(f"ONNX model prediction: {pred_onnx}")

# Compare with original sklearn model
pred_sklearn = rf_classifier.predict(test_input)
print(f"sklearn model prediction: {pred_sklearn}")

assert np.array_equal(pred_onnx, pred_sklearn), "Predictions don't match!"
print("Conversion successful: ONNX and sklearn predictions match.")

# Verify the IR version
loaded_model = onnx.load("random_forest_model_v9.onnx")
print(f"ONNX model IR version: {loaded_model.ir_version}")

# import numpy as np
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.datasets import make_classification
# from skl2onnx import convert_sklearn
# from skl2onnx.common.data_types import FloatTensorType
# import onnx

# # Generate a sample dataset
# X, y = make_classification(n_samples=100, n_features=4, n_informative=2, n_redundant=0, random_state=42)

# # Create and train a Random Forest classifier
# rf_classifier = RandomForestClassifier(n_estimators=10, max_depth=5, random_state=42)
# rf_classifier.fit(X, y)

# # Specify the input feature shape
# initial_type = [('float_input', FloatTensorType([None, 4]))]

# # Convert the model to ONNX
# onnx_model = convert_sklearn(rf_classifier, initial_types=initial_type)

# # Manually set the IR version to 9
# onnx_model.ir_version = 9

# # Update the opset import to version 9
# for opset in onnx_model.opset_import:
#     if opset.domain == '' or opset.domain == 'ai.onnx':
#         opset.version = 9

# # Save the ONNX model
# onnx.save(onnx_model, "random_forest_model_v9.onnx")

# print("Random Forest model has been converted to ONNX format (IR version 9) and saved as 'random_forest_model_v9.onnx'")

# # Optional: Verify the model
# import onnxruntime as rt

# sess = rt.InferenceSession("random_forest_model_v9.onnx")
# input_name = sess.get_inputs()[0].name
# label_name = sess.get_outputs()[0].name

# # Test prediction
# test_input = X[:1].astype(np.float32)
# pred_onnx = sess.run([label_name], {input_name: test_input})[0]
# print(f"ONNX model prediction: {pred_onnx}")

# # Compare with original sklearn model
# pred_sklearn = rf_classifier.predict(test_input)
# print(f"sklearn model prediction: {pred_sklearn}")

# assert np.array_equal(pred_onnx, pred_sklearn), "Predictions don't match!"
# print("Conversion successful: ONNX and sklearn predictions match.")

# # Verify the IR version
# loaded_model = onnx.load("random_forest_model_v9.onnx")
# print(f"ONNX model IR version: {loaded_model.ir_version}")