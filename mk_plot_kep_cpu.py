import sys
import subprocess
import os.path
import numpy as np
import matplotlib.pyplot as plt
import csv

avg = lambda v: sum(v) / len(v)

output = "cpu_kep.pdf"
Nlist = ["0", "1", "2", "3", "999999"]
Nlabel = {"0": "1", "1": "2", "2": "3", "3": "4", "999999": r"$\infty$"}
SIZES = [10, 20, 30, 40, 50]

#
# read data for exact solution, fill variables for plotting
#
filename = "RESULTS/summary_solve_khm.csv"
MISSINGo = {}
NSUCCESSo = dict(((inst, N), 0.) for inst in SIZES for N in Nlist)
NFAILSo = dict(((inst, N), 0.) for inst in SIZES for N in Nlist)
INSTo, NEDGESo, NVERTo, EXPECTo, CPUo, CACHEo = {}, {}, {}, {}, {}, {}
with open(filename) as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    for row in reader:
        instname,N,nvert,nedges,expect,cpu,ncache = row
        assert N in Nlist
        inst = instname[instname.rfind("/")+1:instname.find(".input")]
        seq = int(inst[3:])
        inst = int(inst[:2])
        try:
            nvert = int(nvert)
            nedges = int(nedges)
            MISSINGo[instname] = nvert, nedges
        except:
            # "blacklisted" files, no data in csv
            nvert, nedges = MISSINGo[instname]
        key = (N, nvert, nedges, seq)
        INSTo[key] = int(inst)
        if cpu == "None":  # in some legacy experiments...
            cpu = 3600
        CPUo[key] = min(3600, float(cpu))
        NEDGESo[key] = int(nedges)
        NVERTo[key] = int(nvert)
        if expect == "None":  # beware: string, not object None
            NFAILSo[inst, N] += 1
            assert CPUo[key] >= 3600
        else:
            NSUCCESSo[inst, N] += 1
            EXPECTo[key] = float(expect) / 2   # !!!! number or edges, not vertices (2024 revision)
            CACHEo[key] = int(ncache)
    for inst in SIZES:
        for N in Nlist:
            assert NSUCCESSo[inst, N] + NFAILSo[inst, N] == 50

xo, yo = {}, {}
xxo, yyo = {}, {}
for inst in SIZES:
    KEYS = [k for k in INSTo if INSTo[k] == inst]
    for i in Nlist:
        for j in range(2):
            xo[i, j, inst], yo[i, j, inst] = [], []
            xxo[i, j, inst], yyo[i, j, inst] = [], []  # failed cases
            for k in KEYS:
                (_N, _nvert, _nedges, _seq) = k
                if str(_N) != str(i) or _nedges == 0:
                    continue
                if CPUo[k] < 3600:
                    if j == 0:
                        xo[i, j, inst].append(NVERTo[k])
                    else:
                        xo[i, j, inst].append(NEDGESo[k])
                    yo[i, j, inst].append(CPUo[k])
                else:  # failed cases
                    if j == 0:
                        xxo[i, j, inst].append(NVERTo[k])
                    else:
                        xxo[i, j, inst].append(NEDGESo[k])
                    yyo[i, j, inst].append(CPUo[k])


filename = "RESULTS/summary_greedy-k_khm.csv"
MISSINGg = {}
NSUCCESSg = dict(((inst, N), 0.) for inst in SIZES for N in Nlist)
NFAILSg = dict(((inst, N), 0.) for inst in SIZES for N in Nlist)
INSTg, NEDGESg, NVERTg, EXPECTg, CPUg, CACHEo = {}, {}, {}, {}, {}, {}
with open(filename) as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    for row in reader:
        instname, N, nvert, nedges, expect, cpu, ncache = row
        assert N in Nlist
        inst = instname[instname.rfind("/") + 1:instname.find(".input")]
        seq = int(inst[3:])
        inst = int(inst[:2])
        try:
            nvert = int(nvert)
            nedges = int(nedges)
            MISSINGg[instname] = nvert, nedges
        except:
            # "blacklisted" files, no data in csv
            nvert, nedges = MISSINGg[instname]
        key = (N, nvert, nedges, seq)
        INSTg[key] = int(inst)
        if cpu == "None":  # in some legacy experiments...
            cpu = 3600
        CPUg[key] = min(3600, float(cpu))
        NEDGESg[key] = int(nedges)
        NVERTg[key] = int(nvert)
        if expect == "None":  # beware: string, not object None
            NFAILSg[inst, N] += 1
            assert CPUg[key] >= 3600
        else:
            NSUCCESSg[inst, N] += 1
            EXPECTg[key] = float(expect) / 2   # !!!! number or edges, not vertices (2024 revision)
            CACHEo[key] = int(ncache)
    for inst in SIZES:
        for N in Nlist:
            assert NSUCCESSg[inst, N] + NFAILSg[inst, N] == 50

