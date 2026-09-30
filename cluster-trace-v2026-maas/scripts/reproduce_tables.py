from common import ROOT, connect, query
import csv
from pathlib import Path

INSTANCES = """
WITH instances AS (
    SELECT instance_id, bool_or(workload = 'online') AS online,
           bool_or(workload = 'offline') AS offline,
           bool_or(model_arch = 'dense' AND workload IN ('online', 'offline')) AS dense,
           bool_or(model_arch = 'moe' AND workload IN ('online', 'offline')) AS moe
    FROM daily WHERE instance_id IS NOT NULL AND {partition}
    GROUP BY instance_id
)
SELECT 2, 'online', count(*) FILTER (WHERE online) FROM instances
UNION ALL SELECT 2, 'offline', count(*) FILTER (WHERE offline) FROM instances
UNION ALL SELECT 2, 'all', count(*) FROM instances
UNION ALL SELECT 4, 'dense', count(*) FILTER (WHERE dense) FROM instances
UNION ALL SELECT 4, 'moe', count(*) FILTER (WHERE moe) FROM instances
"""


def main():
    output = ROOT / "output/tables"
    output.mkdir(parents=True, exist_ok=True)
    counts = query("table_instances", INSTANCES, partition=("instance_id", 16))
    for number in (2, 3, 4):
        with connect() as con:
            if number in (2, 4):
                con.execute(f"CREATE TEMP TABLE t{number}_instances (name VARCHAR, instances BIGINT)")
                con.executemany(f"INSERT INTO t{number}_instances VALUES (?, ?)",
                                [(name, count) for table, name, count in counts if table == number])
            sql = (Path(__file__).parent / f"sql/table{number}.sql").read_text()
            result = con.execute(sql)
            columns = [c[0] for c in result.description]
            rows = result.fetchall()
            with (output / f"table{number}.csv").open("w", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(columns)
                writer.writerows(rows)
            lines = ["| " + " | ".join(columns) + " |",
                     "| " + " | ".join(["---"] * len(columns)) + " |"]
            for row in rows:
                values = [f"{v:,.6f}" if isinstance(v, float) else f"{v:,}" if isinstance(v, int)
                          else str(v) for v in row]
                lines.append("| " + " | ".join(values) + " |")
            (output / f"table{number}.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
