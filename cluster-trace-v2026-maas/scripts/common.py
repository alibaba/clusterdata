import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache"
CACHE.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(CACHE / "matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(CACHE))

import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SOURCE = """
SELECT *, gpu_hours AS hours,
       CASE WHEN left(model_id, 2) IN ('b_', 'x_')
            THEN 'base:' || base_id ELSE 'model:' || model_id END AS model_key
FROM daily WHERE workload IN ('online', 'offline')
"""


def connect():
    con = duckdb.connect(config={"memory_limit": "4GB", "threads": 1,
                                 "temp_directory": str(CACHE / "spill")})
    con.execute("SET preserve_insertion_order=false")
    for view, folder in [("daily", "instance_daily"), ("week", "instance_week_5min")]:
        path = str(ROOT / "data" / folder / "*.parquet").replace("'", "''")
        con.execute(f"CREATE VIEW {view} AS SELECT * FROM read_parquet('{path}')")
    con.execute(f"CREATE VIEW src AS {SOURCE}")
    return con


def query(name, sql, setup="", datasets=("instance_daily",)):
    files = [p for dataset in datasets for p in sorted((ROOT / "data" / dataset).glob("*.parquet"))]
    stamp = [(str(p.relative_to(ROOT)), p.stat().st_size, p.stat().st_mtime_ns) for p in files]
    key = hashlib.sha256(json.dumps([stamp, SOURCE, sql, setup]).encode()).hexdigest()
    cache = CACHE / f"{name}.json"
    if cache.exists():
        cached = json.loads(cache.read_text())
        if cached["key"] == key:
            return cached["rows"]
    with connect() as con:
        if setup:
            con.execute(setup)
        rows = con.execute(sql).fetchall()
    temporary = cache.with_suffix(".tmp")
    temporary.write_text(json.dumps({"key": key, "rows": rows}))
    temporary.replace(cache)
    return rows


def save(fig, name=None):
    name = name or fig.get_label()
    folder = ROOT / "output/figures" / name[:5]
    folder.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(folder / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)
