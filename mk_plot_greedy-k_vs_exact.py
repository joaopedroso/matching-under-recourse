import sys
import subprocess
import os.path
import csv
import matplotlib.pyplot as plt
avg = lambda v : sum(v)/len(v)

Nlist = ["0","1","2","3","999999"]
Nlabel = {"0":"1", "1":"2", "2":"3", "3":"4", "999999":r"$\infty$"}
SIZES = [100]

filename = "RESULTS/delorme-50_summary_solve.csv"
NINST = 30
INST, NEDGES, NVERT, EXPECTo, CPU, CACHE = {}, {}, {}, {}, {}, {}
with open(filename) as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    for row in reader:
        inst,N,nvert,nedges,expect,cpu,ncache,_ = row
        assert N in Nlist
        inst = inst[inst.rfind("_")+1:inst.find(".input")]
        seq = int(inst)
        nvert = int(nvert)
        nedges = int(nedges)
        key = (N,nvert,nedges,seq)
        INST[key] = int(inst)
        if cpu == "None":  # in some legacy experiments...
            cpu = 3600
        CPU[key] = min(3600, float(cpu))
        NEDGES[key] = int(nedges)
        NVERT[key] = int(nvert)
        EXPECTo[key] = float(expect)

filename = "RESULTS/delorme-50_summary_greedy-k.csv"
NINST = 30
INST, NEDGES, NVERT, EXPECTg, CPU, CACHE = {}, {}, {}, {}, {}, {}
with open(filename) as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    for row in reader:
        inst,N,nvert,nedges,expect,cpu,ncache,_ = row
        assert N in Nlist
        inst = inst[inst.rfind("_")+1:inst.find(".input")]
        seq = int(inst)
        nvert = int(nvert)
        nedges = int(nedges)
        key = (N,nvert,nedges,seq)
        INST[key] = int(inst)
        if cpu == "None":  # in some legacy experiments...
            cpu = 3600
        CPU[key] = min(3600, float(cpu))
        NEDGES[key] = int(nedges)
        NVERT[key] = int(nvert)
        EXPECTg[key] = float(expect)

# for k in EXPECTo:
#     print(k,EXPECTo[k])

for N in Nlist:
    vert = sorted(set([nvert for (n, nvert, nedges, seq) in EXPECTo if n == N]))
    nelem = 0
    for v in vert:
        E = [EXPECTo[N, v, nedges, seq] for (n, nvert, nedges, seq) in EXPECTo if n == N and nvert == v]
        nelem += len(E)
    assert nelem == NINST

for N in Nlist:
    assert vert == sorted(set([nvert for (n, nvert, nedges, seq) in EXPECTg if n == N]))
    nelem = 0
    for v in vert:
        E = [EXPECTg[N, v, nedges, seq] for (n, nvert, nedges, seq) in EXPECTg if n == N and nvert == v]
        nelem += len(E)
    assert nelem == NINST

# for v in V:
#     print(f"{v}", end="\t")
#     for N in Nlist:
#         opt = avg([EXPECTo[N, v, nedges, seq] for (n, nvert, nedges, seq) in EXPECTg if n == N and nvert == v])
#         grd = avg([EXPECTg[N, v, nedges, seq] for (n, nvert, nedges, seq) in EXPECTg if n == N and nvert == v])
#         print(f"{100*(1-grd/opt):g}", end="\t")
#     print()

x,y = {},{}
for N in Nlist:
    nedg = sorted(set([nedges for (n, nvert, nedges, seq) in EXPECTo if n == N]))
    y[N] = []
x = list(nedg)
xs = {N:[] for N in Nlist}   # for scatter plot
ys = {N:[] for e in nedg for N in Nlist}
for e in nedg:
    print(f"-------------------{e}", end="\n")
    for N in Nlist:
        errs = []
        for (n, nvert, nedges, seq) in EXPECTg:
            if n == N and nedges == e:
                opt = EXPECTo[N, nvert, e, seq]
                grd = EXPECTg[N, nvert, e, seq]
                err = 100 * (1 - grd / opt)
                xs[N].append(e)
                ys[N].append(err)
                errs.append(err)
        y[N].append(avg(errs))
        print(e,N,ys[N],y[N][-1])
        print(f"{y[N]}", end="\n")
    print()



output = "err_greedy_delorme.pdf"
title = ["Greedy loss in terms of the number of vertices", "Greedy loss in terms of the number of edges"]
ylabel = [f"N = {Nlabel[N]}" for N in Nlist]
xlabel = ["number of vertices", "number of edges"]
logy = False

fig, ax = plt.subplots(1, 1, sharex='col', sharey='row', figsize=(7,5))
line = {}
colors = ['#525252', '#88419d', '#2b8cbe', '#d7301f', '#238b45']
markers = ['1', '2', '3', '4', '.']
for i,N in enumerate(Nlist):
    label = f"{Nlabel[N]}"
    ax.scatter(x=xs[N], y=ys[N], alpha=0.8, color=colors[i], marker = markers[i])
    # line[v] = ax.scatter(x=x, y=y[N], s=100, label=label, alpha=0.5, marker = 'x', cmap='gray')
    ax.plot(x, y[N], alpha=0.7, linewidth=5, color=colors[i], label=label) # , s=100, label=label, alpha=0.5, marker='x', cmap='gray')
    ax.grid(color='gray', linestyle='-', linewidth=0.5, alpha=0.2)

ax.set_ylim(ymax=105)
ax.set_ylabel("Greedy % error", size=10)
ax.set_xlabel("Number of edges in instance", size=10)

# plt.set_title(title, size=7)
# plt.legend(title='Instance sizes', handles=[line[l] for l in sorted(line)], loc=4, fontsize=8)
plt.legend(loc=2, fontsize=8)

if output:
    plt.savefig(output)
else:
    plt.show()

# write processed output as latex text
outf = sys.stdout   # open("nnodes.tex", "w")
outf.write("Delorme 50-node instances\n")
outf.write("Observations\t& Error")
outf.write(r"\\" + "\n")
for N in Nlist:
    outf.write(f"N={Nlabel[N]}\t& {avg(y[N])}\t")
    outf.write(r"\\" + "\n")

