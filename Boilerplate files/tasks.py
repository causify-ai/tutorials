from invoke import task
import os

@task
def docker_build_local_image(c):
    c.run("docker build -t tutor_bitcoin_s3fs .")

@task
def docker_bash(c, stage="local", version="1.0.0", skip_pull=False):
    c.run("docker run -it --rm -v $(pwd):/app tutor_bitcoin_s3fs bash")

@task
def docker_jupyter(c, stage="local", version="1.0.0", skip_pull=False, detach=False):
    cmd = "docker run -it --rm -p 8888:8888 -v $(pwd):/app tutor_bitcoin_s3fs jupyter lab --ip=0.0.0.0 --no-browser --allow-root"
    if detach:
        cmd = cmd.replace(" -it ", " -d ")
    c.run(cmd)

@task
def clean(c):
    c.run("find . -type d -name '__pycache__' -exec rm -r {} +")
    c.run("find . -type f -name '*.pyc' -delete")
    c.run("rm -rf .pytest_cache .mypy_cache .ipynb_checkpoints")

@task
def test(c):
    c.run("pytest")
