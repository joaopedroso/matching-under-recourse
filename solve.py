"""Exact solver for maximum-expectation matching under recourse (Algorithm 4).

Problem
-------
Given an undirected compatibility graph whose edges may each fail
independently with a known probability, compute the matching strategy that
maximises the expected number of successfully matched pairs after at most N
rounds of observation and re-matching (the *limited recourse* model,
Section 4 of the paper).

Algorithm
---------
The solver works recursively on the residual graph (the subgraph of edges
that have not yet been matched and observed):

1. Decompose the residual graph into connected components; handle each
   component independently.
2. For each component, enumerate every candidate matching M using
   ``enum_matchings.all_matchings`` (Algorithm 3).
3. For each M, iterate over all 2^|M| failure patterns (bit-vector seq,
   where 0 = failed, 1 = survived):

   - Accumulate probability weight prod(p_e^(1−seq_e) · (1−p_e)^seq_e).
   - Let ON = number of surviving edges.
   - Build the residual graph after observing the pattern (remove matched
     edges that survived and matched edges that failed; keep unmatched
     edges untouched).
   - If N > 0 and the residual is non-empty, recurse with N−1.
   - Expected contribution: prod × (2·ON + E_residual).

4. Select the M that maximises the total expected value.
5. Cache results keyed by (N, frozenset(matching), frozenset(residual
   edges)) to avoid recomputing identical sub-problems.

The expected value counts *vertices* (not edges): a successfully matched
edge {i, j} contributes 2 because both donor-patient pairs are served.

Reference
---------
Pedroso & Ikeda, "Maximum-expectation matching under recourse",
European Journal of Operational Research, 2025.
"""
import networkx as nx
from copy import deepcopy
from time import process_time
from enum_matchings import edges_from_adj, adj_from_edges, all_matchings, to_str
import itertools
import random

# globals
CACHE = {}
CPULIM = 0
LOG = False
ind = ""

def del_edge_in_matching(res, edge):
    """Remove a matched edge that *survived*: delete both endpoints from the residual graph.

    When edge {i, j} is in the matching and both vertices are successfully
    transplanted, neither i nor j can participate in future rounds.  All
    adjacency entries referencing i or j are removed.

    Parameters
    ----------
    res : dict
        Residual adjacency dict, modified in place.
    edge : frozenset
        The surviving matched edge {i, j}.
    """
    (orig,dest) = edge
    for i in [orig,dest]:
        for j in res[i]:
            res[j].remove(i)
        del res[i]

def del_edge_not_in_matching(res, edge):
    """Remove a matched edge that *failed*: delete only the arc between endpoints.

    When edge {i, j} is in the matching but fails, the vertices i and j
    remain in the graph (they may still be matched to other partners in a
    future round), but the arc between them is removed so it is not
    offered again.

    Parameters
    ----------
    res : dict
        Residual adjacency dict, modified in place.
    edge : frozenset
        The failed matched edge {i, j}.
    """
    (orig,dest) = edge
    res[orig].remove(dest)
    res[dest].remove(orig)


