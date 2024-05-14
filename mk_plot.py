import sys
import subprocess
import os.path
import numpy as np
import matplotlib.pyplot as plt
avg = lambda v : sum(v)/len(v)

if len(sys.argv) != 2:
    print("usage: python %s filename.csv" % sys.argv[0])
    exit(0)

filename = sys.argv[1]

Nlist = [999999]  ##### ["0","1","2","3","999999"]
NSUCCESS = {}
NFAILS = {}

avg = lambda x: sum(x)/len(x)

import csv
CPU, CACHE, EDGES, FAIL = {}, {}, {}, {}
with open(filename) as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    for row in reader:
        sn,nvert,nedges,_,expect,_,cpu,ncache = row
        nvert = int(nvert)
        nedges = int(nedges)
        ncache= int(ncache[ncache.find(":")+1:])
        if nvert not in EDGES:
            EDGES[nvert] = [] # set()
        EDGES[nvert].append(nedges)

        key = (nvert,nedges)
        if key not in CPU:
            CPU[key] = []
            CACHE[key] = []
            FAIL[key] = False
        cpu = float(cpu)
        CPU[key].append(min(3600, cpu))
        CACHE[key].append(ncache)
        if cpu >= 3600:
            FAIL[key] = True
            print(key, "failed")
        # print(key, avg(CPU[key]), avg(CACHE[key]))

VERT = list(sorted(EDGES.keys()))
output = None
output = "cpu_graphs.pdf"
title = ["|V| = {}".format(v) for v in VERT]
ylabel = ["CPU time"]
# xlabel = ["number of vertices", "number of edges"]
logy = True
import numpy as np
import matplotlib.pyplot as plt
 
fig, ax = plt.subplots(1, 1, sharex='col', sharey='row', figsize=(5,5))
# plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.03, hspace=0.03)

# ax[j].set_title(title[j], size=8)
ax.set_ylim(ymin=1.e-4, ymax=10000)
ax.grid(True)
ax.set_yscale("log")

line = {}
for j,v in enumerate(VERT):
    # ax[j].legend(title='Instance sizes',fontsize=8,loc=4)

    print("v={}".format(v))
    #!#!x = sorted(EDGES[v])
    #!#!y = [avg(CPU[v,e]) for e in x]
    x = sorted(e for e in EDGES[v] if not FAIL[v,e])
    y = [avg(CPU[v,e]) for e in EDGES[v] if not FAIL[v,e]]
    xx = sorted(e for e in EDGES[v] if FAIL[v,e])
    yy = [avg(CPU[v,e]) for e in EDGES[v] if FAIL[v,e]]
    # x = [e for e in EDGES[v] for k in range(len(CPU[v,e])) if (v,e) in CPU]
    # y = [CPU[v,e][k] for e in EDGES[v] for k in range(len(CPU[v,e])) if (v,e) in CPU]
    print("x=", x)
    print("y=", y)
    print("xx=", xx)
    print("yy=", yy)
    print()

    V = max(VERT)
    color = str((V-v)/(V))
    color = "0."
    label = " {} vertices".format(v)
    line[v] = ax.scatter(x=x, y=y, s=100, color=color, label=label, alpha=0.5, marker = 'x', cmap='gray')
    ax.scatter(x=xx, y=yy, s=100, color=color, alpha=0.75, cmap='gray')

    ax.grid(color='gray', linestyle='-', linewidth=0.5, alpha=0.2)

ax.set_ylabel(ylabel[0], size=10)
ax.set_xlabel("Number of edges", size=10)
ax.set_yscale('log')

# plt.legend(title='Number of vertices', handles=[line[l] for l in sorted(line)], loc=4, fontsize=8)

# plt.suptitle("A GREATER TITLE")
# Fine-tune figure; hide x ticks for top plots and y ticks for right plots
# see http://stackoverflow.com/questions/19626530/python-xticks-in-subplots
# plt.setp([a.get_xticklabels() for a in ax[0, :]], visible=False)
# plt.setp([a.get_xticklabels() for a in ax[1, :]], size=7)
# plt.setp([a.get_yticklabels() for a in ax[:, 1]], visible=False)
# plt.setp([a.get_yticklabels() for a in ax[:, 0]], size = 7)
# plt.setp([a.get_yticklabels() for a in ax[0]], size = 7)
 
if output:
    plt.savefig(output)
else:
    plt.show()

exit(0)

# write processed output as latex text
outf = sys.stdout   # open("nnodes.tex", "w")
outf.write("Instances\t&")
for N in Nlist:
    outf.write("\t& \multicolumn{1}{c}{N=%s}" % N)
outf.write(r" \\" + "\n")
for inst in SIZES: # 10 20 ... 50
    outf.write( ("%s pairs\t& "*1) % (inst))
    for N in Nlist:
        outf.write('\t& %g' % NSUCCESS[inst,N])
    outf.write(r" \\" + "\n")                


