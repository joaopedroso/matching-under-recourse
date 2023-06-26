import networkx as nx
from time import clock
from copy import deepcopy
from configurations import generate_graphs
from eval_matching import solve
from enum_matchings import adj_from_edges, to_str
import sys
from kep_io import read_prob

def get_kep_edges(adj,p_):
    """given a directed KEP graph, return its edges (i.e., its 2-cycles)"""
    V = adj.keys()
    p = {}
    edges = []
    for i in V:
        for j in V:
            if j <= i:
                continue
            if j in adj[i] and i in adj[j]:
                # print("edge", (i,j))
                edge = frozenset((i,j))
                edges.append(edge)
                p[edge] = p_[i]*p_[j]*p_[i,j]*p_[j,i]
    return edges,p


try:
    filename = sys.argv[1]
    N = float(sys.argv[2])
    cpulim = float(sys.argv[3])
except:
    print("usage: {} KEPinstance Nobserv CPUlim".format(sys.argv[0]))
    exit(-1)
adj_, w_, p_ = read_prob(filename)  # read directed graph
edges,p = get_kep_edges(adj_,p_)  # edges for 2-cycles
adj = adj_from_edges(edges)

# if len(edges) <= 25 or len(edges) > 30:
#     print("not solving: number of edges not in 26...30")
#     E, ncache = None, None
#     cpu = None
# else:
import json
with open("RESULTS/cpu_kep_DB.json","r") as f:
    FAILDB = json.load(f)

if filename not in FAILDB:
    start = clock()
    resid = deepcopy(adj)
    E,sol,ncache = solve(adj=adj, p=p, resid=resid, N=N, cpulim=start+cpulim)
    cpu = clock() - start
else:
    print("warning: not solving, instance in blacklist")
    E,sol,ncache = None,None,None
    cpu = cpulim

print("nvert:\tnedges:\texpectation:\tCPU used:\tcache size:\tedges:")
print("{}\t{}\t".format(len(adj),len(edges)),end=""); 
print("{}\t{}\t{}\t{}".format(E,cpu,ncache,to_str(edges)))
sys.stdout.flush()

if cpu >= cpulim:
    FAILDB[filename] = True
    with open("cpu_kep_DB.json","w") as f:
        json.dump(FAILDB, f, indent=4, sort_keys=True)
