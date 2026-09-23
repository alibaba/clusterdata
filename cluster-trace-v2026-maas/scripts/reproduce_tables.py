from common import ROOT, connect
import csv
from pathlib import Path


def main():
    output = ROOT / "output/tables"
    output.mkdir(parents=True, exist_ok=True)
    with connect() as con:
        for number in (2, 3, 4):
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
