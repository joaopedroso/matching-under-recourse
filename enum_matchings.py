from copy import deepcopy


def all_matchings(adj, edges, matchings, match):
    """
    Find all matchings in graph defined by 'adj'
    Parameters:
        adj: the original graph, as an adjacency dictionary [not modified]
        * edges: remaining edges in the graph (initially, all its edges)
        * matchings: current list of matchings found (initially empty)
        * match: currently being enumerated

    Returns:
        machings: list of matchings
    """
    if len(edges) > 0:
        edge = frozenset(edges.pop())

        # add edge to the matching
        m_add = match.copy()
        m_add.add(edge)
        e_add = set(e for e in edges if len(set(e) & edge) == 0)
        # if r_add.may_be_maximal():
        yield m_add.copy()
        # print("*** added matching", to_str(m_add), "/", len(matchings))
        if len(e_add) > 0:
            for m in all_matchings(adj, e_add, matchings, m_add):
                yield m

        # do NOT add (i,j) to the matching
        if len(edges) > 0:
            for m in all_matchings(adj, edges, matchings, match):
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
