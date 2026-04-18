"""Utility for visualising a KEP graph and a matching using NetworkX/Matplotlib.

When run as a script, reads a KEP instance, extracts 2-cycle edges, finds the
maximum-weight matching for each connected component, and draws the graph with
matched edges highlighted.

Usage::

    python plot.py <instance.input[.gz]>
"""
from kep_io import read_prob, get_kep_edges
import sys
import os

import networkx as nx
def plot_matching(G,m):
    # pos=nx.graphviz_layout(G)
    # pos=nx.graphviz_layout(G,prog='dot')
    # pos=nx.spring_layout(G)

    #      import matplotlib.pyplot as plt
    #      # nx.draw(G)
    #      # nx.draw_spring(G,k=1.0,iterations=10000)
    #      nx.draw_spring(G)
    #      # nx.draw_spectral(G)
    #      # nx.draw_graphviz(G,iterations=10000,k=1.0)
    #      plt.show()

    pos=nx.spring_layout(G,k=1.0,iterations=10000)
    # pos=nx.graphviz_layout(G)
    import matplotlib.pyplot as plt
    limits=plt.axis('off') # turn of axis

    nx.draw_networkx(G, pos=pos, with_labels=True, font_size=8, edge_color='gray')
    nx.draw_networkx(G, pos=pos, with_labels=True, font_size=8, edgelist=m, edge_color='black', width=3)
    plt.show()



if __name__ == "__main__":
    try:
        filename = sys.argv[1]
    except:
        print("usage: python %s filename.input[.gz]" % sys.argv[0])
        exit(-1)

    adj, w, p = read_prob(filename)
    edges, _ = get_kep_edges(adj, p)

    G = nx.Graph()
    G.add_edges_from(edges)

    components = list(nx.connected_components(G))

    print("connected components:")
    for c in components:
        print(c)

        sG = nx.subgraph(G, c)
        # m = nx.maximal_matching(sG)
        m = nx.max_weight_matching(sG, maxcardinality=False)
        print("maximum cardinality maching", m)
        edges = [(i,m[i]) for i in m if i>m[i]]

        plot_matching(G,edges)