from tools.ipynb_tools import write_notebook

spec = {
    "cells": [
        {"type": "markdown", "source": "# Tool-written notebook"},
        {"type": "code", "source": "print('ok')"},
    ]
}

print(write_notebook.invoke({"spec": spec, "out_rel": "tool_hello.ipynb"}))
