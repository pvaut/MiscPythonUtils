
import copy
import sys
import gc
from TableUtils import VTTable
from TableUtils import IntervalTools


popnamelist=['Akan','Fula','Jola','Malawi','Mandinka','Northerner','Wolof','YRI']
#popnamelist=['YRI']


basepath="C:/Data/Articles/PositiveSelection"

def BuildIhsCombinationTable():
    
    #prepare table that will contain the combined information
    IHSTable=VTTable.VTTable()
    IHSTable.AddColumn(VTTable.VTColumn("SNP","Text"))
    IHSTable.AddColumn(VTTable.VTColumn("chromosome","Value"))
    IHSTable.AddColumn(VTTable.VTColumn("Pos35","Value"))
    IHSTable.AddColumn(VTTable.VTColumn("AncestralAllele","Text"))
    IHSTable.AddColumn(VTTable.VTColumn("AncestralAlleleFrequency","Text"))
    #column nrs in combined table
    ColNrIHSSNP=IHSTable.GetColNr("SNP")
    ColNrIHSChromosome=IHSTable.GetColNr("chromosome")
    ColNrIHSPos35=IHSTable.GetColNr("Pos35")
    ColNrIHSAncestralAllele=IHSTable.GetColNr("AncestralAllele")
    ColNrIHSAncestralAlleleFrequency=IHSTable.GetColNr("AncestralAlleleFrequency")
    
    ColNrIHSIHS={}
    for popname in popnamelist:
        IHSTable.AddColumn(VTTable.VTColumn("StdIHS_{0}".format(popname),"Value"))
        ColNrIHSIHS[popname]=IHSTable.GetColCount()-1
    
    SNPDict={}
    
    for popname in popnamelist:
        if popname!="YRI":
            filename="{0}/DataPV/SNP/IHS/{1}_Untransmitted_ihs_standardized.txt".format(basepath,popname)
        else:
            filename="{0}/DataPV/SNP/IHS/{1}_650Y_matched_ihs_standardized.txt".format(basepath,popname)
        IHSPopTable=VTTable.VTTable()
        IHSPopTable.LoadFile(filename)#<--------------------------------! SHOULD BE COMPLETE
        IHSPopTable.PrintRows(0,10)
        
        #column nrs in original population file
        ColrNrPopSNP=IHSPopTable.GetColNr("SNP")
        ColNrPopChromosome=IHSPopTable.GetColNr("chromosome")
        ColNrPopPos35=IHSPopTable.GetColNr("Pos35")
        ColNrPopIHSStd=IHSPopTable.GetColNr("StandardizedIHS")
        ColNrPopAncestralAllele=IHSPopTable.GetColNr("AncestralAllele")
        ColNrPopAncestralAlleleFrequency=IHSPopTable.GetColNr("AncestralAlleleFrequency")
        
        for rownr in IHSPopTable.GetRowNrRange():
            SNP=IHSPopTable.GetValue(rownr,ColrNrPopSNP)
            chromosome=IHSPopTable.GetValue(rownr,ColNrPopChromosome)
            Pos35=IHSPopTable.GetValue(rownr,ColNrPopPos35)
            AncestralAllele=IHSPopTable.GetValue(rownr,ColNrPopAncestralAllele)
            AncestralAlleleFrequency=IHSPopTable.GetValue(rownr,ColNrPopAncestralAlleleFrequency)
            IHSStd=IHSPopTable.GetValue(rownr,ColNrPopIHSStd)
            if SNP in SNPDict:
                rownr2=SNPDict[SNP]
                if chromosome!=IHSTable.GetValue(rownr2,ColNrIHSChromosome):
                    raise Exception("Incompatible chromosomes at {0}".format(SNP))
                if Pos35!=IHSTable.GetValue(rownr2,ColNrIHSPos35):
                    raise Exception("Incompatible positions at {0}".format(SNP))
                if AncestralAllele!=IHSTable.GetValue(rownr2,ColNrIHSAncestralAllele):
                    raise Exception("Incompatible ancestral alleles at {0}".format(SNP))
