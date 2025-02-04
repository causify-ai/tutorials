"""
Import as:

import optimizer.opt_lib_tasks as ooplitas
"""

import logging
import os
from typing import Optional

from invoke import task

import helpers.hgit as hgit
import helpers.lib_tasks_docker as hlitadoc
import helpers.lib_tasks_docker_release as hltadore
import helpers.lib_tasks_pytest as hlitapyt
import helpers.lib_tasks_utils as hlitauti

_LOG = logging.getLogger(__name__)

# pylint: disable=protected-access


_CURRENT_DIR = os.path.join(hgit.get_client_root(super_module=False), "pymc")


# #############################################################################
# Docker image release.
# #############################################################################


# TODO(gp): Since this is just a wrapper maybe we should just use *,
#  ** to forward the parameters.
@task
def opt_docker_build_local_image(  # type: ignore
    ctx,
    version,
    cache=True,
    base_image="",
    poetry_mode="update",
):
    """
    Build a local `opt` image (i.e., a release candidate "dev" image).

    See the corresponding `invoke` target for the main container.
    """
    hltadore.docker_build_local_image(
        ctx,
        version,
        cache=cache,
        base_image=base_image,
        poetry_mode=poetry_mode,
        container_dir_name=_CURRENT_DIR,
    )


@task
def opt_docker_tag_local_image_as_dev(  # type: ignore
    ctx,
    version,
    base_image="",
):
    """
    (ONLY CI/CD) Mark the `opt:local` image as `dev`.

    See the corresponding `invoke` target for the main container.
    """
    hltadore.docker_tag_local_image_as_dev(
        ctx,
        version,
        base_image=base_image,
        container_dir_name=_CURRENT_DIR,
    )


@task
def opt_docker_push_dev_image(  # type: ignore
    ctx,
    version,
    base_image="",
):
    """
    (ONLY CI/CD) Push the `opt:dev` image to ECR.

    See the corresponding `invoke` target for the main container.
    """
    hltadore.docker_push_dev_image(
        ctx, version, base_image=base_image, container_dir_name=_CURRENT_DIR
    )


@task
def opt_docker_release_dev_image(  # type: ignore
    ctx,
    version,
    cache=True,
    push_to_repo=True,
    update_poetry=False,
):
    """
    (ONLY CI/CD) Build, test, and release to ECR the latest `opt:dev` image.

    See the corresponding `invoke` target for the main container.
    """
    hltadore.docker_release_dev_image(
        ctx,
        version,
        cache=cache,
        # TODO(Grisha): replace with `opt` tests.
        skip_tests=True,
        fast_tests=False,
        slow_tests=False,
        superslow_tests=False,
        # TODO(Grisha): enable `qa` tests.
        qa_tests=False,
        push_to_repo=push_to_repo,
        update_poetry=update_poetry,
        container_dir_name=_CURRENT_DIR,
    )


# #############################################################################
# Docker development.
# #############################################################################


@task
def opt_docker_pull(ctx, stage="dev", version=None, skip_pull=False):  # type: ignore
    """
    Pull the latest dev `opt` image from the Docker registry.
    """
    hlitauti.report_task()
    if skip_pull:
        _LOG.warning("Skipping pulling docker image as per user request")
        return
    #
    base_image = ""
    hlitadoc._docker_pull(ctx, base_image, stage, version)


@task
def opt_docker_bash(  # type: ignore
    ctx,
    base_image="",
    stage="dev",
    version="",
    use_entrypoint=True,
    as_user=True,
    skip_pull=False,
):
    """
    Start a bash shell inside the `opt` container corresponding to a stage.

    See the corresponding `invoke` target for the main container.
    """
    hlitadoc.docker_bash(
        ctx,
        base_image=base_image,
        stage=stage,
        version=version,
        use_entrypoint=use_entrypoint,
        as_user=as_user,
        container_dir_name=_CURRENT_DIR,
        skip_pull=skip_pull,
    )


@task
def opt_docker_jupyter(  # type: ignore
    ctx,
    stage="dev",
    version="",
    base_image="",
    auto_assign_port=True,
    use_entrypoint=True,
    port=9999,
    self_test=False,
    skip_pull=False,
):
    """
    Run Jupyter notebook server in the `opt` container.

    See the corresponding `invoke` target for the main container.
    """
    hlitadoc.docker_jupyter(
        ctx,
        stage=stage,
        version=version,
        base_image=base_image,
        auto_assign_port=auto_assign_port,
        use_entrypoint=use_entrypoint,
        port=port,
        self_test=self_test,
        container_dir_name=_CURRENT_DIR,
        skip_pull=skip_pull,
    )


@task
def opt_docker_cmd(  # type: ignore
    ctx,
    base_image="",
    stage="dev",
    version="",
    cmd="",
    as_user=True,
    use_bash=False,
):
    """
    Run a command inside the `opt` container corresponding to a stage.

    See the corresponding `invoke` target for the main container.
    """
    hlitadoc.docker_cmd(
        ctx,
        base_image=base_image,
        stage=stage,
        version=version,
        cmd=cmd,
        as_user=as_user,
        use_bash=use_bash,
        container_dir_name=_CURRENT_DIR,
    )


# #############################################################################
# Run tests.
# #############################################################################


