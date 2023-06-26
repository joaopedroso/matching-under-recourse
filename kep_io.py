import gzip
import random

def read_kep(filename):
    "read file in the 'standard' kep format"
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
    "make/write probability file corresponding to a 'standard' kep format"
    def rnd():
        return random.random()
    
    adj, w = read_kep(filename)
    filename = filename.replace(".input", ".prob")
    if filename.find(".gz") > 0:
        f = gzip.open(filename,"w")
    else:
        f = open(filename,"w")

    for i in sorted(adj):
        f.write("%s\n" % rnd())
        for j in sorted(adj[i]):
            f.write("%s " % rnd())
        f.write("\n")
    f.close()

def read_prob(filename):
    "read probability file corresponding to a 'standard' kep format"
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
        adj, w, p = read_prob(filename)
    else:
        write_prob(filename)
        adj_, w_, p_ = read_prob(filename)
        assert adj_ == adj
        assert w_ == w
        assert p_ == p        
