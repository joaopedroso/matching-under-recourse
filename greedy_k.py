"""Greedy-k heuristic for maximum-expectation matching under recourse (Algorithm 2).

At each observation round the algorithm selects a single matching using
NetworkX ``max_weight_matching`` with edge weights equal to the probability
of survival (1 − p_edge).  This is faster than enumerating all matchings
(as the exact solver does) while still producing high-quality solutions.

Unlike the exact solver, the greedy-k algorithm considers the full residual
graph at each round rather than processing connected components independently,
because a maximum-weight matching may span multiple components and must be
chosen globally.

The evaluation of expected value for the chosen matching is identical to the
exact solver (eval_greedy_k mirrors eval_matching from solve.py), including
memoisation by (N, matching, residual edges).

Reference
---------
Pedroso & Ikeda, "Maximum-expectation matching under recourse",
European Journal of Operational Research, 2025.
"""
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
    """Evaluate the expected value of a greedy-k matching (mirrors eval_matching in solve.py).

    Parameters
    ----------
    adj : dict
        Original full graph (adjacency dict); passed to recursive calls.
    p : dict
        Edge failure probabilities: p[frozenset({i,j})] in [0, 1].
    matching : set of frozenset
        Matching chosen by greedy_k_matching to evaluate.
    resid : dict
        Residual graph at the current round.
    N : int or float
        Remaining observation rounds.

    Returns
    -------
    Solution
        Solution object with expected value and decision-tree structure.
    """
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
    """Select and evaluate the greedy-k matching for the current residual graph.

    Calls greedy_k_matching on the *full* residual graph (not per component),
    then evaluates the expected value of the resulting matching via
    eval_greedy_k.

    Parameters
    ----------
    adj : dict
        Original full graph (not modified).
    p : dict
        Edge failure probabilities.
    resid : dict
        Current residual graph.
    N : int or float
        Remaining observation rounds.

    Returns
    -------
    total_val : float
    total_sol : list of Solution

    Raises
    ------
    TimeoutError
        If the CPU time limit (CPULIM) is exceeded.
    """

    global CPULIM
    global ind

    if process_time() > CPULIM:
        raise TimeoutError

    G = nx.from_dict_of_lists(resid)

    if LOG: print(ind+"edges:", to_str(edges_from_adj(resid)), "N=", N)
    total_val = 0
    total_sol = []
    sG = G   # use the full graph: max-weight matching may span multiple components
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
    """Compute the greedy-k matching strategy (public entry point).

    Parameters
    ----------
    adj : dict
        Compatibility graph as an adjacency dict {vertex: set_of_neighbours}.
    p : dict
        Edge failure probabilities: p[frozenset({i,j})] in [0, 1].
    resid : dict
        Initial residual graph; pass deepcopy(adj) for a fresh solve.
    N : int or float
        Maximum observation rounds.  Use float('inf') for unlimited recourse.
    cpulim : float
        Absolute CPU time limit (process_time() scale).
    init : bool
        Unused; kept for API compatibility with solve().

    Returns
    -------
    E : float or None
    sol : list of Solution or None
    ncache : int
    """

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
    adj = {1:{2,4}, 2:{1,3}, 3:{2,4}, 4:{1,3}}   # C4
    edges = edges_from_adj(adj)
    p = {frozenset({1, 2}): 0.1,   # probabilities of edge failure
         frozenset({1, 4}): 0.2,
         frozenset({2, 3}): 0.3,
         frozenset({3, 4}): 0.9,
         }

    N = 0
    adj = {2:{9}, 3:{8}, 6:{8}, 8:{3,6}, 9:{2}}
    edges = edges_from_adj(adj)
    p = {frozenset({2, 9}): 0.9973280978579215,   # probabilities of edge failure
         frozenset({3, 8}): 0.9922058829960843,
         frozenset({6, 8}): 0.9902156637534143,
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
