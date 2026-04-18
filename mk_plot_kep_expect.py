import sys
import subprocess
import os.path
import numpy as np
import matplotlib.pyplot as plt
import csv

avg = lambda v: sum(v) / len(v)

output = "expect_kep.pdf"
Nlist = ["0", "1", "2", "3", "999999"]
Nlabel = {"0": "1", "1": "2", "2": "3", "3": "4", "999999": r"$\infty$"}
SIZES = [10, 20, 30, 40, 50]

#
# read data for exact solution, fill variables for plotting
#
filename = "RESULTS/summary_solve_khm.csv"
MISSINGo = {}
NSUCCESSo = dict(((inst, N), 0) for inst in SIZES for N in Nlist)
NFAILSo = dict(((inst, N), 0) for inst in SIZES for N in Nlist)
NEDGESo, NVERTo, EXPECTo, CPUo, CACHEo = {}, {}, {}, {}, {}
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
        key = (inst, N, nvert, nedges, seq)
        assert key not in CPUo
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
    KEYS = [k for k in CPUo if k[0] == inst]
    for i in Nlist:
        for j in range(2):
            xo[i, j, inst], yo[i, j, inst] = [], []
            xxo[i, j, inst], yyo[i, j, inst] = [], []  # failed cases
            for k in KEYS:
                (_inst, _N, _nvert, _nedges, _seq) = k
                if str(_N) != str(i) or _nedges == 0:
                    continue
                if CPUo[k] < 3600:
                    if j == 0:
                        xo[i, j, inst].append(NVERTo[k])
                    else:
                        xo[i, j, inst].append(NEDGESo[k])
                    # y[i,j,inst].append(CPU[k])
                    yo[i, j, inst].append(EXPECTo[k])
                else:  # failed cases
                    if j == 0:
                        xxo[i, j, inst].append(NVERTo[k])
                    else:
                        xxo[i, j, inst].append(NEDGESo[k])
                    # yy[i,j,inst].append(CPU[k])
                    yyo[i, j, inst].append(-0.25)


filename = "RESULTS/summary_greedy-k_khm.csv"
MISSINGg = {}
NSUCCESSg = dict(((inst, N), 0) for inst in SIZES for N in Nlist)
NFAILSg = dict(((inst, N), 0) for inst in SIZES for N in Nlist)
INSTg, NEDGESg, NVERTg, EXPECTg, CPUg, CACHEg = {}, {}, {}, {}, {}, {}
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
            MISSINGg[instname] = nvert, nedges
        except:
            # "blacklisted" files, no data in csv
            nvert, nedges = MISSINGg[instname]
        key = (inst, N, nvert, nedges, seq)
        assert key not in CPUg
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
            CACHEg[key] = int(ncache)
    for inst in SIZES:
        for N in Nlist:
            assert NSUCCESSg[inst, N] + NFAILSg[inst, N] == 50

xg, yg = {}, {}
xxg, yyg = {}, {}
for inst in SIZES:
    KEYS = [k for k in CPUg if k[0] == inst]
    for i in Nlist:
        for j in range(2):
            xg[i, j, inst], yg[i, j, inst] = [], []
            xxg[i, j, inst], yyg[i, j, inst] = [], []  # failed cases
            for k in KEYS:
                (_inst, _N, _nvert, _nedges, _seq) = k
                if str(_N) != str(i) or _nedges == 0:
                    continue
                if CPUg[k] < 3600:
                    if j == 0:
                        xg[i, j, inst].append(NVERTg[k])
                    else:
                        xg[i, j, inst].append(NEDGESg[k])
                    # y[i,j,inst].append(CPU[k])
                    yg[i, j, inst].append(EXPECTg[k])
                else:  # failed cases
                    if j == 0:
                        xxg[i, j, inst].append(NVERTg[k])
                    else:
                        xxg[i, j, inst].append(NEDGESg[k])
                    # yy[i,j,inst].append(CPU[k])
                    yyg[i, j, inst].append(-0.25)



#
# read data for greedy solution, fill variables for plotting
#
title = ["Expectation in terms of the number of vertices", "Expectation in terms of the number of edges"]
ylabel = [f"N = {Nlabel[N]}" for N in Nlist]
xlabel = ["number of vertices", "number of edges"]
logy = False
fig, ax = plt.subplots(len(Nlist), 2, sharex='col', sharey='row', figsize=(10, 10))
plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.03, hspace=0.03)

line = {}
colors = ['#525252', '#88419d', '#2b8cbe', '#d7301f', '#238b45']
for i, N in enumerate(Nlist):
    for j in range(2):
        ax[i, j].grid(True)
        # ax[i, j].set_yscale("log")
        # ax[i,j].legend(title='Instance sizes',fontsize=8,loc=4)
        for inst in SIZES:
            # alpha = .15 + .75 * inst / 50  # (max(SIZES)+10))
            alpha = .6

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

        plt.legend(title='Instance sizes', handles=[line[l] for l in sorted(line)],
                   ncol=2, loc='center right', fontsize=6)

        ax[i, j].set_xlim(xmin=-2)
        ax[i, j].set_ylim(ymax=3.5)

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
outf.write("instances solved\n")
outf.write("Instances")
for N in Nlist:
    outf.write(" & \\multicolumn{3}{c}{N=%s}" % Nlabel[N])
