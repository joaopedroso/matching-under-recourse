import networkx as nx
from time import process_time
from copy import deepcopy
from greedy import greedy
from enum_matchings import adj_from_edges, to_str
import sys
from kep_io import read_prob
from cpu_solve import get_kep_edges

try:
    filename = sys.argv[1]
    N = int(sys.argv[2])
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
start = process_time()
resid = deepcopy(adj)
E,sol,ncache = greedy(adj=adj, p=p, resid=resid, N=N, cpulim=start+cpulim)
cpu = process_time() - start

print("nvert:\tnedges:\texpectation:\tCPU used:\tcache size:\tedges:")
print("{}\t{}\t".format(len(adj),len(edges)),end=""); 
print("{}\t{}\t{}\t{}".format(E,cpu,ncache,to_str(edges)))
sys.stdout.flush()