#                if abs(AncestralAlleleFrequency-IHSTable.GetValue(rownr2,ColNrIHSAncestralAlleleFrequency)>0.001):
#                    raise Exception("Incompatible ancestral frequencies at {0}: {1} vs {2}".format(SNP,AncestralAlleleFrequency,IHSTable.GetValue(rownr2,ColNrIHSAncestralAlleleFrequency)))
#                print("Duplicate {0} OK".format(SNP))
            else:
                IHSTable.AddRowEmpty()
                rownr2=IHSTable.GetRowCount()-1
                IHSTable.SetValue(rownr2,ColNrIHSSNP,SNP)
                IHSTable.SetValue(rownr2,ColNrIHSChromosome,chromosome)
                IHSTable.SetValue(rownr2,ColNrIHSPos35,Pos35)
                IHSTable.SetValue(rownr2,ColNrIHSAncestralAllele,AncestralAllele)
                IHSTable.SetValue(rownr2,ColNrIHSAncestralAlleleFrequency,AncestralAlleleFrequency)
                SNPDict[SNP]=rownr2
            IHSTable.SetValue(rownr2,ColNrIHSIHS[popname],IHSStd)
                
        IHSTable.PrintRows(0,50)
        
    IHSTable=IHSTable.SortValuesReturn("Pos35")
    IHSTable=IHSTable.SortValuesReturn("chromosome")
    IHSTable.SaveFile("{0}/DataPV/SNP/IHS/CombinedIHS.txt".format(basepath))

    IHSTable.DropCol("AncestralAlleleFrequency")
    for popname in popnamelist:
        IHSTable.DropCol("StdIHS_{0}".format(popname))
    IHSTable.SaveFile("{0}/DataPV/SNP/IHS/AncestralAlleles.txt".format(basepath))

#BuildIhsCombinationTable()

#checks whether the allele1, allele2 information in the keposeda snp file is identical to the illumina files
def CheckAllele12():
    KeposedaSNP=VTTable.VTTable()
    KeposedaSNP.LoadFile(basepath+"/DataPV/KeposedaSNP.txt",200000)
    KeposedaSNP.PrintRows(0,10)

    Chrom1=VTTable.VTTable()
    Chrom1.LoadFile(basepath+"/DataPV/chr1_positive_strand_allele_map.txt")
    Chrom1.PrintRows(0,10)
    snpdct=Chrom1.BuildColDict("SNP",False)

    for rownr in KeposedaSNP.GetRowNrRange():
        SNP=KeposedaSNP.GetValue(rownr,2)
        chromosome=KeposedaSNP.GetValue(rownr,0)
        if chromosome==1:
            rownr2=snpdct[SNP]
            KpAllele1=KeposedaSNP.GetValue(rownr,3)
            KpAllele2=KeposedaSNP.GetValue(rownr,4)
            IllAllele1=Chrom1.GetValue(rownr2,2)
            IllAllele2=Chrom1.GetValue(rownr2,3)
            if (KpAllele1!=IllAllele1) or (KpAllele2!=IllAllele2):
                print("{4}: {0},{1} - {2},{3}".format(KpAllele1,KpAllele2,IllAllele1,IllAllele2,SNP))
    print("done")

#CheckAllele12()
    

