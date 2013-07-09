from TableUtils import VTTable
import sys

basepath='/Users/pvaut/Documents/Data/PfGeneticBarcodes'

tb = VTTable.VTTable()

#tb.LoadXls(basepath+'/SurfinsForPV.xlsx','less than 3')
#tb.SaveFile(basepath+'/snpset1.txt')
#tb.PrintRows(0,10)

tb.LoadFile(basepath+'/snpset1.txt')
#tb.PrintInfo()
tb.PrintRows(0,10)

# Determine groups of snps
snpgroups=[]
maxdist = 20000
lastchromname = ''
lastposit = -1e9
for colnr in range(tb.GetColCount()):
    colname = tb.GetColName(colnr)
    if colname[0:3] == 'MAL':
        chromname = colname.split(':')[0]
        posit=int(colname.split(':')[1])
        if (chromname != lastchromname) or (posit > lastposit+maxdist):
            snpgroups.append([])
        snpgroups[len(snpgroups)-1].append(colnr)
        lastchromname = chromname
        lastposit = posit
        #print(chromname+str(posit))
print(str(snpgroups))


if False:
    import matplotlib.pyplot as plt
    plt.plot([0,1,2,3],[0,2,3,1])
    plt.ylabel('some numbers')
    fig = plt.gcf()
    circ = plt.Circle((1,1), radius=0.1, color='g')
    fig.gca().add_artist(circ)
    plt.show()
