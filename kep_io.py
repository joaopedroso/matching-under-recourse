"""I/O utilities for KEP instances in Klimentova et al. format.

File formats
------------
``<name>.input[.gz]``
    Directed graph.  First line: ``nvert narcs``.  Each subsequent line:
    ``i  j  weight`` (one arc per line).  Vertices are non-negative integers.
    Sentinel line ``-1  -1  -1`` ends the arc list.

``<name>.prob[.gz]``
    Failure probabilities, one vertex block per vertex (in sorted order).
    Each block has two lines:

    - Line 1: ``p_i``  — probability that vertex i fails.
    - Line 2: ``p_{i,j1}  p_{i,j2}  …`` — failure probability for each
      outgoing arc of i, in the same sorted order as in the .input file.

Edge (2-cycle) failure probability
-----------------------------------
An undirected edge {i, j} represents the 2-cycle i → j → i.  The edge
fails if *any* of the four components fail (both vertices, both arcs)::

    p_edge = 1 − (1−p_i)(1−p_j)(1−p_{i,j})(1−p_{j,i})

Benchmark instances
-------------------
Klimentova et al. instances (small, up to 50 vertices):
    https://www.dcc.fc.up.pt/~jpp/code/KEP/

Blom et al. (Delorme) instances (50 and 100 vertices):
    see ``delorme2kep.py`` for format conversion.
"""
import re
import gzip
import random

def read_kep(filename):
    """Read a KEP instance file in Klimentova et al. format.

    Parameters
    ----------
    filename : str
        Path to a ``.input`` or ``.input.gz`` file.

    Returns
    -------
    adj : dict
        Directed adjacency dict {i: [j, …]}.
    w : dict
        Arc weights: w[i, j] = weight of arc i → j.
    """
    if filename.find(".gz") > 0:
        f = gzip.open(filename)
    else:
        f = open(filename)
    data = list(reversed(f.read().split()))
    f.close()
    nvert = int(data.pop())
    narcs = int(data.pop())
    adj = {}
    w = {}
    for a in range(narcs):
        i = int(data.pop())
        j = int(data.pop())
        if i in adj:
            adj[i].append(j)
        else:
            adj[i] = [j]
        w[i,j] = float(data.pop())
        assert i>=0 and j>=0
    return adj, w


def write_prob(filename):
    """Generate and write random failure probabilities for a KEP instance.

    Reads the graph from ``filename`` and writes a corresponding ``.prob``
    (or ``.prob.gz``) file with uniformly random probabilities in [0, 1)
    for each vertex and arc.  The random state must be seeded by the caller.

    Parameters
    ----------
    filename : str
        Path to the ``.input`` or ``.input.gz`` file.  The output file
        is written alongside it with the ``.input`` suffix replaced by
        ``.prob``.
    """

    def rnd():
        return random.random()

    adj, w = read_kep(filename)
    filename = filename.replace(".input", ".prob")
    if filename.find(".gz") > 0:
        f = gzip.open(filename, "w")
    else:
        f = open(filename, "w")

    for i in sorted(adj):
        f.write("%s\n" % rnd())
        for j in sorted(adj[i]):
            f.write("%s " % rnd())
        f.write("\n")
    f.close()


def read_prob(filename):
    """Read a KEP instance together with its failure probabilities.

    Parameters
    ----------
    filename : str
        Path to the ``.input`` or ``.input.gz`` file; the ``.prob``
        counterpart is located automatically.

    Returns
    -------
    adj : dict
        Directed adjacency dict.
    w : dict
        Arc weights.
    p : dict
        Failure probabilities: p[i] for vertex i, p[i,j] for arc i→j.
    """
    adj, w = read_kep(filename)
    filename = filename.replace(".input", ".prob")
    if filename.find(".gz") > 0:
        f = gzip.open(filename)
    else:
        f = open(filename)

    data = list(reversed(f.read().split()))
    f.close()
    p = {}
    for i in sorted(adj):
        p[i] = float(data.pop())
        for j in sorted(adj[i]):
            p[i,j] = float(data.pop())

    return adj, w, p


def get_kep_edges(adj, p_):
    """Extract undirected edges (2-cycles) from a directed KEP graph.

    A 2-cycle {i, j} exists when both arcs i→j and j→i are present.
    The combined failure probability accounts for both vertices and both arcs::

        p_edge = 1 − (1−p_i)(1−p_j)(1−p_{i,j})(1−p_{j,i})

    Parameters
    ----------
    adj : dict
        Directed adjacency dict from ``read_kep`` or ``read_prob``.
    p_ : dict
        Failure probabilities from ``read_prob``: p_[i] and p_[i, j].

    Returns
    -------
    edges : list of frozenset
        Undirected edges {i, j} (2-cycles), each as a frozenset.
    p : dict
        Combined edge failure probabilities: p[frozenset({i,j})].
    """
    V = adj.keys()
    p = {}
    edges = []
    for i in V:
        for j in V:
            if j <= i:
                continue
            if j in adj[i] and i in adj[j]:
                # print("edge", (i,j))
                edge = frozenset((i,j))
                edges.append(edge)
                p[edge] = 1 - (1-p_[i])*(1-p_[j])*(1-p_[i,j])*(1-p_[j,i])
    return edges,p


if __name__ == "__main__":
    import sys
    import os 
    try:
        filename = sys.argv[1]
        seed = int(sys.argv[2])
    except:
        print("%s: draw probabilities for arc and node failure in kep instance" % sys.argv[0])
        print("usage: python %s filename.input[.gz] seed" % sys.argv[0])
        print("produces 'filename.prob[.gz]'")
        exit(-1)

    random.seed(seed)
    probfile = filename.replace(".input", ".prob")
    if os.path.exists(probfile) or os.path.exists(probfile+".gz"):
        print(probfile, "exists, not overwriting")
    else:
        write_prob(filename)
