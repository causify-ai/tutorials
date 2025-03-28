import os

import numpy as np
import logging

import arviz as az
import pymc as pm
import numpy as np
import seaborn as sns
import scipy.stats as stats
import matplotlib.pyplot as plt
import preliz as pz


def set_notebook_style() -> None:
    print("# Setting notebook style")
    plt.rcParams['figure.figsize'] = [8, 3]


def notebook_signature() -> None:
    print("# Notebook signature")
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


def config_notebook() -> None:
    set_notebook_style()
    notebook_signature()


def obj_to_str(var_name: str, val: any, top_n: int = 3) -> str:
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


def print_obj(*args: any, **kwargs: any) -> None:
    print(obj_to_str(*args, **kwargs))


dst_dir = "./figures"
if not os.path.exists(dst_dir):
    os.makedirs(dst_dir)


# Lesson 7, notebook 1


def convert_to_filename(string: str) -> str:
    string = string.replace(":", "")
    return string.replace(' ', '').replace('.', '_')


def print_figure(file_name: str) -> None:
    txt = f"![Fig]({file_name})" + "{ width=100px }"
    print(txt)


def plot_binomial() -> None:
    n_params = [2, 4, 8]
    p_params = [0, 0.25, 0.5, 0.75, 1]
    max_n = max(n_params)
    # Create a plot.
    _, ax = plt.subplots(len(n_params),
                        len(p_params),
                        sharex=True,
                        sharey=True,
                        figsize=(9, 7),
                        # Fit plots into the figure cleanly.
                        constrained_layout=True)
                        #constrained_layout=False)
    for i in range(len(n_params)):
        for j in range(len(p_params)):
            #x = list(range(1, i + 1))
            x = list(range(1, max_n + 1))
            n = n_params[i]
            p = p_params[j]
            # Evaluate the PDF in several points.
            y = stats.binom(n=n, p=p).pmf(x)
            y = [y[k] if k < n else np.nan for k in range(max_n)]
            #print(n, p, x, y)
            # Plot the PDF.
            ax[i, j].plot(x, y, marker='o', linestyle='-')
            # Add the legend.
            ax[i, j].plot([], label="n={:3.2f}\np={:3.2f}".format(n, p), alpha=0)
            ax[i, j].legend(loc=1)
    ax[2, 1].set_xlabel('x')
    ax[1, 0].set_ylabel('p(x)', rotation=0, labelpad=20);
    #ax[1, 0].set_yticks([])
    ax[1, 0].set_xticks(range(1, max_n + 1))
    #
    title = "Chap7: Binomial distribution"
    plt.title(title)
    file_name = os.path.join(dst_dir, convert_to_filename(title))
    plt.savefig(file_name, dpi=300)
    #
    print_figure(file_name)



def plot_beta():
    params1 = [0.8, 1.0, 2.0, 4.0]
    params2 = [0.8, 1.0, 2.0, 4.0]
    x = np.linspace(0, 1, 200)
    # Create a plot.
    _, ax = plt.subplots(len(params1),
                        len(params2),
                        sharex=True,
                        sharey=True,
                        figsize=(9, 7),
                        # Fit plots into the figure cleanly.
                        constrained_layout=True)
                        #constrained_layout=False)
    for i in range(len(params1)):
        for j in range(len(params2)):
            param1 = params1[i]
            param2 = params2[j]
            # Evaluate the PDF in several points.
            y = stats.beta(a=param1, b=param2).pdf(x)
            # Plot the PDF.
            ax[i, j].plot(x, y)
            # Add the legend.
            ax[i, j].plot([], label="a={:3.2f}\nb={:3.2f}".format(param1, param2), alpha=0)
            ax[i, j].legend(loc=1)
    ax[2, 1].set_xlabel('x')
    ax[1, 0].set_ylabel('p(x)', rotation=0, labelpad=20);
    #ax[1, 0].set_yticks([])