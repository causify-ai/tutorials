#!/bin/bash -e

# Parse params.
export JUPYTER_HOST_PORT=8888
export JUPYTER_USE_VIM=0
export TARGET_DIR=""
export VERBOSE=0

OLD_CMD_OPTS=$@
while getopts p:d:uv flag
do
    case "${flag}" in
        p) JUPYTER_HOST_PORT=${OPTARG};;
        u) JUPYTER_USE_VIM=1;;
        d) TARGET_DIR=${OPTARG};;
        # /Users/saggese/src/git_gp1/code/
        v) VERBOSE=1;;
    esac
done

if [[ $VERBOSE == 1 ]]; then
    set -x
fi;

jupyter nbextension enable autosavetime/main

if [[ $JUPYTER_USE_VIM != 0 ]]; then
    jupyter nbextension enable vim_binding/vim_binding
fi;

cat << EOT >> ~/.jupyter/jupyter_notebook_config.py
#------------------------------------------------------------------------------
# Jupytext
#------------------------------------------------------------------------------
# The following line yields:
# ```
# [C 14:54:35.676 NotebookApp] Bad config encountered during initialization:
# The 'contents_manager_class' trait of a NotebookApp instance expected a
# subclass of notebook.services.contents.manager.ContentsManager or
# jupyter_server.contents.services.managers.ContentsManage, not the
# JupytextContentsManager JupytextContentsManager.
# ```
# Not needed according to https://bytemeta.vip/repo/mwouts/jupytext/issues/953
#c.NotebookApp.contents_manager_class = "jupytext.TextFileContentsManager"
# Always pair ipynb notebooks to py files
c.ContentsManager.default_jupytext_formats = "ipynb,py"
# Use the percent format when saving as py
c.ContentsManager.preferred_jupytext_formats_save = "py:percent"
c.ContentsManager.outdated_text_notebook_margin = float("inf")
EOT

mkdir -p ~/.jupyter/nbextensions/autosavetime
cat << EOT >> ~/.jupyter/nbextensions/autosavetime/main.js
var params = {
    autosavetime_set_starting_interval: 1,
    autosavetime_starting_interval: 1,
    autosavetime_show_selector : false,
}
EOT

# Run Jupyter.
jupyter-notebook \
    --port=$JUPYTER_HOST_PORT \
    --no-browser \
    --ip=* \
    --NotebookApp.token='' --NotebookApp.password='' \
    --allow-root
