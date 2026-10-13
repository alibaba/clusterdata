# Reproduce Tables 2-4 and the released panels of Figures 2-18 sequentially.
# Each script uses the same Python environment and writes results under output/.
# See docs/figure_reproduction.md for inputs, resource use, and panel coverage.

from pathlib import Path
import subprocess
import sys


if __name__ == "__main__":
    scripts = Path(__file__).resolve().parent
    names = ["reproduce_tables.py", *[f"plot_fig{n}.py" for n in range(2, 19)]]
    for name in names:
        subprocess.run([sys.executable, str(scripts / name)], check=True)
