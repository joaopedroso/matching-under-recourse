import re
import random
from kep_io import write_prob

def read_delorme(filename):
    """read file in the 'Delorme' format used by Blom et al.
       Cutting Plane Approaches for the Robust Kidney Exchange Problem
       by Danny Blom, Christopher Hojny, and Bart Smeulders.
    """
    if filename.find(".gz") > 0:
        f = gzip.open(filename)
    else:
        f = open(filename)
    data = f.readlines()
    f.close()

    # lines defining the graph are in the form "(X, Y), A, B", where (X,Y) are the edges
    pattern = r"\((?P<X>.+), *(?P<Y>.+)\), *(?P<A>.+), *(?P<B>.+)"

    # list to store extracted graph
    graph = []
    for line in data:
        match = re.search(pattern, line)  # match the pattern
        if match:  # check if there's a match
            group_dict = match.groupdict()  # access by names (X, Y, A, B)
            graph.append(group_dict)

    # make graph
    adj = {}
    w = {}
    for item in graph:
        i, j = int(item['X']), int(item['Y'])
        if i in adj:
            adj[i].append(j)
        else:
            adj[i] = [j]
        w[i, j] = 1
        assert i >= 0 and j >= 0
        # print(i,j,w[i,j])

    return adj, w


def delorme2kep(filename):
    "make/write kep 'standard' + probability files corresponding to instance in Blom et al. format"
    adj, w = read_delorme(filename)

    filename = filename.replace(".txt", ".input")
    if filename.find(".gz") > 0:
        f = gzip.open(filename, "w")
    else:
        f = open(filename, "w")

    f.write("%s\t%s\n" % (len(adj), sum(len(adj[i]) for i in adj)))
    for i in sorted(adj):
        for j in sorted(adj[i]):
            w = 1
            f.write("%s\t%s\t%s\n" % (i,j,w))
    f.write("%s\t%s\t%s\n" % (-1, -1, -1))
    f.close()
    write_prob(filename)


if __name__ == "__main__":
    import sys
    import os
    try:
        filename = sys.argv[1]
    except:
        print("usage: python %s filename.txt[.gz]" % sys.argv[0])
        print("produces 'filename.input[.gz]' and 'filename.prob[.gz]' in klimentova's kep format")
        exit(-1)

    random.seed(1)
    kep_file = filename.replace(".txt", ".input")
    if os.path.exists(kep_file) or os.path.exists(kep_file + ".gz"):
        print(kep_file, "exists, not overwriting")
    else:
        delorme2kep(filename)

