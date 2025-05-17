# Bitcoin Time Series Analysis with EconML

This project applies **Microsoft's EconML** library to perform **causal inference** on real-time Bitcoin pricing data. The goal is to estimate the causal effect of external trends (e.g., Google Trends) on Bitcoin returns using advanced machine learning models like DML, DR Learner, and Causal Forests.

---

## Project Structure

```bash
.
├── bitcoin_utils.py          # Core module with reusable functions and models
├── Bitcoin.API.ipynb         # Demo: How to use the API and wrapper layer
├── Bitcoin.API.md            # Explanation of API design and decisions
├── Bitcoin.example.ipynb     # Example notebook using the API in practice
├── Bitcoin.example.md        # Explanation of the example and model outputs
├── Dockerfile                # Build recipe for the reproducible Docker image
├── run_jupyter.sh            # Startup script for launching Jupyter in Docker
├── requirements.txt          # Python dependencies (used inside container)