# TODO(Grisha): Pass a test_list in fast, slow, ... instead of duplicating all
#  the code CmTask #1571.
@task
def opt_run_fast_tests(
    ctx,
    stage="dev",
    version="",
    use_opt_test_marker=False,
    pytest_opts="",
    coverage=False,
    collect_only=False,
    tee_to_file=False,
    n_threads="1",
    **kwargs,
):
    """
    Run fast tests from the `optimizer` dir inside the `opt` container
    corresponding to a stage.

    See the corresponding `invoke` target for the main container.

    :param use_opt_test_marker: whether to run only the tests marked as
        `optimizer` tests
    """
    test_list_name = "fast_tests"
    if use_opt_test_marker:
        # Run only the tests marked as `optimizer`.
        custom_marker = "optimizer"
    else:
        custom_marker = ""
    # Run only the tests in the `optimizer` dir.
    pytest_opts = "optimizer"
    # False since optimizer doesn't have a submodule.
    skip_submodules = False
    # False since we cannot call `git_clean` invoke from the `optimizer` dir.
    git_clean = False
    rc = hlitapyt._run_tests(
        ctx,
        test_list_name,
        stage,
        version,
        custom_marker,
        pytest_opts,
        skip_submodules,
        coverage,
        collect_only,
        tee_to_file,
        n_threads,
        git_clean,
        **kwargs,
    )
    return rc


@task
def opt_run_slow_tests(
    ctx,
    stage="dev",
    version="",
    use_opt_test_marker=False,
    pytest_opts="",
    coverage=False,
    collect_only=False,
    tee_to_file=False,
    n_threads="1",
    **kwargs,
):
    """
    Run slow tests from the `optimizer` dir inside the `opt` container
    corresponding to a stage.

    See the corresponding `invoke` target for the main container.

    :param use_opt_test_marker: whether to run only the tests marked as
        `optimizer` tests
    """
    test_list_name = "slow_tests"
    if use_opt_test_marker:
        # Run only the tests marked as `optimizer`.
        custom_marker = "optimizer"
    else:
        custom_marker = ""
    # Run only the tests in the `optimizer` dir.
    pytest_opts = "optimizer"
    # False since optimizer doesn't have a submodule.
    skip_submodules = False
    # False since we cannot call `git_clean` invoke
    # from the `optimizer` dir.
    git_clean = False
    rc = hlitapyt._run_tests(
        ctx,
        test_list_name,
        stage,
        version,
        custom_marker,
        pytest_opts,
        skip_submodules,
        coverage,
        collect_only,
        tee_to_file,
        n_threads,
        git_clean,
        **kwargs,
    )
    return rc


# #############################################################################
# Start/stop optimizer services.
# #############################################################################


def _get_opt_docker_up_cmd(
    detach: bool, base_image: str, stage: str, version: Optional[str]
) -> str:
    """
    Get `docker-compose up` command for the optimizer service.

    E.g.,
    ```
    IMAGE=*****.dkr.ecr.us-east-1.amazonaws.com/opt:dev \
        docker-compose \
        --file devops/compose/docker-compose.yml \
        --env-file devops/env/default.env \
        up \
        -d \
        app
    ```

    :param detach: whether to run in detached mode or not
    """
    service_name = "app"
    generate_docker_compose_file = True
    extra_env_vars = None
    extra_docker_compose_files = None
    docker_up_cmd_ = hlitadoc._get_docker_base_cmd(
        base_image,
        stage,
        version,
        service_name,
        generate_docker_compose_file,
        extra_env_vars,
        extra_docker_compose_files,
    )
    # Add up command.
    docker_up_cmd_.append(
        r"""
        up"""
    )
    if detach:
        # Run in detached mode.
        docker_up_cmd_.append(
            r"""
        -d"""
        )
    # Specify the service name.
    service = "app"
    docker_up_cmd_.append(
        rf"""
        {service}"""
    )
    #
    docker_up_cmd = hlitauti.to_multi_line_cmd(docker_up_cmd_)
    return docker_up_cmd  # type: ignore[no-any-return]


@task
def opt_docker_up(  # type: ignore
    ctx, detach=True, base_image="", stage="dev", version=""
):
    """
    Start the optimizer as a service.
    """
    # Build `docker-compose up` cmd.
    docker_up_cmd = _get_opt_docker_up_cmd(detach, base_image, stage, version)
    # Run.
    hlitauti.run(ctx, docker_up_cmd, pty=True)


# TODO(gp): @all merge this command with the up command passing a `mode` switch.
def _get_opt_docker_down_cmd(
    base_image: str, stage: str, version: Optional[str]
) -> str:
    """
    Get `docker-compose down` command for the optimizer.

    E.g.,
    ```
    IMAGE=*****.dkr.ecr.us-east-1.amazonaws.com/opt:dev \
        docker-compose \
        --file devops/compose/docker-compose.yml \
        --env-file devops/env/default.env \
        down
    ```
    """
    service_name = "app"
    generate_docker_compose_file = True
    extra_env_vars = None
    extra_docker_compose_files = None
    docker_down_cmd_ = hlitadoc._get_docker_base_cmd(
        base_image,
        stage,
        version,
        service_name,
        generate_docker_compose_file,
        extra_env_vars,
        extra_docker_compose_files,
    )
    # Add down command.
    docker_down_cmd_.append(
        r"""
        down"""
    )
    docker_down_cmd = hlitauti.to_multi_line_cmd(docker_down_cmd_)
    return docker_down_cmd  # type: ignore[no-any-return]


@task
def opt_docker_down(ctx, base_image="", stage="dev", version=""):  # type: ignore
    """
    Bring down the optimizer service.
    """
    # Build `docker-compose down` cmd.
    docker_down_cmd = _get_opt_docker_down_cmd(base_image, stage, version)
    # Run.
    hlitauti.run(ctx, docker_down_cmd, pty=True)
