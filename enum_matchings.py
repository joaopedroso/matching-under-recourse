from copy import deepcopy


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
    """
    Find the greedy matching in graph defined by 'adj', as proposed by Chen XXXX
    Parameters:
        * adj: the original graph, as an adjacency dictionary [not modified]
        * p: probability of failure
        * edges: remaining edges in the graph (initially, all its edges)
        * match: currently being enumerated

    Yields:
        matchings as they are found
    """
    print(f"<<<match: {match}, edges: {edges}")
    if len(edges) > 0:
        edge = frozenset(edges.pop())

        # add edge to the matching
        match.add(edge)
        edges = set(e for e in edges if len(set(e) & edge) == 0)
    print(f"match: {match}, edges: {edges}>>>")
    yield match


def greedy_matchingS(adj, p, edges, match):
    """
    Find the greedy matching in graph defined by 'adj', as proposed by Chen XXXX  [unused]
    Parameters:
        * adj: the original graph, as an adjacency dictionary [not modified]
        * p: probability of failure
        * edges: remaining edges in the graph (initially, all its edges)
        * match: currently being enumerated

    Yields:
        matchings as they are found
    """
    # print(f"match: {match}, edges: {edges}")
    if len(edges) > 0:
        assert list(edges) == list(sorted(edges, key=lambda e: -p[frozenset(e)]))
        edge = frozenset(edges.pop())

        # add edge to the matching
        m_add = match.copy()
        m_add.add(edge)
        e_add = set(e for e in edges if len(set(e) & edge) == 0)
        if len(e_add) == 0:   # only maximal matchings considered
            # print(f"yielding match: {m_add}, edges: {e_add}")
            yield m_add

        if len(e_add) > 0:
            for m in greedy_matching(adj, p, e_add, m_add):
                yield m

        # do NOT add (i,j) to the matching
        if len(edges) > 0:
            for m in greedy_matching(adj, p, edges, match):
                yield m


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
