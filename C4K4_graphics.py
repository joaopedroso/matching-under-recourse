"""Generate expectation data for cycle C_V and complete graph K_V.

Sweeps over N = 0 … V (number of observation rounds) with a fixed edge
failure probability and prints a tab-separated table of expected matched
edges, suitable for plotting Figure 3 of the paper.

Usage::

    python C4K4_graphics.py
"""

from copy import deepcopy
from solve import solve
from enum_matchings import edges_from_adj

prob = 0.8
V = 6   # number of vertices

print(f"PLOT: recourse with varying depth on C{V}, K{V}, p={prob}")
print(f"# N\tC{V}\tK{V}")
for N in range(V + 1):   # number of observation rounds
    print(f"{N}", end="\t")

    adj = {i: ((i-1)%V, (i+1)%V) for i in range(V)}  # C_V
    edges = edges_from_adj(adj)
    p = {frozenset({i, j}): prob for (i, j) in edges}
    resid = deepcopy(adj)
    E, sol, ncache = solve(adj=adj, p=p, resid=resid, N=N, cpulim=float("inf"))
    print(f"{E / 2}", end="\t")

    adj = {i: (set(range(V)) - {i}) for i in range(V)}  # K_V
    edges = edges_from_adj(adj)
    p = {frozenset({i, j}): prob for (i, j) in edges}
    resid = deepcopy(adj)
    E, sol, ncache = solve(adj=adj, p=p, resid=resid, N=N, cpulim=float("inf"))
    print(f"{E / 2}")
