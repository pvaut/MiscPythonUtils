import copy
import sys
import gc
from TableUtils import VTTable
from TableUtils import IntervalTools


popnamelist=['Akan','Fula','Jola','Malawi','Mandinka','Northerner','Wolof','YRI']



basepath="C:/Data/Articles/PositiveSelection"


##Load Kerrins top window B36 data
#KerrinB36TopWindows=VTTable.VTTable()
#KerrinB36TopWindows.LoadFile(basepath+"/DataSaturn/Summary/TopWindowsBuild36.txt")
#
#def RemoveSurroundings(st): return(st[2:-2].replace(',',''))
#KerrinB36TopWindows.MapCol('WindowStart',RemoveSurroundings)
#KerrinB36TopWindows.ConvertColToValue('WindowStart')
#KerrinB36TopWindows.MapCol('WindowEnd',RemoveSurroundings)
#KerrinB36TopWindows.ConvertColToValue('WindowEnd')
#
#KerrinB36TopWindows.RenameCol('Test', 'test')
#KerrinB36TopWindows.RenameCol('Chr', 'chromosome')
#KerrinB36TopWindows.RenameCol('WindowStart', 'start')
#KerrinB36TopWindows.RenameCol('WindowEnd', 'stop')
#
#for colname in KerrinB36TopWindows.GetColList():
#    KerrinB36TopWindows.RenameCol(colname,'KR_'+colname)
#
#KerrinB36TopWindows.MergeColsToString("WinKey","{0}_{1}_{2}",'KR_test','KR_chromosome','KR_start')
#KerrinB36TopWindows.MoveCol('WinKey',0)
#
#print('****** KERRIN B36 TOP WINDOWS *********')
#KerrinB36TopWindows.PrintRows(0,10)

#Loading gene data
genelist=VTTable.VTTable()
#genelist.LoadFile(basepath+"/DataKeposeda/Build36/genes.csv")
#genelist.MapCol('chromosome',lambda val: val[1:-1])
#genelist.MapCol('name',lambda val: val[1:-1])
#genelist.MapCol('ensembl_id',lambda val: val[1:-1])
#genelist=genelist.SortValuesReturn('start')
#genelist=genelist.SortValuesReturn('chromosome')
#genelist.PrintRows(0,100)
#sys.exit()

genelist.LoadFile(basepath+"/DataKeposeda/Build36/Genes_UCSC_Build36.txt")
genelist.DropCol('hg18.knownGene.name')
genelist.DropCol('hg18.knownGene.cdsStart')
genelist.DropCol('hg18.knownGene.cdsEnd')
genelist.MapCol('hg18.knownGene.chrom',lambda val: val[3:99999])
genelist=genelist.SortValuesReturn('hg18.knownGene.txStart')
genelist=genelist.SortValuesReturn('hg18.knownGene.chrom')
genelist.PrintRows(0,10)
#sys.exit()


            

#create overlap finders
ChromoOverlapFinders={}
for genenr in range(0,genelist.GetRowCount()):
    chromostr=genelist.GetValue(genenr,0)
    if not(chromostr in ChromoOverlapFinders):
        ChromoOverlapFinders[chromostr]=IntervalTools.IntervalOverlapFinder()
    genestart=genelist.GetValue(genenr,1)
    genestop=genelist.GetValue(genenr,2)
    ChromoOverlapFinders[chromostr].AddInterval(genestart,genestop,genelist.GetValue(genenr,3))


#Load Keposeda B36 all window data
KSB36Windows=VTTable.VTTable()
KSB36Windows.LoadFile(basepath+"/DataKeposeda/Build36/windows_query.tab")
KSB36Windows=KSB36Windows.SortValuesReturn('start')
KSB36Windows=KSB36Windows.SortValuesReturn('chromosome')
KSB36Windows.ConvertColToString('chromosome')
KSB36Windows.MapCol('chromosome',lambda val: val[0:len(val)-2])

#Determine overlap genes
print('Start determining overlap genes')
#KSB36Windows.DropCol('Genes')
#KSB36Windows.DropCol('IntersectionGenes')
#KSB36Windows.DropCol('150IntersectionGenes')
KSB36Windows.AddColumn(VTTable.VTColumn('OverlapGenes','Text'))
KSB36Windows.FillColumn('OverlapGenes','-')
mygenecolnr=KSB36Windows.GetColNr('OverlapGenes')
for winnr in range(0,KSB36Windows.GetRowCount()):
    winchromo=KSB36Windows.GetValue(winnr,0)
    winstart=KSB36Windows.GetValue(winnr,1)
    winstop=KSB36Windows.GetValue(winnr,2)
    overlaplist2=ChromoOverlapFinders[winchromo].FindOverlapsFast(winstart,winstop)
    overlaplist2.reverse()
    overlaplist2=set(overlaplist2)
    sorted(overlaplist2)
    overlaplist2str=', '.join(overlaplist2)
    KSB36Windows.SetValue(winnr,mygenecolnr,overlaplist2str)
print('Finished determining overlap genes '+str(KSB36Windows.GetRowCount()))
    
KSB36Windows.PrintRows(0,10)
KSB36Windows.SaveFile(basepath+"/DataKeposeda/Build36/FinalWindowData.txt")


# Create top top list of windows
# definition: windows that have for one or both of the tests either
#    all 8 populations rank <=0.01
#    [7 populations rank <=1 and 1 population missing data] currently not used

KSB36Windows.AddColumn(VTTable.VTColumn('IHSTopRank','Text'))
KSB36Windows.FillColumn('IHSTopRank','-')
KSB36Windows.AddColumn(VTTable.VTColumn('XPEHHTopRank','Text'))
KSB36Windows.FillColumn('XPEHHTopRank','-')
KSB36Windows.MoveCol('IHSTopRank', 3)
KSB36Windows.MoveCol('XPEHHTopRank', 4)
KSB36Windows.PrintRows(0,10)

def toptopfilterfunc(*vals):
    successcount=0
    missingcount=0
    for val in vals:
        if (val==None): missingcount+=1
        else:
            if val<=0.01: successcount+=1
    return( (successcount+missingcount==8)) and (successcount>0)# or ((successcount==7)and(missingcount==1)) )


lst_ihs=["IHS "+popname for popname in popnamelist]
lst_xpehh=["XPEHH "+popname+" vs CEU" for popname in popnamelist]
toptoplist_ihs=KSB36Windows.FilterByFunctionReturn(toptopfilterfunc,*lst_ihs)
toptoplist_ihs.FillColumn('IHSTopRank','YES')
toptoplist_xpehh=KSB36Windows.FilterByFunctionReturn(toptopfilterfunc,*lst_xpehh)
toptoplist_xpehh.FillColumn('XPEHHTopRank','YES')

toptoplist=VTTable.VTTable()
toptoplist.CopyFrom(toptoplist_ihs)
toptoplist.Append(toptoplist_xpehh)

toptoplist.PrintInfo()
toptoplist.PrintRows(0,99999)
toptoplist.SaveFile(basepath+"/DataKeposeda/Build36/toptoplist.txt")