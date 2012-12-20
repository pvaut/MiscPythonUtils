


popnames=['YRI','Malawi','Mandinka','Wolof','Fula','Jola','Akan','Northerner']

basepath="C:/Data/Articles/PositiveSelection/DataSaturn"


f_ihs = open(basepath+"/IHS/_PV_IHSwindowed_Summary.txt")
f_xp = open(basepath+"/XPEHH/_PV_XPEHHwindowed_Summary.txt")

f2 = open(basepath+"/_PV_TopWindows.txt",'w')
f2.write("IHS\tXPEHH\tChromo\tStartWin\EndWin\n")

header=f_ihs.readline()
header=f_xp.readline()
for line_ihs in f_ihs:
    line_ihs=line_ihs.rstrip('\r\n')
    cells_ihs=line_ihs.split("\t")
    
    line_xp=f_xp.readline()
    line_xp=line_xp.rstrip('\r\n')
    cells_xp=line_xp.split("\t")
    
    ok_ihs=True
    for popnr in range(0,len(popnames)):
        if (float(cells_ihs[3+popnr])>0.01):
            ok_ihs=False

    ok_xp=True
    for popnr in range(0,len(popnames)):
        if (float(cells_xp[3+popnr])>0.01):
            ok_xp=False

    if (ok_ihs or ok_xp):
        f2.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(ok_ihs,ok_xp,cells_ihs[0],cells_ihs[1],cells_ihs[2]))
f_ihs.close()
f_xp.close()
f2.close()

print('done!')