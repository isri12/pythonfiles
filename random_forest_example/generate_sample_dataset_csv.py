import numpy as np
import pandas as pd
from sklearn.datasets import make_classification

# Generate a sample dataset
X, y = make_classification(n_samples=100, n_features=4, n_informative=2, n_redundant=0, random_state=42)

# Create a DataFrame
df = pd.DataFrame(X, columns=['feature1', 'feature2', 'feature3', 'feature4'])
df['target'] = y

# Save the DataFrame to a CSV file
df.to_csv('sample_data.csv', index=False)
print("Sample data saved to 'sample_data.csv'")