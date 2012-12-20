import copy
import sys
import gc
from TableUtils import VTTable
from TableUtils import IntervalTools

popnamelist=['Akan','Fula','Jola','Malawi','Mandinka','Northerner','Wolof','YRI']
basepath="C:/Data/Articles/PositiveSelection"


def CreateWindowOverlapGenes(wintable):
    genelist=VTTable.VTTable()
    genelist.LoadFile(basepath+"/DataKeposeda/Build36/Genes_UCSC_Build36.txt")
    genelist.DropCol('hg18.knownGene.name')
    genelist.DropCol('hg18.knownGene.cdsStart')
    genelist.DropCol('hg18.knownGene.cdsEnd')
    genelist.MapCol('hg18.knownGene.chrom',lambda val: val[3:99999])
    genelist=genelist.SortValuesReturn('hg18.knownGene.txStart')
    genelist=genelist.SortValuesReturn('hg18.knownGene.chrom')
    print("************ GENE LIST ************")
    genelist.PrintRows(0,10)
    
    #create overlap finders
    ChromoOverlapFinders={}
    for genenr in range(0,genelist.GetRowCount()):
        chromostr=genelist.GetValue(genenr,0)
        if not(chromostr in ChromoOverlapFinders):
            ChromoOverlapFinders[chromostr]=IntervalTools.IntervalOverlapFinder()
        genestart=genelist.GetValue(genenr,1)
        genestop=genelist.GetValue(genenr,2)
        ChromoOverlapFinders[chromostr].AddInterval(genestart,genestop,genelist.GetValue(genenr,3))
    
    #Determine overlap genes
    print('Start determining overlap genes')
    wintable.AddColumn(VTTable.VTColumn('overlapgenes','Text'))
    wintable.FillColumn('overlapgenes','-')
    mygenecolnr=wintable.GetColNr('overlapgenes')
    mychromocolnr=wintable.GetColNr('chrom')
    mycentercolnr=wintable.GetColNr('pos')
    mysizecolnr=wintable.GetColNr('winsize')
    for winnr in range(0,wintable.GetRowCount()):
        winchromo=str(int(wintable.GetValue(winnr,mychromocolnr)))
        wincenter=wintable.GetValue(winnr,mycentercolnr)
        winsize=wintable.GetValue(winnr,mysizecolnr)
        winstart=wincenter-winsize/2
        winstop=wincenter+winsize/2
        overlaplist2=ChromoOverlapFinders[winchromo].FindOverlapsFast(winstart,winstop)
        overlaplist2.reverse()
        overlaplist2=set(overlaplist2)
        sorted(overlaplist2)
        overlaplist2str=', '.join(overlaplist2)
        wintable.SetValue(winnr,mygenecolnr,overlaplist2str)
    print("************ WINDOWS WITH OVERLAP GENES ************")
    wintable.PrintRows(0,10)




