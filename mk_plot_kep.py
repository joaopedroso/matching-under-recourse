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

Nlist = ["0","1","2","3","inf"]
SIZES = [10,20,30,40,50]
NSUCCESS = dict(((inst,N),0.) for inst in SIZES for N in Nlist)
NFAILS = dict(((inst,N),0.) for inst in SIZES for N in Nlist)

import csv
INST, NEDGES, NVERT, EXPECT, CPU, CACHE = {}, {}, {}, {}, {}, {}
with open(filename) as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    for row in reader:
        inst,N,nvert,nedges,expect,cpu,ncache,_ = row
        assert N in Nlist
        inst = inst[inst.rfind("/")+1:inst.find(".input")]
        seq = int(inst[3:])
        inst = int(inst[:2])
        nvert = int(nvert)
        nedges = int(nedges)
        key = (N,nvert,nedges,seq)
        INST[key] = int(inst)
        if cpu == "None":  # in some legacy experiments...
            cpu = 3600
        CPU[key] = min(3600, float(cpu))
        NEDGES[key] = int(nedges)
        NVERT[key] = int(nvert)
        if expect == "None":    # beware: string, not object None
            NFAILS[inst,N] += 1
            assert CPU[key] >= 3600
        else:
            NSUCCESS[inst,N] += 1
            EXPECT[key] = float(expect)
            CACHE[key] = int(ncache)
    for inst in SIZES:
        for N in Nlist:
            assert NSUCCESS[inst,N] + NFAILS[inst,N] == 50

output = "cpu_kep.pdf"
title = ["CPU used in terms of the number of vertices", "CPU used in terms of the number of edges"]
ylabel = ["N = {}".format(N) for N in Nlist]
xlabel = ["number of vertices", "number of edges"]
logy = True
index = np.arange(len(SIZES))
filename = None
x,y = {},{}
xx,yy = {},{}
 
for inst in SIZES:
    KEYS = [k for k in INST if INST[k] == inst]
    for i in Nlist:
        for j in range(2):
            x[i,j,inst], y[i,j,inst] = [], []
            xx[i,j,inst], yy[i,j,inst] = [], []  # failed cases
            for k in KEYS:
                if str(k[0]) != str(i):
                    continue
                if CPU[k] < 3600:
                    if j == 0:
                        x[i,j,inst].append(NVERT[k])
                    else:
                        x[i,j,inst].append(NEDGES[k])
                    y[i,j,inst].append(CPU[k])
                else:  # failed cases
                    if j == 0:
                        xx[i,j,inst].append(NVERT[k])
                    else:
                        xx[i,j,inst].append(NEDGES[k])
                    yy[i,j,inst].append(CPU[k])
 
 
import numpy as np
import matplotlib.pyplot as plt
 
fig, ax = plt.subplots(len(Nlist), 2, sharex='col', sharey='row', figsize=(10,10))
plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.03, hspace=0.03)
 
line = {}
for i,N in enumerate(Nlist):
    for j in range(2):
        ax[i,j].grid(True)
        ax[i,j].set_yscale("log")
        # ax[i,j].legend(title='Instance sizes',fontsize=8,loc=4)
        for inst in SIZES:
            color = str((50-inst)/50)  # (max(SIZES)+10))
            label = "{} pairs".format(inst)
            line[inst] = ax[i,j].scatter(x=x[N,j,inst], y=y[N,j,inst], s=60, color=color, alpha=0.5, cmap='gray', label=label)
            # failed cases:
            ax[i,j].scatter(x=xx[N,j,inst], y=yy[N,j,inst], s=50, color=color, marker='.', alpha=0.5, cmap='gray')
 
        plt.legend(title='Instance sizes', handles=[line[l] for l in sorted(line)], loc=4, fontsize=8)
 
        ax[i,j].set_xlim(xmin=-2)
 
        ax[i,j].grid(color='gray', linestyle='-', linewidth=0.5, alpha=0.2)
        if i == 0:
            ax[i,j].set_title(title[j], size=7)
        if j == 0:
            ax[i,j].set_ylabel(ylabel[i], size=7)
        else:
            ax[i,j].set_xlim(xmax=80)  # !!!!! take care not to miss any solved instance 
        if i == 2-1:
            ax[i,j].set_xlabel(xlabel[j])
        if logy:
            ax[i,j].set_yscale('log')
            
# plt.suptitle("A GREATER TITLE")
# Fine-tune figure; hide x ticks for top plots and y ticks for right plots
# see http://stackoverflow.com/questions/19626530/python-xticks-in-subplots
#!#! plt.setp(ax, xticks=[i+1 for i in index], xticklabels=sizes)
plt.setp([a.get_xticklabels() for a in ax[0, :]], visible=False)
plt.setp([a.get_xticklabels() for a in ax[1, :]], size=7)
plt.setp([a.get_yticklabels() for a in ax[:, 1]], visible=False)
plt.setp([a.get_yticklabels() for a in ax[:, 0]], size = 7)
 
if output:
    plt.savefig(output)
else:
    plt.show()


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


