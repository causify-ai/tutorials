

<!-- toc -->

- [Tutorials "Learn X in 60 minutes"](#tutorials-learn-x-in-60-minutes)
  * [What are the goals for each tutorial](#what-are-the-goals-for-each-tutorial)

<!-- tocstop -->

# Tutorials "Learn X in 60 minutes"

- The goal is to give everything needed for someone to become familiar with a big
  data / AI / LLM / data science technology in 60 minutes.

- Each tutorial corresponds to a directory in the `//tutorials` repo
  [https://github.com/causify-ai/tutorials](https://github.com/causify-ai/tutorials)
  with

- Each tutorial contains:
  1) A Docker container with everything needed to build and run using the Causify
     dev-system format
  2) A markdown `XYZ.API.md` about
     - the native API
     - the software layer written by us on top of the native API
  3) A Jupyter notebook `XYZ.API.ipynb` with an example of using the native / our
     APIs
  4) A markdown `XYZ.example.md` with a full example of an application using the
     API
  5) A Jupyter notebook `XYZ.example.md` with a full example
  6) A file `XYZ_utils.py` with utility functions

## README format
- Each project contains a readme summarizing its status

## What are the goals for each tutorial

- All the code is on GitHub in a format common to all the tutorials
- Each tutorial conceptually corresponds to a blog entry

### Docker container
- The Docker container should:
  1. Contain everything so that one is ready to run tutorials and develop with
     that technology
     - Often installing and getting a package to work (e.g., PyMC) takes a long
       time

### Jupyter notebooks
- Each Jupyter notebook should:
  3. Run end-to-end after a restart
     - This is enforced by the unit test through `pytest`
     - In this way we are guaranteed that it works
     - It's super frustrating when a tutorial doesn't work because the version of
       the library is not compatible with the code anymore
  2. Be self-contained and linear
     - Each example is explained thoroughly without having to jump from tutorial
       to tutorial
     - Each cell and its output is commented and explained
  4. Take less than few minutes to execute end-to-end

### Markdown
- Markdown documents should cover information about:
  - What it is the Python package / library
  - What problem it solves
  - What are the alternatives, both open source and commercial with comments about
    advantages and disadvantages
  - A description of the native API, i.e., the package
  - A description of the Docker container
  - Visual aids with `mermaid` (e.g., flow diagrams, data transformation steps,
    and plots) to enhance understanding of how the library and the example works
  - References to books and in-depth tutorial that we have run and we think are
    awesome
  - All sources should be referred and acknowledged

- This is the same approach we use in [DATA605
  tutorials](https://github.com/gpsaggese/umd_data605/tree/main/tutorials) even
  these tutorials don't use the Causify dev system, but some simpler bash scripts
  - Git
  - Docker
  - Docker compose
  - Postgres
  - MongoDB
  - Airflow
  - Dask
  - Spark
