from TableUtils import VTTable
import sys

#basepath='/Users/pvaut/Documents/Data/PfGeneticBarcodes'
basepath='/home/pvaut/Documents/Genome/PfGeneticBarcodes'

#def convertdashtoabsent(x):
#    return 33
#    if x=='-':
#        return 0
#    else:
#        return 2




tb = VTTable.VTTable()

def ImportData():
    tb0 = VTTable.VTTable()
    tb0.LoadXls(basepath+'/SurfinsForPV.xlsx','less than 3')
    tb0.SaveFile(basepath+'/snpset1.txt')
    tb0.PrintRows(0,10)


def LoadData(tb):
    tb.LoadFile(basepath+'/snpset1.txt')
    tb.RenameCol('SnpName','Sample')
    #tb.PrintRows(0,20)

    # Merge in other sample information
    infotb = VTTable.VTTable()
    infotb.LoadXls(basepath+'/Processed_metadata-2.1.xlsx','2.1')
    infotb.DropCol('Country')
    infotb.DropCol('Fws')
    infotb.DropCol('SiteInfoSource')
    infotb.DropCol('Site')
    infotb.DropCol('LabSample')
    infotb.DropCol('LowTypability')
    infotb.DropCol('PcaOutlier')
    infotb.DropCol('IsDuplicate')
    infotb.DropCol('ManualExlusion')
    infotb.DropCol('Typability')
    infotb.DropCol('UsedInSnpDiscovery')
    infotb.DropCol('Notes')
    #infotb.PrintRows(0, 20)
    tb2 = VTTable.VTTable()
    tb2.MergeTablesByKeyFrom(tb,infotb,'Sample',True,False)
    tb=tb2
    #tb1.PrintRows(0, 20)
    #sys.exit()



    # Determine groups of snps
    snpcols=[]
    snpgroups=[]
    maxdist = 20000
    lastchromname = ''
    lastposit = -1e9
    idx = 0
    for colnr in range(tb.GetColCount()):
        colname = tb.GetColName(colnr)
        if colname[0:3] == 'MAL':
            snpcols.append(colnr)
            chromname = colname.split(':')[0]
            posit=int(colname.split(':')[1])
            if (chromname != lastchromname) or (posit > lastposit+maxdist):
                idx += 1
                snpgroups.append({ 'name': 'grp'+str(idx), 'snps': [], 'codes':{}, 'codecount':0 })
            snpgroups[len(snpgroups)-1]['snps'].append(colnr)
            lastchromname = chromname
            lastposit = posit
            #print(chromname+str(posit))


    print('###########################################\nSNP COLS: '+str(snpcols)+"\n###############################")
    print('###########################################\nSNP GROUPS: '+str(snpgroups)+"\n###############################")



def CalcBarcodes():
    for snpgroup in snpgroups:
        tb.AddColumn(VTTable.VTColumn(snpgroup['name'],'Value'))
        tb.FillColumn(snpgroup['name'],None)
    for rownr in tb.GetRowNrRange():
        key=tb.GetValue(rownr,0)
        print('KEY='+key)
        if len(key)>0:
            for snpgroup in snpgroups:
                isComplete = True
                code =''
                for snpColNr in snpgroup['snps']:
                    vl=tb.GetValue(rownr,snpColNr)
                    if vl==0: isComplete = False
                    code += str(int(float(vl)))
                if isComplete:
                    if code not in snpgroup['codes']:
                        snpgroup['codecount'] += 1
                        snpgroup['codes'][code] = snpgroup['codecount']
                    codenr = snpgroup['codes'][code]
                    print(code+' '+str(codenr))
                    tb.SetValue(rownr,tb.GetColNr(snpgroup['name']),codenr)

    tb.PrintRows(0,20)
    tb.SaveFile(basepath+'/result.txt')


