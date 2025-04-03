# GitHub Tutorial (Simpler Docker Layer)

This repository contains two versions of the GitHub Stats tutorial:

- `tutorial_github`: Runs in a **thin Docker environment**, which is lightweight and closer to a production setup. This is the approach commonly used at Causify-AI and is encouraged for students comfortable with Docker and environment setup.
- `tutorial_github_simple`: Uses a **simple Docker-based setup**, similar to the ones used in `DATA605` tutorials. It relies on a pre-built image (`pmodi08/umd_data605_template`) hosted on Docker Hub and includes all the necessary dependencies (Python, Jupyter, required packages) out of the box.

If you encounter difficulties with the thin environment or want a quick, reliable alternative to get started, `tutorial_github_simple` is a sample that you can refer.

For instructions on setting up the **thin environment**, refer to this guide:  
[How to Set Up Development on Laptop](https://github.com/causify-ai/helpers/blob/757fa710f3a293b2d3ab5c4586de04faa1e5e99b/docs/onboarding/intern.set_up_development_on_laptop.how_to_guide.md)

## Run Instructions

This tutorial uses the pre-built Docker image available on Docker Hub: `pmodi08/umd_data605_template`.

### 1. Start the container

```bash
> ./docker_bash.sh
```

This mounts the current tutorial directory and opens an interactive bash session in the container.

### 2. Inside the container, start Jupyter

```bash
> /data/run_jupyter.sh
```

You will see output showing that Jupyter is running on port 8888.

### 3. Open in browser

Go to [http://localhost:8888](http://localhost:8888) in your web browser.

### 4. Open the notebook

Navigate to:

```
data/tutorial_github_simple/github.example.ipynb
```

Run the cells to in the notebook using the provided code.