def AdaptWindows():
    inputfilename=basepath+"/DataKeposedaMySQL/windows_b36.tab"
    outputfilename=basepath+"/DataKeposedaMySQL/WindowTable.txt"
    
    wins_orig=VTTable.VTTable()
    wins_orig.LoadFile(inputfilename)
    
    wins_orig.DropCol("__id")
    wins_orig.RenameCol('chromosome','chrom')
    for popname in popnamelist:
        wins_orig.RenameCol("{0}_vs_CEU_XPEHH".format(popname),'WXPEHH_{0}'.format(popname))    
        wins_orig.RenameCol("{0}_IHS".format(popname),'WIHS_{0}'.format(popname))
        
    colnr_start=wins_orig.GetColNr('start')
    colnr_stop=wins_orig.GetColNr('stop')
    wins_orig.AddColumn(VTTable.VTColumn("pos","Value"))  
    wins_orig.FillColumn("pos",0)
    colnr_pos=wins_orig.GetColNr('pos')
    wins_orig.AddColumn(VTTable.VTColumn("winsize","Value"))  
    wins_orig.FillColumn("winsize",0)
    colnr_size=wins_orig.GetColNr('winsize')
    for rownr in wins_orig.GetRowNrRange():
        ps1=wins_orig.GetValue(rownr,colnr_start)
        ps2=wins_orig.GetValue(rownr,colnr_stop)
        wins_orig.SetValue(rownr,colnr_pos,round((ps1+ps2)/2.0))
        wins_orig.SetValue(rownr,colnr_size,ps2-ps1)
    wins_orig.DropCol("start")
    wins_orig.DropCol("stop")

    
    colpos=0
    wins_orig.MoveCol('chrom',colpos);colpos+=1   
    wins_orig.MoveCol('pos',colpos);colpos+=1   
    wins_orig.MoveCol('winsize',colpos);colpos+=1   
    for popname in popnamelist:
        wins_orig.MoveCol('WIHS_{0}'.format(popname),colpos);colpos+=1
    for popname in popnamelist:
        wins_orig.MoveCol('WXPEHH_{0}'.format(popname),colpos);colpos+=1
        
    #Merge with overlap genes
    CreateWindowOverlapGenes(wins_orig)
    
    #Count number of populations in top 1%
    wins_orig.AddColumn(VTTable.VTColumn("IHSTop1","Value"))  
    wins_orig.FillColumn("IHSTop1",0)
    colnrtop1ihs=wins_orig.GetColNr("IHSTop1")
    wins_orig.AddColumn(VTTable.VTColumn("XPEHHTop1","Value"))  
    wins_orig.FillColumn("XPEHHTop1",0)
    colnrtop1xpehh=wins_orig.GetColNr("XPEHHTop1")
    for rownr in wins_orig.GetRowNrRange():
        ct=0;
        for popname in popnamelist:
            vl=wins_orig.GetValue(rownr,wins_orig.GetColNr('WIHS_{0}'.format(popname)))
            if (vl is not None) and (vl<=0.01): ct+=1
        wins_orig.SetValue(rownr, colnrtop1ihs, ct)
        ct=0;
        for popname in popnamelist:
            vl=wins_orig.GetValue(rownr,wins_orig.GetColNr('WXPEHH_{0}'.format(popname)))
            if (vl is not None) and (vl<=0.01): ct+=1
        wins_orig.SetValue(rownr, colnrtop1xpehh, ct)

                                  
    
    print("\n\n\n\n================= AFTER ====================")        
    wins_orig.PrintRows(0,10)
    
    wins_orig.SaveFile(outputfilename,saveheader=False, absentvaluestring='\\N')
    
    #Create a starting point for the SQL statement that is going to create the table
    f=open(basepath+"/DataKeposedaMySQL/ImportWindows.sql",'w')
    f.write('USE world;\n')
    f.write('DROP TABLE IF EXISTS windows;\n')
    f.write('CREATE TABLE windows (\n')
    for colname in wins_orig.GetColList():
        datatype="DOUBLE"
        if (colname=='chrom') or (colname=='pos') or (colname=='winsize'): datatype="INT"
        if (colname=='overlapgenes'): datatype="VARCHAR(2000)"
        f.write('    {0} {1},\n'.format(colname,datatype))
    f.write(');\n')
    
    f.write("LOAD DATA INFILE '{0}'\n".format(outputfilename))
    f.write("    INTO TABLE windows\n")
    f.write("    FIELDS TERMINATED BY '\\t'\n")
    f.write("    LINES TERMINATED BY '\\n'\n")
    f.write("    ;\n")
    
    f.write("CREATE INDEX wn_chrom on windows (chrom);\n")
    f.write("CREATE INDEX wn_pos on windows (pos);\n")
    
    
    f.close()
    
            
    print("================= DONE ====================")    
    
AdaptWindows()





