def CalcSimilarCount():
    sampleSnpVals=[]
    for rownr in tb.GetRowNrRange():
        sampleSnpVals.append( [ tb.GetValue(rownr,snpColNr) for snpColNr in snpcols ] )
    snprange=range(len(snpcols))
    sampleDistances = []
    for rownr1 in tb.GetRowNrRange():
        print(str(rownr1))
        snps1 = sampleSnpVals[rownr1]
        dists= []
        for rownr2 in tb.GetRowNrRange():
            snps2 = sampleSnpVals[rownr2]
            dst = 0
            for i in snprange:
                if snps1[i] != snps2[i]:
                    dst += 1
            dists.append(dst)
        sampleDistances.append(dists)

    for maxdist in range(maxmaxdist):
        colName = 'DistCount_'+str(maxdist)
        tb.AddColumn(VTTable.VTColumn(colName,'Value'))
        colNr = tb.GetColNr(colName)
        tb.FillColumn(colName,None)
        for rownr1 in tb.GetRowNrRange():
            print(str(rownr1))
            dists = sampleDistances[rownr1]
            cnt =0
            for rownr2 in tb.GetRowNrRange():
                if dists[rownr2] <= maxdist:
                    cnt += 1
            tb.SetValue(rownr1, colNr, cnt)

    # Remove snp columns
    snpcolnames = [tb.GetColName(colnr) for colnr in snpcols]
    for colname in snpcolnames:
        tb.DropCol(colname)
    tb.PrintRows(0, 200000)
    tb.SaveFile(basepath+'/SimilarCount.txt')


def CreateAggregatedSimilarCount():
    tb = VTTable.VTTable()
    tb.LoadFile(basepath+'/SimilarCount.txt')
    tb.PrintRows(0, 20)

    sites = VTTable.VTTable()
    sites.allColumnsText = True
    sites.LoadFile(basepath+'/sites.txt')
    sites.DropCol('GeoCode')
    sites.DropCol('Country')
    sites.DropCol('SubCont')
    sites.ConvertColToValue('Latitude')
    sites.ConvertColToValue('Longitude')

    tbres = VTTable.VTTable()
    tbres.AddColumn(VTTable.VTColumn('ID', 'Text'))
    tbres.FillColumn('ID',None)
    tbres.AddColumn(VTTable.VTColumn('MaxDist', 'Value'))
    tbres.FillColumn('MaxDist',None)
    tbres.AddColumn(VTTable.VTColumn('ClusterSize', 'Value'))
    tbres.FillColumn('ClusterSize',None)
    tbres.AddColumn(VTTable.VTColumn('ClusterMemberCount', 'Value'))
    tbres.FillColumn('ClusterMemberCount',None)

    print('====== sites ============')
    sites.PrintRows(0, 20)


    for rownr in sites.GetRowNrRange():
        sitecode = sites.GetValue(rownr,sites.GetColNr('ID'))
        for maxdist in range(maxmaxdist):
            distcolname='DistCount_'+str(maxdist)

            clustercount=[0 for i in range(10000)]
            for samplenr in tb.GetRowNrRange():
                if tb.GetValue(samplenr,tb.GetColNr('SiteCode'))  == sitecode:
                    clustersize=int(tb.GetValue(samplenr,tb.GetColNr(distcolname)))
                    clustercount[clustersize] += 1
            for k in range(len(clustercount)):
                if clustercount[k]>0:
                    tbres.AddRowEmpty()
                    resrownr = tbres.GetRowCount() - 1
                    tbres.SetValue(resrownr,tbres.GetColNr('ID'),sitecode)
                    tbres.SetValue(resrownr,tbres.GetColNr('MaxDist'),maxdist)
                    tbres.SetValue(resrownr,tbres.GetColNr('ClusterSize'),k)
                    tbres.SetValue(resrownr,tbres.GetColNr('ClusterMemberCount'),clustercount[k])
    tbres.PrintRows(0,20)
    tbres.SaveFile(basepath+'/clustermembercount.txt')
    tbres.SaveSQLCreation(basepath+'/clustermembercount_create.sql','clustermembercount')
    tbres.SaveSQLDump(basepath+'/clustermembercount_data.sql','clustermembercount')

    sites.SaveFile(basepath+'/clustersites.txt')
    sites.SaveSQLCreation(basepath+'/clustersites_create.sql','clustersites')
    sites.SaveSQLDump(basepath+'/clustersites_data.sql','clustersites')


maxmaxdist = 5

#LoadData(tb)
#CalcSimilarCount();

CreateAggregatedSimilarCount()

if False:
    import matplotlib.pyplot as plt
    plt.plot([0,1,2,3],[0,2,3,1])
    plt.ylabel('some numbers')
    fig = plt.gcf()
    circ = plt.Circle((1,1), radius=0.1, color='g')
    fig.gca().add_artist(circ)
    plt.show()
