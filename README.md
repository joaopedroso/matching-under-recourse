# Maximum-expectation matching under recourse — code

Reference implementation for:

> João Pedro Pedroso & Shiro Ikeda.  
> **Maximum-expectation matching under recourse.**  
> *European Journal of Operational Research*, 2025.  
> https://doi.org/10.1016/j.ejor.2025.01.022

## Problem summary

In a Kidney Exchange Program (KEP), donor-patient pairs are modelled as
vertices and compatibility as directed arcs.  A 2-cycle {i, j} (arcs i→j and
j→i) represents a mutual exchange.  Vertices and arcs each fail independently
with known probabilities.  The goal is to find a matching strategy that
maximises the **expected** number of successfully transplanted pairs, allowing
up to N rounds of observation and re-matching (*limited recourse*).

## Repository structure

| File | Role |
|---|---|
| `solve.py` | Exact solver — Algorithm 4 (recursive enumeration + memoisation) |
| `greedy_k.py` | Greedy-k heuristic — Algorithm 2 (max-weight matching) |
| `enum_matchings.py` | Matching enumeration primitives (Algorithms 2–3) |
| `kep_io.py` | Read/write KEP instances and failure probabilities |
| `configurations.py` | Enumerate non-isomorphic graphs (benchmark set) |
| `cpu_solve.py` | CLI driver for the exact solver |
| `cpu_greedy_k.py` | CLI driver for greedy-k |
| `cpu_vs_nedges.py` | Benchmark exact solver on small non-isomorphic graphs |
| `delorme2kep.py` | Convert Blom et al. instances to KEP format |
| `plot.py` | Visualise a KEP graph and matching |
| `C4K4_graphics.py` | Example: expectation on C_V and K_V |
| `mk_plot_kep_expect.py` | Generate Figure 5 and Tables 2–3 |
| `mk_plot_kep_cpu.py` | Generate Figure 6 and Table 1 |
| `mk_plot_configurations.py` | Generate Figure 4 |
| `mk_plot_delorme_greedy-k_vs_exact.py` | Generate Table 4 |
| `mk_plot_kep.py` | Exploratory CPU plot (single solver) |
| `process_results.sh` | Assemble per-instance output files into a summary CSV |
| `RESULTS/` | Output directory for new experiment runs |
| `RESULTS_EJOR/` | Pre-computed results from the paper (not in git; download separately) |

## Requirements

**For running experiments** (performance-critical):

- [PyPy 3.10](https://www.pypy.org/) — the shell scripts invoke `pypy3.10`.
  CPython works for small experiments but is ~30–100× slower.
- [NetworkX](https://networkx.org/) — required by all solvers.

**For plotting** (CPython is fine):

- [NumPy](https://numpy.org/)
- [Matplotlib](https://matplotlib.org/)

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Benchmark instances

Klimentova et al. instances (10–50 vertices, 50 replicates each):  
https://www.dcc.fc.up.pt/~jpp/code/KEP/

Place the instance files in `DATA/small/` (the shell scripts expect this path).

Blom et al. (Delorme) instances (50 and 100 vertices):  
Available from the authors of the paper cited in `delorme2kep.py`.
Convert them first:

```bash
bash delorme2kep.sh
```

Place converted files in `DATA/DelormeInstances/`.

## Reproducing paper results

Pre-computed result files for the paper are in `RESULTS_EJOR/` (not tracked
in git; see the paper's supplementary material or contact the authors).
The plotting scripts read from `RESULTS_EJOR/` by default.

To reproduce from scratch, run the experiment scripts and process the output:

### Table 1 + Figures 5–6 (Klimentova instances, exact solver)

```bash
bash run_cpu_solve.sh
TYPE=solve RESULTS=RESULTS/solve-<interpreter>-<date>-<host> \
    bash process_results.sh > RESULTS_EJOR/2025-01-13/summary_solve_khm.csv
python mk_plot_kep_cpu.py     # Figure 6, Table 1 (stdout)
python mk_plot_kep_expect.py  # Figure 5, Tables 2–3 (stdout)
```

### Tables 2–3 + Figures 5–6 (Klimentova instances, greedy-k)

```bash
bash run_cpu_greedy_k.sh
TYPE=greedy-k RESULTS=RESULTS/greedy-k-<interpreter>-<date>-<host> \
    bash process_results.sh > RESULTS_EJOR/2025-01-13/summary_greedy-k_khm.csv
python mk_plot_kep_cpu.py
python mk_plot_kep_expect.py
```

### Table 4 (Delorme instances)

```bash
bash run_cpu_greedy_k_delorme.sh   # greedy-k (1 h/instance limit)
bash run_cpu_solve_delorme.sh      # exact solver (10 h/instance limit)
python mk_plot_delorme_greedy-k_vs_exact.py
```

### Figure 4 (CPU vs graph structure, small non-isomorphic graphs)

```bash
bash run_configurations.sh
python mk_plot_configurations.py <output_csv> cpu_graphs.pdf
```

## Running a single instance

```bash
# Exact solver, N=2 observation rounds, 3600 s limit:
python cpu_solve.py DATA/small/10_01.input.gz 2 3600

# Greedy-k, unlimited recourse:
python cpu_greedy_k.py DATA/small/10_01.input.gz inf 3600
```

Output format (tab-separated):

```
nvert   nedges  expectation  CPU_used  cache_size  edges
```

A timeout yields `None` for expectation and cache_size.

## Failure probability model

Each undirected edge {i, j} (2-cycle) has combined failure probability:

```
p_edge = 1 − (1−p_i)(1−p_j)(1−p_{i,j})(1−p_{j,i})
```

where p_i, p_j are vertex failure probabilities and p_{i,j}, p_{j,i} are arc
failure probabilities, stored in a `.prob` file alongside each `.input` file.

## Notes on N encoding

The shell scripts and Python drivers use N directly as in the paper:
N = 1, 2, 3, 4, inf (unlimited recourse).  The pre-computed result files in
`RESULTS_EJOR/` were produced with an older internal encoding
(N = 0, 1, 2, 3, 999999 corresponding to paper N = 1, 2, 3, 4, ∞) and are
therefore **not** directly compatible with the current plotting scripts.
To regenerate the summary CSVs in the new encoding, re-run the experiment
scripts and process with `process_results.sh`.
