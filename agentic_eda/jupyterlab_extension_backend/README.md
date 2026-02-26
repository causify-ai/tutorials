# JupyterLab Extension Backend

Run the backend entrypoint from this directory:

```bash
cd /Users/indro/src/tutorials1/agentic_eda/jupyterlab_extension_backend
python -m src.main \
  --mode integrity \
  --path /Users/indro/src/tutorials1/agentic_eda/jupyterlab_extension_backend/datasets/T1_slice.csv
```

If you run from a different directory, set `PYTHONPATH`:

```bash
PYTHONPATH=/Users/indro/src/tutorials1/agentic_eda/jupyterlab_extension_backend \
python -m src.main \
  --mode integrity \
  --path /Users/indro/src/tutorials1/agentic_eda/jupyterlab_extension_backend/datasets/T1_slice.csv
```
