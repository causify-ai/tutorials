import os

import numpy as np

def notebook_signature():

    cmd = "python --version"
    os.system(cmd)

    cmd = "uname -a"
    os.system(cmd)

    modules = ["numpy", "pymc", "matplotlib", "arviz", "preliz"]
    for module in modules:
        cmd = f"import {module}"
        exec(cmd)
        version = eval(f"{module}.__version__")
        print(f"{module} version={version}")


def obj_to_str(var_name, val, top_n=3):
    txt = []
    txt_tmp = "var_name=%s (type=%s)" % (var_name, str(type(val)))
    txt.append(txt_tmp)
    if isinstance(val, np.ndarray):
        txt.append("shape=%s" % val.shape)
        if len(val.shape) == 1:
            txt_tmp = "%s ... %s" % (val[:top_n], val[-top_n:])
            txt_tmp = txt_tmp.replace("[", "")
            txt_tmp = txt_tmp.replace("]", "")
            txt_tmp = f"[{txt_tmp}]"
            txt.append(txt_tmp)
    return "\n".join(txt)


def print_obj(*args, **kwargs):
    print(obj_to_str(*args, **kwargs))
