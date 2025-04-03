# Tutorial Template: Two Docker Approaches

This directory provides two versions of the same tutorial setup to help you work with Jupyter notebooks and Python scripts inside Docker environments. Both versions run the same code but use **different Docker configurations**.

## 1. `tutorial_causify_way/` (Thin Docker Environment)

- This setup reflects the **thin Docker layer** approach commonly used in production environments (e.g., at Causify-AI).
- It is lightweight and mirrors real-world deployment workflows.
- **Recommended** for students familiar with Docker or those wishing to explore a production-like setup.
- For thin environment setup instructions, refer to:  
  [How to Set Up Development on Laptop](https://github.com/causify-ai/helpers/blob/757fa710f3a293b2d3ab5c4586de04faa1e5e99b/docs/onboarding/intern.set_up_development_on_laptop.how_to_guide.md)

## 2. `tutorial_data605_way/` (Simple Docker Environment)

- This version is modeled after the setup used in **DATA605 tutorials**.
- It uses a pre-built Docker image [`pmodi08/umd_data605_template`](https://hub.docker.com/r/pmodi08/umd_data605_template) that comes with Python, Jupyter, and all required packages pre-installed.
- This template provides a ready-to-run environment, including scripts to build, run, and clean the Docker container.

> **Note:** The image `pmodi08/umd_data605_template` is a starting point to help you quickly get up and running. For your specific project, you should:
> - Modify the Dockerfile to add project-specific dependencies
> - Update bash/scripts accordingly
> - Expose additional ports if your project requires them

## Reference Tutorials

- The `tutorial_github` example has been implemented in **both environments** for you to refer to:
  - `tutorial_github_causify/` uses the thin Docker layer setup.
  - `tutorial_github_data605/` uses the simple pre-built image setup.

Choose the approach that best fits your comfort level and project needs. Both are valid depending on your use case.
