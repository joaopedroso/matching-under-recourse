"""Graph matching primitives used by the exact solver and greedy-k heuristic.

This module provides three matching strategies and graph conversion utilities:

all_matchings
    Enumerate *all* matchings of a graph by recursive backtracking
    (Algorithm 3 of the paper).  Used by the exact solver (solve.py) to
    explore every possible first-round choice.

greedy_matching
    Return the single greedy matching: pop edges in order of decreasing
    failure probability (most reliable first) and greedily include each
    edge if it does not conflict with already-selected edges.

greedy_k_matching
    Return the single maximum-weight matching computed by NetworkX
    ``max_weight_matching`` with weights = 1 − p_edge (survival
    probability).  Used by the greedy-k heuristic (greedy_k.py).

All three functions yield matching(s) as sets of frozensets {i, j}.
"""
import networkx as nx


def all_matchings(adj, edges, match):
    """
    Find all matchings in graph defined by 'adj'
    Parameters:
        adj: the original graph, as an adjacency dictionary [not modified]
        * edges: remaining edges in the graph (initially, all its edges)
        * match: currently being enumerated

    Yields:
        matchings as they are found
    """
    if len(edges) > 0:
        edge = frozenset(edges.pop())

        # add edge to the matching
        m_add = match.copy()
        m_add.add(edge)
        e_add = set(e for e in edges if len(set(e) & edge) == 0)
        yield m_add.copy()
        if len(e_add) > 0:
            for m in all_matchings(adj, e_add, m_add):
                yield m

        # do NOT add (i,j) to the matching
        if len(edges) > 0:
            for m in all_matchings(adj, edges, match):
                yield m


def greedy_matching(adj, p, edges, match):
    """Find the single greedy matching: select the most reliable edge first.

    Pops edges in order of *decreasing* failure probability (the last element
    of the sorted list has the highest failure probability, so popping gives
    the most reliable edge), then greedily adds it to the matching and removes
    all conflicting edges.  Yields exactly one matching.

    Parameters
    ----------
    adj : dict
        Original graph (not used directly; present for API consistency).
    p : dict
        Edge failure probabilities: p[frozenset({i,j})] in [0, 1].
    edges : list
        Remaining candidate edges, sorted so that edges.pop() returns the
        edge with the *lowest* failure probability (most reliable).
    match : set
        Edges already selected (initially empty).

    Yields
    ------
    set of frozenset
        The single greedy matching.
    """
    if len(edges) > 0:
        edge = frozenset(edges.pop())

        # add edge to the matching
        match.add(edge)
        edges = set(e for e in edges if len(set(e) & edge) == 0)
    yield match


def greedy_k_matching(adj, p, edges):
    """Find the maximum-weight matching with weights equal to survival probability.

    Builds a weighted graph where each edge {i,j} has weight 1 − p[{i,j}]
    (probability of survival), then calls NetworkX ``max_weight_matching``
    to find the matching that maximises total expected survival weight.
    Yields exactly one matching.

    This is the core selection step of Algorithm 2 (greedy-k) in the paper.

    Parameters
    ----------
    adj : dict
        Original graph (not used directly; present for API consistency).
    p : dict
        Edge failure probabilities: p[frozenset({i,j})] in [0, 1].
    edges : list of (int, int)
        All edges of the current residual graph.

    Yields
    ------
    set of frozenset
        The single maximum-weight matching.
    """
    # print(f"<<<edges: {edges}")
    if len(edges) > 0:
        G = nx.Graph()
        w_edges = [(i, j, 1-p[frozenset({i,j})]) for (i,j) in edges]   # 1-p -> probability of succeeding (2025-01-10
        G.add_weighted_edges_from(w_edges)
        # # Print edge weights
        # for u, v, data in G.edges(data=True):
        #     print(f"Edge ({u}, {v}) has weight {data['weight']}")
        # print(f"match: {list(nx.max_weight_matching(G))}, edges: {edges}>>>")
        yield set(frozenset(e) for e in nx.max_weight_matching(G))



def edges_from_adj(adj):
    edges = set()
    for i in adj:
        for j in adj[i]:
            edges.add(frozenset((i,j)))
            assert i in adj[j]
    return edges


def adj_from_edges(edges):
    adj = {}
    for (i,j) in edges:
        if i in adj:
            adj[i].add(j)
        else:
            adj[i] = set([j])
        if j in adj:
            adj[j].add(i)
        else:
            adj[j] = set([i])
    return adj


def to_str(edges):
    s = "{ "
    for (orig,dest) in edges:
        s += "{}-{} ".format(orig,dest)
    s += "}"
    return s


if __name__ == "__main__":
    print("sample usage")
    adj = {1:set([2,3,4,5]), 2:set([1,3]), 3:set([1,2]), 4:set([1]), 5:set([1])}
    edges = edges_from_adj(adj)
    print("adj", adj)
    print("edges", edges)

    # import networkx as nx
    # from plot import plot_matching
    # G = nx.Graph()
    # G.add_edges_from(edges)
    # m = nx.maximal_matching(G)
    # plot_matching(G,m)

    print("edge set:", [(i,j) for (i,j) in edges])
    m_all = [m for m in all_matchings(adj=adj, edges=edges, matchings=[], match=set())]
    sols = sorted([sorted([(i,j) for (i,j) in m]) for m in m_all])
    for m in sols:
        print(to_str(m))
        # plot_matching(G,m)
    print("matchings found:", len(m_all))
