import papermill as pm

#!/bin/bash

# Automatically run the main notebook using Papermill
echo "🔁 Running LightGBM.example.ipynb using Papermill..."

papermill LightGBM.example.ipynb output.ipynb

echo "✅ Finished execution. Output saved to output.ipynb"
