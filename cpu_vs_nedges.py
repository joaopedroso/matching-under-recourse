import networkx as nx
from time import process_time
from copy import deepcopy
import sys
from configurations import generate_graphs
from solve import solve

try:
    maxsz = int(sys.argv[1])
    cpulim = float(sys.argv[2])
except:
    print("usage: {} maxsize cpulim".format(sys.argv[0]))
    exit(-1)

for (i,G) in enumerate(generate_graphs(maxsz)):
    # print("{}\t{}\t{}\t{}\t".format(i+1,len(G),len(G.edges()),G.edges()), end="")
    print("{}\t{}\t{}\t".format(i+1,len(G),len(G.edges())),end="")
    adj = nx.to_dict_of_lists(G)
    edges = G.edges()
    P = 0 # no failure
    p = {}
    for (i,j) in edges:
        p[frozenset({i,j})] = P
    resid = deepcopy(adj)
    start = process_time()
    E,sol,ncache = solve(adj=adj, p=p, resid=resid, N=len(edges), cpulim=start+cpulim)
    # E,sol,ncache = -1,-1,-1
    cpu = process_time() - start
    print("expectation:\t{}\tCPU used:\t{}\tcache size:{}".format(E,cpu,ncache))
    sys.stdout.flush()

    # required, otherwise garbage collecting time will appear on the next call...
    del E
    del sol
    del ncache
    from solve import CACHE
    CACHE.clear()
