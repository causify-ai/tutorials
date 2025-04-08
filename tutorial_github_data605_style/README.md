# GitHub Tutorial DATA605 style

## Run instructions

1. Build the container
   - Update requirements.txt
   ```bash
   > ./docker_build.sh
   ```

2. Start the container
   ```bash
   > ./docker_bash.sh
   ```
   - This mounts the current tutorial directory and opens an interactive bash
     session in the container.

3. Inside the container, start Jupyter
   ```bash
   > /data/run_jupyter.sh
   ```
   - You will see output showing that Jupyter is running on port 8888.

4. Open in browser
   - Go to [http://localhost:8888](http://localhost:8888) in your web browser

5. Open the notebook
   - Navigate to `data/tutorial_github_simple/github.example.ipynb`
   - Run the cells to in the notebook using the provided code.