class Solution:
    """Complete (recursive) solution at one node of the decision tree.

    Attributes
    ----------
    matching : set of frozenset
        The matching chosen at this level.
    expect : float
        Expected number of matched vertices rooted at this node
        (includes contributions from all sub-trees).
    prob : dict
        Maps each failure pattern (tuple of 0/1) to its probability.
    pat : dict
        Maps each failure pattern to the list of Solution objects for the
        subsequent round (one per connected component of the residual).
    """
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
    """Evaluate the expected value of a given matching under the recourse model.

    Iterates over all 2^|matching| failure patterns, computes the probability
    and immediate reward (surviving edges) of each, then recurses on the
    residual graph with N−1 rounds remaining.  Results are memoised by
    (N, matching, residual edges).

    Parameters
    ----------
    adj : dict
        Original full graph (adjacency dict); passed through to recursive calls.
    p : dict
        Edge failure probabilities: p[frozenset({i,j})] = probability that
        edge {i,j} fails.
    matching : set of frozenset
        Candidate matching to evaluate.
    resid : dict
        Residual graph at the current round (modified in place during
        enumeration; a deep copy is made per failure pattern).
    N : int or float
        Remaining observation rounds.  float('inf') means unlimited recourse.

    Returns
    -------
    Solution
        A Solution object carrying the expected value and the full decision
        tree rooted at this matching.
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
            val_resid,sol_resid = __solve(adj=adj, p=p, resid=resid_seq, N=N-1)
        else:
            val_resid,sol_resid = 0,[Solution(set(),0)]
        sol.pattern(seq,prod,sol_resid)
        sol.expect += prod * (2*ON + val_resid)

    CACHE[key] = sol
    return sol


def __solve(adj, p, resid, N):
    """Recursively find the optimal matching strategy for the residual graph.

    Decomposes the residual into connected components, then for each component
    enumerates all candidate matchings and selects the one with maximum
    expected value (via eval_matching).  Components with a single vertex or
    no edges are skipped.

    Parameters
    ----------
    adj : dict
        Original full graph (not modified).
    p : dict
        Edge failure probabilities.
    resid : dict
        Current residual graph (modified by eval_matching sub-calls).
    N : int or float
        Remaining observation rounds.

    Returns
    -------
    total_val : float
        Sum of best expected values across all components.
    total_sol : list of Solution
        One Solution per component (empty if no matchings exist).

    Raises
    ------
    TimeoutError
        If the CPU time limit (CPULIM) is exceeded.
    """

    global CPULIM, ind

    if LOG: ind += "  "

    if process_time() > CPULIM:
        raise TimeoutError

    G = nx.from_dict_of_lists(resid)
    components = list(nx.connected_components(G))

    if LOG: print(ind+"edges:", to_str(edges_from_adj(resid)), "N=", N)
    if LOG: print(ind+"connected components", [c for c in components])
    total_val = 0
    total_sol = []
    for c in components:
        if len(c) == 1:   # only one edge in this component
            continue

        sG = nx.subgraph(G, c)
        edges_0 = list(sG.edges())
        if len(edges_0) == 0:
            continue
        adj_0 = nx.to_dict_of_lists(sG,c)

        max_val = -1
        for mi in all_matchings(adj=adj, edges=edges_0, match=set()):
            if LOG: print(ind+"matching:...", to_str(mi))
            if process_time() > CPULIM:
                raise TimeoutError
            m_matching = mi.copy()
            m_resid = deepcopy(adj_0)
            m_sol = eval_matching(adj, p, m_matching, m_resid, N)
            if m_sol.expect > max_val:
                max_val = m_sol.expect
                solution = deepcopy(m_sol)
            if LOG: print(ind+"...matching:", to_str(mi), "expectation", m_sol.expect)
        if max_val > 0:
            total_val += max_val
            total_sol.append(solution)

    if LOG: ind = ind[:-2]
    return total_val, total_sol


def solve(adj, p, resid, N, cpulim, init=True):
    """Compute the maximum-expectation matching strategy (public entry point).

    Clears the memoisation cache, sets the CPU limit, then calls the
    internal solver.  Returns (None, None, cache_size) if the time limit
    is exceeded before a solution is found.

    Parameters
    ----------
    adj : dict
        Original compatibility graph as an adjacency dict
        {vertex: set_of_neighbours}.
    p : dict
        Edge failure probabilities: p[frozenset({i,j})] in [0, 1].
    resid : dict
        Initial residual graph; pass deepcopy(adj) for a fresh solve.
    N : int or float
        Maximum number of observation/re-matching rounds.
        Use float('inf') for unlimited recourse.
    cpulim : float
        Absolute CPU time limit in seconds (time.process_time() scale).
        Pass start + budget, where start = process_time() at call time.
    init : bool
        Unused; kept for API compatibility.

    Returns
    -------
    E : float or None
        Expected number of matched vertices, or None on timeout.
    sol : list of Solution or None
        Solution tree (one Solution per top-level component), or None.
    ncache : int
        Number of entries in the memoisation cache at termination.
    """

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
    N = 1   # number of observations allowed
    # adj = {1:{2,4}, 2:{1,3}, 3:{2,4}, 4:{1,3}}   # C4
    # adj = {1:{2,3,4}, 2:{1,3}, 3:{1,2}, 4:{1}}   # K4
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
    p = {frozenset({1, 2}): 0.01,   # probabilities of edge failure
         frozenset({1, 4}): 0.02,
         frozenset({2, 3}): 0.03,
         frozenset({3, 4}): 0.99,
         }
    N = 0
    adj = {2:{9}, 3:{8}, 6:{8}, 8:{3,6}, 9:{2}}
    edges = edges_from_adj(adj)
    p = {frozenset({2, 9}): 0.9973280978579215,   # probabilities of edge failure
         frozenset({3, 8}): 0.9922058829960843,
         frozenset({6, 8}): 0.9902156637534143,
         }

    print("sample usage:")
    resid = deepcopy(adj)
    E,sol,ncache = solve(adj=adj, p=p, resid=resid, N=N, cpulim=float("inf"))
    print("expectation:", E)
    print("cache size:", ncache)
    print("solution:")
    for s in sol:
        print(s)
