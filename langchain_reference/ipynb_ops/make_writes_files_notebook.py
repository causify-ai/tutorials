from __future__ import annotations
from pathlib import Path
import nbformat

def main():
    Path("notebooks").mkdir(exist_ok=True)
    nb = nbformat.v4.new_notebook()
    nb.cells = [
        nbformat.v4.new_markdown_cell("# Writes files"),
        nbformat.v4.new_code_cell(
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n"
            "import pandas as pd\n"
            "\n"
            "df = pd.DataFrame({'x': np.arange(5), 'y': np.arange(5)**2})\n"
            "df.to_csv('table.csv', index=False)\n"
            "\n"
            "plt.plot(df['x'], df['y'])\n"
            "plt.title('y=x^2')\n"
            "plt.savefig('plot.png', dpi=120)\n"
            "print('wrote table.csv and plot.png')\n"
        ),
    ]
    nbformat.write(nb, "notebooks/writes_files.ipynb")
    print("Wrote notebooks/writes_files.ipynb")

if __name__ == "__main__":
    main()