xg, yg = {}, {}
xxg, yyg = {}, {}
for inst in SIZES:
    KEYS = [k for k in INSTg if INSTg[k] == inst]
    for i in Nlist:
        for j in range(2):
            xg[i, j, inst], yg[i, j, inst] = [], []
            xxg[i, j, inst], yyg[i, j, inst] = [], []  # failed cases
            for k in KEYS:
                (_N, _nvert, _nedges, _seq) = k
                if str(_N) != str(i) or _nedges == 0:
                    continue
                if CPUg[k] < 3600:
                    if j == 0:
                        xg[i, j, inst].append(NVERTg[k])
                    else:
                        xg[i, j, inst].append(NEDGESg[k])
                    yg[i, j, inst].append(CPUg[k])
                else:  # failed cases
                    if j == 0:
                        xxg[i, j, inst].append(NVERTg[k])
                    else:
                        xxg[i, j, inst].append(NEDGESg[k])
                    yyg[i, j, inst].append(CPUg[k])



#
# read data for greedy solution, fill variables for plotting
#
title = ["CPU used in terms of the number of vertices", "CPU used in terms of the number of edges"]
ylabel = [f"N = {Nlabel[N]}" for N in Nlist]
xlabel = ["number of vertices", "number of edges"]
logy = True
fig, ax = plt.subplots(len(Nlist), 2, sharex='col', sharey='row', figsize=(10, 10))
plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.03, hspace=0.03)

line = {}
colors = ['#525252', '#88419d', '#2b8cbe', '#d7301f', '#238b45']
for i, N in enumerate(Nlist):
    for j in range(2):
        ax[i, j].grid(True)
        for inst in SIZES:
            alpha = .15 + .75 * inst / 50  # (max(SIZES)+10))
            label = f"{inst} pairs"

            # optimal
            line[inst] = ax[i, j].scatter(x=xo[N, j, inst], y=yo[N, j, inst], marker='x', s=20,
                                          color=colors[0], alpha=alpha, label=label)
            # failed cases:
            ax[i, j].scatter(x=xxo[N, j, inst], y=yyo[N, j, inst], marker='x', s=10,
                             color=colors[0], alpha=alpha, label=label)

            # greedy
            line[1000*inst] = ax[i, j].scatter(x=xg[N, j, inst], y=yg[N, j, inst], marker='+', s=30,
                                          color=colors[1], alpha=alpha, label='(greedy-k)')
            # failed cases:
            ax[i, j].scatter(x=xxg[N, j, inst], y=yyg[N, j, inst], marker='+', s=15,
                             color=colors[1], alpha=alpha, label='(greedy-k)')

        plt.legend(title='Instance sizes', handles=[line[l] for l in sorted(line)], loc=4, fontsize=6, ncol=2)

        ax[i, j].set_xlim(xmin=-2)

        ax[i, j].grid(color='gray', linestyle='-', linewidth=0.5, alpha=0.2)
        if i == 0:
            ax[i, j].set_title(title[j], size=7)
        if j == 0:
            ax[i, j].set_ylabel(ylabel[i], size=7)
        # else:
        #     ax[i, j].set_xlim(xmax=100)  # !!!!! take care not to miss any solved instance
        if i == 2 - 1:
            ax[i, j].set_xlabel(xlabel[j])
        if logy:
            ax[i, j].set_yscale('log')

# plt.suptitle("A GREATER TITLE")
# Fine-tune figure; hide x ticks for top plots and y ticks for right plots
# see http://stackoverflow.com/questions/19626530/python-xticks-in-subplots
# !#! plt.setp(ax, xticks=[i+1 for i in index], xticklabels=sizes)
plt.setp([a.get_xticklabels() for a in ax[0, :]], visible=False)
plt.setp([a.get_xticklabels() for a in ax[1, :]], size=7)
plt.setp([a.get_yticklabels() for a in ax[:, 1]], visible=False)
plt.setp([a.get_yticklabels() for a in ax[:, 0]], size=7)

if output:
    plt.savefig(output)
else:
    plt.show()

# write processed output as latex text
outf = sys.stdout  # open("nnodes.tex", "w")
outf.write("Instances")
for N in Nlist:
    outf.write("\t& \\multicolumn{2}{c}{N=%s}" % Nlabel[N])
outf.write(r" \\" + "\n")
for inst in SIZES:  # 10 20 ... 50
    outf.write(("%s pairs" * 1) % (inst))
    for N in Nlist:
        outf.write('\t& %5g' % NSUCCESSo[inst, N])
        outf.write('\t& %5g' % NSUCCESSg[inst, N])
    outf.write(r" \\" + "\n")


