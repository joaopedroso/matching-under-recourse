# code for calculating the number of different configurations as a
# function of the size of a graph


import sys
import networkx as nx
from networkx.algorithms import isomorphism


def add_graph(Gs, N, edges):
    """add_graph: check if given graph is isomorphic to another in list, if not add it
    Parameters:
        * Gs - graph database
        * N - number of nodes in the new graph
        * edges - list of edges
    Output: True if new graph was added, False if not
    """
    Gn = nx.Graph()
    Gn.add_nodes_from(range(1,N+1))
    Gn.add_edges_from(edges)

    for G in Gs:
        GM = isomorphism.GraphMatcher(G,Gn)
        if GM.is_isomorphic():
            return False
    Gs.append(Gn)
    # print("added", Gn.edges(), len(Gs), "graphs")
    return True
        


def mk_graphs(Gs, N, node, edges):
    """mk_graphs: list of all non-isomorphic connected graphs with given number of vertices
    Parameters:
        * Gs - list with current graph database
        * N - number of vertices
        * node - vertex currently being considered as source (from-vertex)
        * edges - current list of edges
    Output:
        * list with all non-isomorphic graphs from the initial base
    """
    # modify coming graph by adding all possible edges from 'node'
    for i in range(N):
        j = i+1
        edge = frozenset((node,j))
        if j != node and edge not in edges:
            if add_graph(Gs, N, edges | set([edge])):
                mk_graphs(Gs, N, node, edges | set([edge]))
    if node != N:
        mk_graphs(Gs, N, node+1, edges)
    return Gs

def generate_graphs(K):
    """generate_graphs: generator of non-isomorphic connected graphs, sorted by number of vertices, then nubmer of edges
    Parameters:
        * K - maximum number of vertices to consider
    Output:
        * all non-isomorphic graphs up to given size
    """
    for N in range(2, K+1):
        edges = set()
        # starting with a path:
        for i in range(N-1):
            edges.add(frozenset((i+1,i+2)))

        G = nx.Graph()
        G.add_nodes_from(range(1,N+1))
        G.add_edges_from(edges)
        Gs = mk_graphs([G], N, 1, edges)
        cmp=lambda G: len(G.edges())
        Gs.sort(key=cmp)
        for G in Gs:
            yield G




if __name__ == "__main__":
    try:
        K = int(sys.argv[1])	# max cycle len to consider
    except:
        print("usage: {} K, where K is the maximum number of nodes".format(sys.argv[0]))
        exit(0)

    for N in range(2, K+1):
        edges = set()
        # starting with a path:
        for i in range(N-1):
            edges.add(frozenset((i+1,i+2)))

        G = nx.Graph()
        G.add_nodes_from(range(1,N+1))
        G.add_edges_from(edges)
        Gs = mk_graphs([G], N, 1, edges)
        cmp=lambda G: len(G.edges())
        Gs.sort(key=cmp)
        for G in Gs:
            print("{}\t{}\t{}".format(len(G),len(G.edges()),G.edges()))
        print("N={}, {} graphs\n".format(N,len(Gs)))
