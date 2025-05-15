# Real-Time Bitcoin Price Analysis using Databricks CLI

**Author**: Ritik Pratap Singh  
**Date**: 2025-04-30  
**Course**: DATA605 — Spring 2025

---

## 1. Project Overview

This project builds an automated pipeline to:

1. Fetch real-time Bitcoin prices from the CoinGecko API  
2. Upload data to Databricks DBFS  
3. Run a time-series forecast (ARIMA) on a Databricks cluster  
4. Download forecast results and visualize them locally  
5. Tear down cloud resources—all via the Databricks CLI

There are two primary entry points:

- **`databricks_cli.API.py`** — demo of core CLI commands  
- **`databricks_cli.example.py`** — end-to-end pipeline runner  

For interactive, cell-by-cell exploration, see the companion notebooks.

---

## 2. Project Files

```text
databricks_cli_utils.py         # shared helpers for CLI, data fetch, modeling, plotting
databricks_cli.API.py           # one-shot demo of all CLI wrappers
databricks_cli.API.ipynb        # interactive API walkthrough
databricks_cli.API.md           # markdown docs for API.py

databricks_cli.example.py       # one-shot pipeline runner (fetch→forecast→plot)
databricks_cli.example.ipynb    # interactive pipeline walkthrough
databricks_cli.example.md       # markdown docs for example.py

bitcoin_analysis.ipynb          # analysis notebook to upload into Databricks workspace

config/
  ├─ cluster_config.json        # cluster creation spec
  └─ cluster_id.txt             # saved cluster ID after create

data/
  ├─ bitcoin_price.json         # appended price records
  └─ forecast_output.csv        # downloaded forecast results

output_plots/
  ├─ historical.png             # local historical plot
  └─ forecast.png               # local forecast plot

scripts/                        # auxiliary shell scripts
requirements.txt                # Python dependencies
Dockerfile                      # image spec (DATA605 style)
docker_build.sh                 # build image
docker_bash.sh                  # start bash shell
docker_jupyter.sh               # launch JupyterLab
docker_name.sh                  # tagging helper
```

---

## 3. Prerequisites & Setup

1. **Clone the repo & navigate**  
   ```bash
   git clone https://github.com/causify-ai/tutorials.git
   cd tutorials/DATA605/Spring2025/projects/TutorTask92_Spring2025_Real_Time_Bitcoin_Price_Analysis_with_Databricks_CLI
   ```
2. **Install Docker** (Desktop/Engine)  
3. **Generate a Databricks PAT** from User Settings → Access Tokens  
4. **(Local) Python 3.8+** for initial CLI configuration

---

## 4. Build & Run Docker (data605_style)

**Note**: I have copied the `install_jupyter_extensions.sh` & `bashrc` from  `docker_common` into my local project folder. Also I have slightly modified docker- bash,build and Dockfile.

1. **Build the image**  
   ```bash
   chmod +x docker_*.sh
   ./docker_build.sh
   ```
2. **Start an interactive shell** (mounts your CLI config for persistence)  
   ```bash
   ./docker_bash.sh --mount-config
   ```
3. **Launch JupyterLab**  
   ```bash
   ./docker_jupyter.sh --mount-config
   ```
   - Visit `http://localhost:8888/lab?token=...`

> **Tip:** If you’d rather pass your host credentials as env-vars instead of mounting:
> ```bash
> docker run --rm -it \
>   -e DATABRICKS_HOST="https://<workspace>.cloud.databricks.com" \
>   -e DATABRICKS_TOKEN="dapiXXXX" \
>   -v "$(pwd)":/data -p 8888:8888 \
>   umd_data605/bitcoin_cli_project \
>   bash
> ```

---

## 5. Prepare Databricks Workspace

1. **Upload** `bitcoin_analysis.ipynb` into your workspace.  
2. **Copy its path** (e.g. `/Users/you@example.com/bitcoin_analysis`).  
3. **Set** `ANALYSIS_NOTEBOOK_PATH` in `databricks_cli.example.ipynb`.  
4. **Verify** `config/cluster_config.json` matches your workspace’s available versions.

---

## 6. Usage

### 6.1 Run the API demo script  
```bash
python databricks_cli.API.py
```  
This will:

- Create a cluster  
- Check status  
- Upload/download a test file  
- Submit and poll a job run  
- Delete the cluster  

### 6.2 Run the full pipeline script  
```bash
python databricks_cli.example.py
```  
This executes the entire fetch→forecast→plot flow and writes visuals to `output_plots/`.

### 6.3 Interactive Notebooks  
Open in JupyterLab and **Restart & Run All**:

- `databricks_cli.API.ipynb`  
- `databricks_cli.example.ipynb`

---

## 7. Batch Execution

```bash
docker run --rm -v "$(pwd)":/data umd_data605/bitcoin_cli_project \
  bash -c "cd /data && \
    jupyter nbconvert --to notebook --execute \
      databricks_cli.example.ipynb \
      --output executed_example.ipynb"
```

---

## 8. Troubleshooting

- **No `/data` dir**: Use Bash (Git Bash/WSL) not PowerShell.  
- **CLI failures**: Ensure `--mount-config` or env-vars are set correctly.  
- **Port conflicts**: Change `-p 8888:8888` in Docker run.

---

## 9. References

- [Databricks CLI Docs](https://docs.databricks.com/en/dev-tools/cli/index.html)  
- [CoinGecko API Docs](https://www.coingecko.com/en/api)  
- [Statsmodels ARIMA Docs](https://www.statsmodels.org/stable/generated/statsmodels.tsa.arima.model.ARIMA.html)