outf.write(r" \\" + "\n")
for inst in SIZES:
    KEYS = [k for k in CPUo if k[0] == inst]
    outf.write(("%s pairs ") % (inst))
    for N in Nlist:
        outf.write(' & %2d' % len([EXPECTo[k] for k in KEYS if k[1] == N and CPUo[k]<3600 and NEDGESo[k]>0]))
        outf.write(' & %8g' % avg([EXPECTo[k] for k in KEYS if k[1] == N and CPUo[k]<3600 and NEDGESo[k]>0]))
        outf.write(' & %8g' % avg([EXPECTg[k] for k in KEYS if k[1] == N and CPUo[k]<3600 and NEDGESo[k]>0]))
    outf.write(r" \\" + "\n")
outf.write("total")
for N in Nlist:
    outf.write(' & %2d' % len([EXPECTo[k] for k in EXPECTo if k[1] == N and CPUo[k]<3600 and NEDGESo[k]>0]))
    outf.write(' & %8g' % avg([EXPECTo[k] for k in EXPECTo if k[1] == N and CPUo[k]<3600 and NEDGESo[k]>0]))
    outf.write(' & %8g' % avg([EXPECTg[k] for k in EXPECTo if k[1] == N and CPUo[k]<3600 and NEDGESo[k]>0]))
outf.write(r" \\" + "\n")

# !!!!!!!!!!!!!!!!!!!!
outf.write("\ninstances solved for all Ns\n")
outf.write("Instances & Number")
for N in Nlist:
    outf.write(" & \\multicolumn{2}{c}{N=%s}" % Nlabel[N])
outf.write(r" \\" + "\n")
for N in Nlist:
    for inst in SIZES:
        KEYS = [k for k in CPUo if k[0] == inst]
        SEQS = list((set(k[-1] for k in KEYS if k[1] == Nlist[-1] and CPUo[k]<3600 and NEDGESo[k]>0)))
        outf.write(' & %8g' % avg([EXPECTo[k] for k in KEYS if k[1] == N and k[-1] in SEQS]))
        outf.write(' & %8g' % avg([EXPECTg[k] for k in KEYS if k[1] == N and k[-1] in SEQS]))
        outf.write(r" \\" + "\n")
# !!!!!!!!!!!!!!!

outf.write("\ninstances solved for all Ns\n")
outf.write("Instances & Number")
for N in Nlist:
    outf.write(" & \\multicolumn{2}{c}{N=%s}" % Nlabel[N])
outf.write(r" \\" + "\n")
for inst in SIZES:
    KEYS = [k for k in CPUo if k[0] == inst]
    SEQS = list((set(k[-1] for k in KEYS if k[1] == Nlist[-1] and CPUo[k]<3600 and NEDGESo[k]>0)))
    outf.write((f"{inst} pairs & {len(SEQS):2}"))
    for N in Nlist:
        outf.write(' & %8g' % avg([EXPECTo[k] for k in KEYS if k[1] == N and k[-1] in SEQS]))
        outf.write(' & %8g' % avg([EXPECTg[k] for k in KEYS if k[1] == N and k[-1] in SEQS]))
    outf.write(r" \\" + "\n")

outf.write("\ncheck that sum of failures and successes match number of instances\n")
for N in Nlist[0:1]:
    for inst in SIZES[0:1]:
        KEYS = [k for k in CPUo if k[0] == inst]
        SEQS = list((set(k[-1] for k in KEYS if k[1] == Nlist[-1] and NEDGESo[k] <= 0)))
        print(0, len(SEQS), SEQS)
        SEQS = list((set(k[-1] for k in KEYS if k[1] == Nlist[-1] and CPUo[k] < 3600 and NEDGESo[k] > 0)))
        print("X", len(SEQS), SEQS)
        print(N, inst, NSUCCESSo[inst, N], NFAILSo[inst, N], len([k for k in KEYS if k[-1] in SEQS]))
        assert NSUCCESSo[inst, N] + NFAILSo[inst, N] == 50


outf.write("\nsome info about gaps\n")
nzg, zg = {N:0 for N in Nlist}, {N:0 for N in Nlist}
objs,grds,gaps = {N:[] for N in Nlist},{N:[] for N in Nlist},{N:[] for N in Nlist}
for N in Nlist:
    for (inst, n, nvert, nedges, seq) in EXPECTo:
        key = (inst, n, nvert, nedges, seq)
        if CPUo[key]>3600 or NEDGESo[key]==0:
            continue
        if n == N :
            obj = EXPECTo[key]
            grd = EXPECTg[key]
            print(f"{key}\t{obj}\t{grd}")
            err = 100 * (1 - grd / obj)
            err = err if err > 1.e-12 else 0
            objs[N].append(obj)
            grds[N].append(grd)
            gaps[N].append(err)
            if err > 1.e-12:
                nzg[N] += 1
            else:
                zg[N] += 1

# write processed output as latex text
outf = sys.stdout   # open("nnodes.tex", "w")
outf.write("Gaps for Xenia's instances\n")
outf.write("Observations\t& \\#\t& Exact\t& Greedy\t& Mean Gap(\\%)\t& Max Gap(\\%)\t& Non-zero Gaps\t")
outf.write(r"\\" + "\n")
for N in Nlist:
    outf.write(f"N={Nlabel[N]}\t& {nzg[N]+zg[N]}\t& {avg(objs[N])}\t & {avg(grds[N])}\t & {avg(gaps[N])}\t & {max(gaps[N])}\t & {nzg[N]}/{zg[N]}\t")
    outf.write(r"\\" + "\n")
