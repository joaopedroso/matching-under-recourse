"""
cycle_db.py:  export database with precomputed expectation expressions

creates object DB of class cycle_db, which can be called with
    DB.expect(G,p)
    where:
        - G: graph with cycle for which expectation is to be computed
        - p: probabilities of failure for vertices and arcs in G
    returns value for the expected length of a cycle packing with internal recourse

Copyright (c) by Joao Pedro PEDROSO, 2012
"""
import networkx as nx
from networkx.algorithms import isomorphism

class cycle_db:
    def __init__(self):
        self.db = {}

    def add(self, g, f):
        narcs = len(g.edges())
        if not self.db.has_key(narcs):
            self.db[narcs] = {}
        self.db[narcs][g] = f

    def expect(self, g, p):
        # compute expectation for graph 'g' with probabilities of failure 'p'
        # by using an expression derived for an isomorphic graph
        
        # print "incoming:", g.edges()
        narcs = len(g.edges())
        for Gn in self.db[narcs]:
            DiGM = isomorphism.DiGraphMatcher(Gn,g)
            if DiGM.is_isomorphic():
                # print "isomorphic:", Gn.edges()
                r = DiGM.mapping
                pprime = {}
                # print "r:", r
                for i in Gn.nodes():
                    # print i, r[i]
                    pprime[i] = p[r[i]]
                for (i,j) in Gn.edges():
                    # print (i,j), (r[i],r[j])
                    pprime[i,j] = p[r[i],r[j]]
                    
                return self.db[narcs][Gn](pprime)

        raise(Exception,"unhandled graph: %r" % g.edges())




import re
__re_arc = re.compile(r"p_([0-9]+)_([0-9]+)", re.IGNORECASE)
__re_node = re.compile(r"p([0-9]+)", re.IGNORECASE)	# after replacing arcs!
def string_to_function(s):
    """prep: prepare python function from the input string
    Example:
        3*(p1 - 1)*(p2 - 1)*(p3 - 1)*(p_1_2 - 1)*(p_2_3 - 1)*(p_3_1 - 1)
    Becomes a function returning:
        3*(p[1] - 1)*(p[2] - 1)*(p[3] - 1)*(p[1,2] - 1)*(p[2,3] - 1)*(p[3,1] - 1)
    """
    tmp = __re_arc.sub(lambda x : "p[%s,%s]"%(x.group(1),x.group(2)), s)
    expr = __re_node.sub(lambda x : "p[%s]"%x.group(1), tmp)
    exec('py = lambda p:' + expr)
    return py
    


if __name__ == "__main__":
    # some examples
    arcs = [(2, 1), (1, 2)]
    G = nx.DiGraph()
    G.add_edges_from(arcs)
    p = { 1:0.1, 2:0.1, (1,2):0, (2,1):0 }
    print DB.expect(G,p)

    arcs = [(1, 2), (2, 3), (3, 1)]
    G = nx.DiGraph()
    G.add_edges_from(arcs)
    p = { 1:0.1, 2:0.1, 3:0.1, (1,2):0, (2,3):0, (3,1):0 }
    print DB.expect(G,p)

    arcs = [(1, 2), (2, 3), (3, 1), (1, 3)]
    G = nx.DiGraph()
    G.add_edges_from(arcs)
    p = { 1:0.1, 2:0.1, 3:0.1, (1,2):0, (2,3):0, (3,1):0, (1,3):0. }
    print DB.expect(G,p)

    p = { 1:0.1, 2:0.1, 3:0.1, (1,2):0, (2,3):0, (3,1):0, (1,3):1. }
    print DB.expect(G,p)

    arcs = [(1, 2), (2, 3), (3, 1), (2,1)]
    G = nx.DiGraph()
    G.add_edges_from(arcs)
    p = { 1:0.1, 2:0.1, 3:0.1, (1,2):0, (2,3):0, (3,1):0, (2,1):0. }
    print DB.expect(G,p)

    p = { 1:0.1, 2:0.1, 3:0.1, (1,2):0, (2,3):0, (3,1):0, (2,1):1. }
    print DB.expect(G,p)

    arcs = [(1, 2), (1, 3), (3, 2), (2, 1)]
    print "arcs:", arcs
    G = nx.DiGraph()
    G.add_edges_from(arcs)
    p = { 1:0.0, 2:0., 3:0.1, (1,2):0, (1,3):0, (3,2):0, (2,1):0.25 }
    print DB.expect(G,p)
