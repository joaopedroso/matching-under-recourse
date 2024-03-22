# file "enum_maximal_matchings.py"
# (not used anymore, see enum_matchings)


from copy import deepcopy


def may_be_maximal(resid, adj):
    """check if a residual graph may be maximal in adj
       (superseeded by more efficient version in class Residual)
        """
    isolated = [i for i in resid if len(resid[i])==0]
    if len(isolated) <= 1:
        return True
    for (_,i) in enumerate(isolated):
        for (__,j) in enumerate(isolated[_+1:]):
            if j in adj[i]:
                return False
    return True

class Residual:
    """keep information about residual graph, to accelerate checking
       if it may still contain a maximal maching"""
    def __init__(self, adj, res, isolated):
        # adj: the original graph, as an adjacency dictionary
        # res: residual graph (initially, identical to adj)
        # isolated: vertices with no incident edges in the the residual graph
        self.adj = adj
        self.res = deepcopy(res)
        self.isolated = isolated.copy()

    def __str__(self):
        return str(self.res)

    def copy(self):
        return Residual(self.adj, self.res, self.isolated)

    def _update(self, orig, dest):
        self._may_be_maximal = True
        for i in self.isolated:
            for j in self.isolated:
                if j>i and j in self.adj[i]:
                    self._may_be_maximal = False

    def del_edge_in_matching(self, edge):
        (orig,dest) = edge
        for i in [orig,dest]:
            for j in self.res[i]:
                self.res[j].remove(i)
                if len(self.res[j]) == 0:
                    self.isolated.add(j)
            del self.res[i]
            self.isolated.discard(i)
        self._update(orig, dest)

    def del_edge_not_in_matching(self, edge):
        (orig,dest) = edge
        self.res[orig].remove(dest)
        self.res[dest].remove(orig)
        for i in [orig,dest]:
            if len(self.res[i]) == 0:
                self.isolated.add(i)
        self._update(orig, dest)

    def may_be_maximal(self):
        return self._may_be_maximal


def all_matchings(adj, edges, matchings, match, resid):
    # adj: the original graph, as an adjacency dictionary [not modified]
    # * edges: remaining edges in the graph (initially, all its edges)
    # * matchings: current list of matchings found (initially empty)
    # * match: currently being enumerated
    # * resid: residual graph (initially, identical to adj)  [*: modified]

    if len(edges) > 0:
        edge = frozenset(edges.pop())
        (orig,dest) = edge

        # add (orig,dest) to the matching; so, remove all edges connected to (orig,dest) from resid
        m_add = match.copy()
        m_add.add(edge)
        e_add = set(e for e in edges if len(set(e) & edge) == 0)
        r_add = resid.copy()
        r_add.del_edge_in_matching(edge)
        if r_add.may_be_maximal():
            if len(e_add) == 0:
                matchings.append(m_add.copy())
                print("*** added matching", to_str(m_add), "/", len(matchings))
            else:
                all_matchings(adj, e_add, matchings, m_add, r_add)
        
        # do NOT add (i,j) to the matching; remove only (i,j) from resid
        if len(edges) > 0:   # this implies e_add being true (!!!)
            r_out = resid
            r_out.del_edge_not_in_matching(edge)
            if r_out.may_be_maximal():
                all_matchings(adj, edges, matchings, match, r_out)

    else:
        assert False
    return matchings


def get_kep_edges(adj):
    """given a directed KEP graph, return its edges (i.e., its 2-cycles)"""
    V = adj.keys()
    edges = []
    for i in V:
        for j in V:
            if j <= i:
                continue
            if j in adj[i] and i in adj[j]:
                # print("edge", (i,j))
                edges.append(frozenset((i,j)))
    return edges


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
    try:
        import sys
        from kep_io import read_prob
        filename = sys.argv[1]
        adj_, w_, p_ = read_prob(filename)  # read directed graph
        print("adj_", adj_)
        edges = get_kep_edges(adj_)  # edges for 2-cycles
        print("edges", edges)
        adj = adj_from_edges(edges)
        print("adj", adj)
    except:
        # print("usage: python %s filename.input[.gz]" % sys.argv[0])
        # exit(-1)
        # adj = {1:[2,4], 2:[1,3], 3:[2,4], 4:[1,3]}
        # adj = {1:[2,5,6], 2:[1,3,5], 3:[2,4,5], 4:[3,5], 5:[1,2,3,4], 6:[1]}
        # adj = {1:set([2,3,4]), 2:set([1]), 3:set([1]), 4:set([1])}
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
    resid = Residual(adj, res=adj, isolated={i for i in adj if len(adj[i]) == 0})
    m_all = all_matchings(adj=adj, edges=edges, matchings=[], match=set(), resid=resid)
    sols = sorted([sorted([(i,j) for (i,j) in m]) for m in m_all])
    for m in sols:
        print(to_str(m))
        # plot_matching(G,m)
    print("maximal matchings:", len(m_all))
