import papermill as pm

print("🔁 Running LightGBM Bitcoin pipeline...")
pm.execute_notebook(
    "LightGBM.example.ipynb",
    "output.ipynb",
    kernel_name="python3"
)
print("✅ Pipeline executed and saved to output.ipynb.")