def AdaptSnps():
    inputfilename=basepath+"/DataKeposedaMySQL/snps_b36.tab"
    outputfilename=basepath+"/DataKeposedaMySQL/SnpTable.txt"
    
    snps_orig=VTTable.VTTable()
    snps_orig.LoadFile(inputfilename)
    snps_orig.PrintRows(0,100)
    
    
    #Merge forward & backward xpehh values, taking the one with the largest absolute value
    for popname in popnamelist:
        colname1="XPEHH_fwd_{0}_vs_CEU".format(popname)
        colname2="XPEHH_back_{0}_vs_CEU".format(popname)
        colnr1=snps_orig.GetColNr(colname1)
        colnr2=snps_orig.GetColNr(colname2)
        for rownr in snps_orig.GetRowNrRange():
            val=None
            val1=snps_orig.GetValue(rownr, colnr1)
            val2=snps_orig.GetValue(rownr, colnr2)
            if val1 is not None:
                if (val is None) or (abs(val1)>abs(val)): val=val1        
            if val2 is not None:
                if (val is None) or (abs(val2)>abs(val)): val=val2
            snps_orig.SetValue(rownr,colnr1,val)
        snps_orig.DropCol(colname2)   
        snps_orig.RenameCol(colname1,'XPEHH_{0}'.format(popname))    
    
    
    #rearrange columns & rename some columns 
    snps_orig.DropCol("__id")
    snps_orig.RenameCol('chromosome','chrom')   
    snps_orig.RenameCol('coordinates','pos')
    snps_orig.RenameCol('AncestralAllele','ancallele')   
    snps_orig.RenameCol('snp','snpid')
    colpos=0
    snps_orig.MoveCol('chrom',colpos);colpos+=1   
    snps_orig.MoveCol('pos',colpos);colpos+=1   
    snps_orig.MoveCol('snpid',colpos);colpos+=1   
    snps_orig.MoveCol('allele1',colpos);colpos+=1   
    snps_orig.MoveCol('allele2',colpos);colpos+=1   
    snps_orig.MoveCol('ancallele',colpos);colpos+=1
    for popname in popnamelist:
        snps_orig.MoveCol('Freq_{0}'.format(popname),colpos);colpos+=1
    for popname in popnamelist:
        snps_orig.MoveCol('IHS_{0}'.format(popname),colpos);colpos+=1
    for popname in popnamelist:
        snps_orig.MoveCol('XPEHH_{0}'.format(popname),colpos);colpos+=1
        
        
    ################## Merge ancestral allele information ##################
    ref_ancest=VTTable.VTTable()
    ref_ancest.LoadFile(basepath+"/DataKeposedaMySQL/PV_AncestralAlleles.txt")
    ref_snpdct=ref_ancest.BuildColDict("SNP",False)
    ref_ancallelcolnr=ref_ancest.GetColNr('AncestralAllele')
    
    data_snpcolnr=snps_orig.GetColNr('snpid')
    data_ancallcolnr=snps_orig.GetColNr('ancallele')
    for rownr in snps_orig.GetRowNrRange():
        state='-'
        snpid=snps_orig.GetValue(rownr,data_snpcolnr)
        if snpid in ref_snpdct:
            state=ref_ancest.GetValue(ref_snpdct[snpid],ref_ancallelcolnr)
        snps_orig.SetValue(rownr,data_ancallcolnr,state)
        
    snps=VTTable.VTTable()
    snps.CopyFrom(snps_orig)
    
    snps.SaveFile(outputfilename,saveheader=False, absentvaluestring='\\N')
    
    print("\n\n\n\n================= AFTER ====================")        
    snps.PrintRows(0,100)
    
    #Create a starting point for the SQL statement that is going to create the table
    f=open(basepath+"/DataKeposedaMySQL/ImportSnps.sql",'w')
    f.write('USE world;\n')
    f.write('DROP TABLE IF EXISTS snp;\n')
    f.write('CREATE TABLE snp (\n')
    for colname in snps.GetColList():
        datatype="DOUBLE"
        if (colname=='chrom') or (colname=='pos'): datatype="INT"
        if (colname=='snpid'): datatype="VARCHAR(20)"
        if (colname=='allele1') or (colname=='allele2') or (colname=='ancallele'): datatype="VARCHAR(5)"
        f.write('    {0} {1},\n'.format(colname,datatype))
    f.write(');\n')
    
    f.write("LOAD DATA INFILE '{0}'\n".format(outputfilename))
    f.write("    INTO TABLE snp\n")
    f.write("    FIELDS TERMINATED BY '\\t'\n")
    f.write("    LINES TERMINATED BY '\\n'\n")
    f.write("    ;\n")
    
    f.write("CREATE INDEX snp_chrom on snp (chrom);\n")
    f.write("CREATE INDEX snp_pos on snp (pos);\n")
    f.write("CREATE INDEX snp_snpid on snp (snpid);\n")
    
    
    f.close()
    
            
    print("================= DONE ====================")