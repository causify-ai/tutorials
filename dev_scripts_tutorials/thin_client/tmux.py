#!/usr/bin/env python3
"""
Check whether a tmux session exists and, if not, creates it.
"""

import logging
import os
import sys

# To customize: xyz
_HAS_SUBREPO = True

_SCRIPT_PATH = os.path.abspath(__file__)

if _HAS_SUBREPO:
    # Change the directory to the real directory if we are in a symlink.
    dir_name = os.path.dirname(os.path.realpath(_SCRIPT_PATH)) + "/../.."
    # print(dir_name)
    os.chdir(dir_name)

# We need to tweak `PYTHONPATH` directly since we are bootstrapping the system.
sys.path.append("helpers_root/dev_scripts_helpers/thin_client")
import thin_client_utils as tcu

#sys.path.append("helpers_root/helpers")
#import helpers.hdbg as hdbg

_LOG = logging.getLogger(__name__)


if __name__ == "__main__":
    parser = tcu.create_parser(__doc__)
    if _HAS_SUBREPO:
        # To customize: xyz
        dir_prefix = "tutorials"
    else:
        # `helpers` has no super-repo.
        dir_prefix = "helpers"
    setenv_path = os.path.join(f"dev_scripts_{dir_prefix}", "thin_client",
                               "setenv.sh")
    tcu.create_tmux_session(
        parser, _SCRIPT_PATH, dir_prefix, setenv_path, _HAS_SUBREPO
    )
