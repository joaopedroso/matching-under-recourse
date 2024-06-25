from copy import deepcopy
from solve import solve
from enum_matchings import edges_from_adj

# print("PLOT 1: no recourse vs C4 vs K4 ")
# print("# p\tC4N0\tK4N0\tC4Ninf\tK4Ninf")
# N = 100  # number of observations allowed
# for n in range(N + 1):
#     prob = n / N
#     print(f"{prob}", end="\t")
#
#     adj = {1: {2, 4}, 2: {1, 3}, 3: {2, 4}, 4: {1, 3}}  # C4
#     edges = edges_from_adj(adj)
#     p = {}
#     resid = deepcopy(adj)
#     for (i, j) in edges:
#         p[frozenset({i, j})] = prob
#     E, sol, ncache = solve(adj=adj, p=p, resid=resid, N=0, cpulim=float("inf"))
#     print(f"{E / 2}", end="\t")
#
#     adj = {1: {2, 3, 4}, 2: {1, 3, 4}, 3: {1, 2, 4}, 4: {1, 2, 3}}  # K4
#     edges = edges_from_adj(adj)
#     p = {}
#     resid = deepcopy(adj)
#     for (i, j) in edges:
#         p[frozenset({i, j})] = prob
#     E, sol, ncache = solve(adj=adj, p=p, resid=resid, N=0, cpulim=float("inf"))
#     print(f"{E / 2}", end="\t")
#
#     adj = {1: {2, 4}, 2: {1, 3}, 3: {2, 4}, 4: {1, 3}}  # C4
#     edges = edges_from_adj(adj)
#     p = {}
#     resid = deepcopy(adj)
#     for (i, j) in edges:
#         p[frozenset({i, j})] = prob
#     E, sol, ncache = solve(adj=adj, p=p, resid=resid, N=999999, cpulim=float("inf"))
#     print(f"{E / 2}", end="\t")
#
#     adj = {1: {2, 3, 4}, 2: {1, 3, 4}, 3: {1, 2, 4}, 4: {1, 2, 3}}  # K4
#     edges = edges_from_adj(adj)
#     p = {}
#     resid = deepcopy(adj)
#     for (i, j) in edges:
#         p[frozenset({i, j})] = prob
#     E, sol, ncache = solve(adj=adj, p=p, resid=resid, N=999999, cpulim=float("inf"))
#     print(f"{E / 2}")

prob = 0.8
V = 6   # number of vertices
adj = {i: ((i - 1) % V, (i + 1) % V) for i in range(V)}  # C-V
print(f"C{V}:\t{adj}")
adj = {i: (set(range(V)) - {i}) for i in range(V)}   # K-v
print(f"K{V}:\t{adj}")

print(f"PLOT 2: recourse with varying depth on C{V}, K{V}, p={prob}")
print(f"# N\tC{V}\tK{V}")
for N in range(V + 1):   # number of observations allowed
    print(f"{N}", end="\t")

    adj = {i: ((i-1)%V, (i+1)%V) for i in range(V)}  # C-V
    # print(adj)
    edges = edges_from_adj(adj)
    p = {}
    resid = deepcopy(adj)
    for (i, j) in edges:
        p[frozenset({i, j})] = prob
    E, sol, ncache = solve(adj=adj, p=p, resid=resid, N=N, cpulim=float("inf"))
    print(f"{E / 2}", end="\t")

    adj = {i: (set(range(V)) - {i}) for i in range(V)}   # K-v
    # print(adj)
    edges = edges_from_adj(adj)
    p = {}
    resid = deepcopy(adj)
    for (i, j) in edges:
        p[frozenset({i, j})] = prob
    E, sol, ncache = solve(adj=adj, p=p, resid=resid, N=N, cpulim=float("inf"))
    print(f"{E / 2}")

