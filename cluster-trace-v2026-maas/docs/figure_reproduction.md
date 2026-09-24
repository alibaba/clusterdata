# Reproducing Figures

Download and extract the data following [data_download.md](data_download.md).
Run the commands below from `cluster-trace-v2026-maas/` with Python 3.10 or later.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/run_all.py
```

To reproduce an individual figure or the tables:

```sh
.venv/bin/python scripts/plot_fig5.py
.venv/bin/python scripts/reproduce_tables.py
```

Tables are saved in `output/tables/`; figure panels are saved as separate PDFs
in `output/figures/figNN/`.

## Figures and scripts

| Result | Script | Content |
| --- | --- | --- |
| Tables 2–4 | `scripts/reproduce_tables.py` | Workload, PD-mode, and architecture summaries |
| Fig. 2 | `scripts/plot_fig2.py` | Cluster GPU-Time curve |
| Fig. 3 | `scripts/plot_fig3.py` | GPU-type GPU Time and online share |
| Fig. 4 | `scripts/plot_fig4.py` | SM utilization by GPU type and cluster |
| Fig. 5 | `scripts/plot_fig5.py` | Weekly and six-month resource dynamics |
| Fig. 6 | `scripts/plot_fig6.py` | Application GPU Time and daily instance counts |
| Fig. 7 | `scripts/plot_fig7.py` | Daily application placement footprint |
| Fig. 8 | `scripts/plot_fig8.py` | Two application cases |
| Fig. 9 | `scripts/plot_fig9.py` | GPU memory, KV cache, and SM utilization |
| Fig. 10 | `scripts/plot_fig10.py` | PD KV cache and transfer latency |
| Fig. 11(c,d) | `scripts/plot_fig11.py` | Model size and SM utilization |
| Fig. 12 | `scripts/plot_fig12.py` | Model variants and GPU-Time concentration |
| Fig. 13 | `scripts/plot_fig13.py` | Hot/cold instance lifetimes and model sizes |
| Fig. 14 | `scripts/plot_fig14.py` | Hot/cold resource activity |
| Fig. 15(a) | `scripts/plot_fig15.py` | Model size by PD mode |
| Fig. 16 | `scripts/plot_fig16.py` | PD resource profiles |
| Fig. 17(a,c,d) | `scripts/plot_fig17.py` | Dense/MoE resource profiles |
| Fig. 18 | `scripts/plot_fig18.py` | Top-model deployment coverage |

Fig. 5 uses both instance tables; Fig. 8–10 use the application-case files.
Other figures and Tables 2–4 use the daily table.

## Reproduction scope

- Fig. 2's bars require unreleased cluster machine-inventory data.
- Fig. 11(a,b), Fig. 15(b), and Fig. 17(b) require unreleased GPU hardware specifications.
