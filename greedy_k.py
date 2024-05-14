# !!!!! new, 2024-04-01

import networkx as nx
from copy import deepcopy
from time import process_time
from enum_matchings import edges_from_adj, greedy_k_matching, to_str
import itertools
from solve import Solution, del_edge_in_matching, del_edge_not_in_matching

# globals
CACHE = {}
CPULIM = 0
LOG = False
ind = ""


def eval_greedy_k(adj, p, matching, resid, N):
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
            val_resid,sol_resid = __greedy_k(adj=adj, p=p, resid=resid_seq, N=N - 1)
        else:
            val_resid,sol_resid = 0,[Solution(set(),0)]
        sol.pattern(seq,prod,sol_resid)
        sol.expect += prod * (2*ON + val_resid)

    CACHE[key] = sol
    return sol


def __greedy_k(adj, p, resid, N):
    # adj: the original graph, as an adjacency dictionary [not modified]
    # * resid: residual graph (initially, identical to adj)  [*: modified]
    # * N: number of observations allowed
    # cache: dictionary with previously computed matchings

    global CPULIM
    global ind

    if process_time() > CPULIM:
        raise TimeoutError

    G = nx.from_dict_of_lists(resid)

    if LOG: print(ind+"edges:", to_str(edges_from_adj(resid)), "N=", N)
    total_val = 0
    total_sol = []
    sG = G   # !!!!! cannot consider connected components independently in the greedy_k case; so using total graph
    edges_0 = list(sG.edges())
    if len(edges_0) > 0:
        adj_0 = nx.to_dict_of_lists(sG)   #,c)

        max_val = -1
        for mi in greedy_k_matching(adj=adj, p=p, edges=edges_0):
            if LOG: print(ind+"matching:", to_str(mi))
            if process_time() > CPULIM:
                raise TimeoutError
            m_matching = mi.copy()
            m_resid = deepcopy(adj_0)
            m_sol = eval_greedy_k(adj, p, m_matching, m_resid, N)
            if m_sol.expect > max_val:
                max_val = m_sol.expect
                solution = deepcopy(m_sol)
            if LOG: print(ind+"matching:", to_str(mi), "expectation", m_sol.expect)
        if max_val > 0:
            total_val += max_val
            total_sol.append(solution)

    return total_val, total_sol


def greedy_k(adj, p, resid, N, cpulim, init=True):
    # adj: the original graph, as an adjacency dictionary [not modified]
    # * resid: residual graph (initially, identical to adj)  [*: modified]
    # * N: number of observations allowed
    # cache: dictionary with previously computed matchings

    global CACHE
    global CPULIM
    CACHE.clear()
    CPULIM = cpulim

    try:
        E,sol = __greedy_k(adj, p, resid, N)
    except TimeoutError:
        E,sol = None,None

    return E,sol,len(CACHE)


if __name__ == "__main__":
    N = 100   # number of observations allowed
    # adj = {1:{2,4}, 2:{1,3}, 3:{2,4}, 4:{1,3}}   # C4
    # adj = {1:{2,3,4}, 2:{1,3}, 3:{1,2}, 4:{1}}   #K4
    # edges = edges_from_adj(adj)
    # p = {}
    # P = 0.5
    # for (i,j) in edges:
    #     p[frozenset({i,j})] = random.random()
    # p = {frozenset({2, 3}): .1,
    #      frozenset({1, 2}): .2,
    #      frozenset({1, 3}): .3,
    #      frozenset({1, 4}): .4,
    #      }
    adj = {1:{2,4}, 2:{1,3}, 3:{2,4}, 4:{1,3}}   #
    edges = edges_from_adj(adj)
    p = {frozenset({1, 2}): 0.1,   # probabilities of edge failure
         frozenset({1, 4}): 0.2,
         frozenset({2, 3}): 0.3,
         frozenset({3, 4}): 0.9,
         }

    print(f"sample usage, graph={adj}")
    print(p)
    resid = deepcopy(adj)
    E,sol,ncache = greedy_k(adj=adj, p=p, resid=resid, N=N, cpulim=float("inf"))
    print("expectation:", E)
    print("cache size:", ncache)
    print("solution:")
    for s in sol:
        print(s)
