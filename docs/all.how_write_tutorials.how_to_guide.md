

<!-- toc -->

- [Tutorials "Learn X in 60 minutes"](#tutorials-learn-x-in-60-minutes)
  * [What are the goals for each tutorial](#what-are-the-goals-for-each-tutorial)

<!-- tocstop -->

# Tutorials "Learn X in 60 minutes"

The goal is to give everything needed for one person to become familiar with a
Big data / AI / LLM / data science technology in 60 minutes.

- Each tutorial conceptually corresponds to a blog entry.

Each tutorial corresponds to a directory in the `//tutorials` repo
[https://github.com/causify-ai/tutorials](https://github.com/causify-ai/tutorials)
with

- A markdown \`XYZ.API.md\` about the API and the software layer written by us
  on top of the native API
- A markdown `XYZ.example.md` with a full example of an application using the
  API
- A Docker container with everything you need in our Causify dev-system format
- A Jupyter notebook with an example of APIs
- A Jupyter notebook with a full example

## What are the goals for each tutorial

Docker container

- Provides a Docker container with everything installed and ready to run
  tutorials and develop with that technology
  - Often installing the package and get it to work takes long to figure out
- All the code is on GitHub in a common format to all tutorials

Jupyter notebooks

- Each Jupyter notebook should
  - Be unit tested so that you are guaranteed that it works
    - It's super frustrating when a tutorial doesn't work because the version of
      the library is not compatible with the code anymore
  - Be self-contained and linear: each example is explained thoroughly without
    having to jump from tutorial to tutorial
    - Each cell and its output is commented and explained
  - Run end-to-end after a restart (we can add a unit test for it)
  - Take less than few minutes to execute end-to-end

Markdown documents should cover:

- What it is the package
- What problem it solves
- What are the alternatives, both open source and commercial with comments about
  advantages and disadvantages
- Describe the native API
- Description of the Docker container
- Visual aids with mermaid (e.g., flow diagrams, data transformation steps, and
  plots) to enhance understanding
- References to books and in-depth tutorial that we have run and we think are
  awesome
- All sources should be referred and acknowledged

This is the same approach we use in DATA605 tutorials
https://github.com/gpsaggese/umd\_data605/tree/main/tutorials, e.g.,

- Git
- Docker
- Docker compose
- Postgres
- MongoDB
- Airflow
- Dask
- GitHub
- Spark
