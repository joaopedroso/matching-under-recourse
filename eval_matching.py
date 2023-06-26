import networkx as nx
from copy import deepcopy
from time import clock
from enum_matchings import edges_from_adj, adj_from_edges, all_matchings, to_str
import itertools
import random

# globals
CACHE = {}
CPULIM = 0
LOG = False

def del_edge_in_matching(res, edge):
    (orig,dest) = edge
    for i in [orig,dest]:
        for j in res[i]:
            res[j].remove(i)
        del res[i]

def del_edge_not_in_matching(res, edge):
    (orig,dest) = edge
    res[orig].remove(dest)
    res[dest].remove(orig)


class Solution:
    """hold complete (recursive) solution information"""
    level = 0
    def __init__(self, matching, expect):
        self.matching = matching    # a level's matching
        self.expect = expect        # this solution's expectation
        self.prob = {}      # dictionary, with probability counted for each binary pattern of self.matching's failure
        self.pat = {}       # dictionary, with a Solution list on each binary pattern of self.matching's failure

    def __str__(self):
        Solution.level += 1
        ind = Solution.level*"  "
        s = "{}{}{} E:{}\n".format(Solution.level, ind, to_str(self.matching), self.expect)
        for pt in sorted(self.pat.keys()):
            strpt = "".join([str(i) for i in pt])
            s += ind+" * '{}' P:{}\n".format(strpt, self.prob[pt])
            for sol in self.pat[pt]:
                s += str(sol)
        Solution.level -= 1
        return s

    def pattern(self, pat, prob, sol):
        self.prob[pat] = prob
        self.pat[pat] = sol

# sol = Solution({frozenset({1,2}),frozenset({3,4})}, 2.5)
# sol.pattern("00", 0.3, [Solution({frozenset({2,3}),frozenset({1,4})},1.3)])
# sol.pattern("01", 0.1, [Solution(set(),0)])
# sol.pattern("10", 0.2, [Solution(set(),0)])
# sol.pattern("11", 0.7, [Solution(set(),0)])
# print(sol)
# exit(0)


def eval_matching(adj, p, matching, resid, N):
    # adj: the original graph, as an adjacency dictionary
    # matching: matching being evaluated
    # resid: residual graph (initially, identical to adj) [*: modified]
    # N: number of observations allowed
    key = N, frozenset(matching), frozenset(edges_from_adj(resid))
    if key in CACHE:
        return CACHE[key]
    sol = Solution(matching.copy(), 0)
    matching = list(matching)
    # get all the possible combinations of edge failure
    for seq in itertools.product([0,1], repeat=len(matching)):  # seq is 00...0, 00...1, ..., 11...1
        resid_seq = deepcopy(resid)
        ON = 0
        prod = 1
        for k in range(len(seq)):
            edge = matching[k]
            if seq[k] == 1:  # ON
                ON += 1
                prod *= (1-p[edge])
                del_edge_in_matching(resid_seq,edge)
            else:  # OFF
                prod *= p[edge]
                del_edge_not_in_matching(resid_seq,edge)
        if len(resid_seq) > 0 and N>0:
            val_resid,sol_resid = __solve(adj=adj, p=p, resid=resid_seq, N=N-1)
        else:
            val_resid,sol_resid = 0,[Solution(set(),0)]
        sol.pattern(seq,prod,sol_resid)
        sol.expect += prod * (2*ON + val_resid)

    CACHE[key] = sol
    return sol


def __solve(adj, p, resid, N):
    # adj: the original graph, as an adjacency dictionary [not modified]
    # * resid: residual graph (initially, identical to adj)  [*: modified]
    # * N: number of observations allowed
    # chache: dictionary with previouly computed matchings

    global CPULIM

    if clock() > CPULIM:
        raise TimeoutError

    G = nx.from_dict_of_lists(resid)
    components = list(nx.connected_components(G))

    if LOG: print(ind+"edges:", to_str(edges_from_adj(resid)), "N=", N)
    if LOG: print(ind+"connected components", [c for c in components])
    total_val = 0
    total_sol = []
    for c in components:
        if len(c) == 1:
            continue

        sG = nx.subgraph(G, c)
        edges_0 = sG.edges()
        if len(edges_0) == 0:
            continue
        adj_0 = nx.to_dict_of_lists(sG,c)

        max_val = -1
        for mi in all_matchings(adj=adj, edges=edges_0, matchings=[], match=set()):
            if LOG: print(ind+"matching:", to_str(mi))
            if clock() > CPULIM:
                raise TimeoutError
            m_matching = mi.copy()
            m_resid = deepcopy(adj_0)
            m_sol = eval_matching(adj, p, m_matching, m_resid, N)
            if m_sol.expect > max_val:
                max_val = m_sol.expect
                solution = deepcopy(m_sol)
            if LOG: print(ind+"matching:", to_str(mi), "expectation", m_sol.expect)
        if max_val > 0:
            total_val += max_val
            total_sol.append(solution)

    return total_val, total_sol


def solve(adj, p, resid, N, cpulim, init=True):
    # adj: the original graph, as an adjacency dictionary [not modified]
    # * resid: residual graph (initially, identical to adj)  [*: modified]
    # * N: number of observations allowed
    # chache: dictionary with previouly computed matchings

    global CACHE
    global CPULIM
    CACHE.clear()
    CPULIM = cpulim

    try:
        E,sol = __solve(adj, p, resid, N)
    except TimeoutError:
        E,sol = None,None

    return E,sol,len(CACHE)


if __name__ == "__main__":
    # adj = {1:{2,4}, 2:{1,3}, 3:{2,4}, 4:{1,3}}   # C4
    adj = {1:{2,3,4}, 2:{1,3,4}, 3:{1,2,4}, 4:{1,2,3}}   #K4
    edges = edges_from_adj(adj)
    p = {}
    P = 0.5
    N = 100
    for (i,j) in edges:
        p[frozenset({i,j})] = P

    print("sample usage:")
    resid = deepcopy(adj)
    E,sol,ncache = solve(adj=adj, p=p, resid=resid, N=N, cpulim=5)
    print("expectation:", E)
    print("cache size:", ncache)
    print("solution:")
    for s in sol:
        print(s)
