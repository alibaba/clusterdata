from pathlib import Path
import subprocess
import sys


if __name__ == "__main__":
    scripts = Path(__file__).resolve().parent
    names = ["reproduce_tables.py", *[f"plot_fig{n}.py" for n in range(2, 19)]]
    for name in names:
        subprocess.run([sys.executable, str(scripts / name)], check=True)