#Checks whether the ancestral alleles distilled from Kerrin's iHS files corresponds to one of the allele1, allele2 states in the keposeda snp table  
def CheckAllele12vsAncest():
    KeposedaSNP=VTTable.VTTable()
    KeposedaSNP.LoadFile(basepath+"/DataPV/KeposedaSNP.txt")
    KeposedaSNP.PrintRows(0,10)

    AncestAll=VTTable.VTTable()
    AncestAll.LoadFile("{0}/DataPV/SNP/IHS/AncestralAlleles.txt".format(basepath))
    AncestAll.PrintRows(0,10)
    snpdct=AncestAll.BuildColDict("SNP",False)

    notfoundcount=0
    for rownr in KeposedaSNP.GetRowNrRange():
        SNP=KeposedaSNP.GetValue(rownr,2)
        if SNP in snpdct:
            rownr2=snpdct[SNP]
            allele1=KeposedaSNP.GetValue(rownr,3)
            allele2=KeposedaSNP.GetValue(rownr,4)
            allelanc=AncestAll.GetValue(rownr2, 3)
            if (allelanc!=allele1) and (allelanc!=allele2):
                print("Problem: SNP={0} allele1={1} allele2={2} ancest={3}".format(SNP,allele1,allele2,allelanc))
        else:
            #print("Not found in ancestral allele dict: SNP {0}".format(SNP))
            notfoundcount+=1
    print("SNPs not found in ancestral allele info: {0} / {1}".format(notfoundcount,KeposedaSNP.GetRowCount()))

#CheckAllele12vsAncest()


#Compares the ancestral allele information as destilled from Kerrin's iHS files with Pritchard data
def CheckAncest():
    AncestPritch=VTTable.VTTable()
    AncestPritch.LoadFile(basepath+"/DataPV/AncestralPritchard/allanc.CEU",1000,True)
    AncestPritch.PrintRows(0,10)

    AncestAll=VTTable.VTTable()
    AncestAll.LoadFile("{0}/DataPV/SNP/IHS/AncestralAlleles.txt".format(basepath))
    AncestAll.PrintRows(0,10)
    snpdct=AncestAll.BuildColDict("SNP",False)

    notfoundcount=0
    for rownr in AncestPritch.GetRowNrRange():
        SNP=AncestPritch.GetValue(rownr,0)
        if SNP in snpdct:
            rownr2=snpdct[SNP]
            allele_ref=AncestPritch.GetValue(rownr,3)
            allele_anc=AncestPritch.GetValue(rownr,4)
            allelanc=AncestAll.GetValue(rownr2, 3)
            if (allelanc!=allele_anc):
                print("Problem: SNP={0} allele1={1} allele2={2} ancest={3}".format(SNP,allele_ref,allele_anc,allelanc))
        else:
            #print("Not found in ancestral allele dict: SNP {0}".format(SNP))
            notfoundcount+=1
    #print("SNPs not found in ancestral allele info: {0} / {1}".format(notfoundcount,KeposedaSNP.GetRowCount()))

CheckAncest()




def bla():
    KeposedaSNP=VTTable.VTTable()
    KeposedaSNP.LoadFile(basepath+"/DataPV/KeposedaSNP.txt",50)
    KeposedaSNP.PrintRows(0,10)
    
    FulaIHS=VTTable.VTTable()
    FulaIHS.LoadFile(basepath+"/DataPV/Fula_Untransmitted_ihs_standardized.txt")
    FulaIHS.PrintRows(0,10)
    FulaIHS_SNPDict=FulaIHS.BuildColDict("SNP",False)
    
    
    snpcolnr=KeposedaSNP.GetColNr("snp")
    fulafreqcolnr=KeposedaSNP.GetColNr("Freq_Fula")
    
    freqcolnr2=FulaIHS.GetColNr("AncestralAlleleFrequency")
    for rownr in range(0,15):
        snp=KeposedaSNP.GetValue(rownr,snpcolnr)
        rownr2=FulaIHS_SNPDict[snp]
        freq1=KeposedaSNP.GetValue(rownr, fulafreqcolnr)
        freq2=FulaIHS.GetValue(rownr2, freqcolnr2)
        print("")
        print("")
        print("{0} {1} diff={2} sum={3}".format(freq1,freq2,freq1-freq2,freq1+freq2))
        KeposedaSNP.PrintRows(rownr,rownr)
        FulaIHS.PrintRows(rownr2,rownr2)
        #sys.exit()
    
    sys.exit()
    