from TableUtils import VTTable

basedir = 'C:/Data/Genomes/PlasmodiumFalciparum/Release_21/OriginalData_03'


#-------------------------------------------------------------------------
tableGenes=VTTable.VTTable()
tableGenes.allColumnsText=True
tableGenes.LoadFile(basedir+"/Definition-GeneInfo.tab")
tableGenes.RemoveEmptyRows()
tableGenes.ColumnRemoveQuotes('Comments')


#-------------------------------------------------------------------------
tableAminoAlleles=VTTable.VTTable()
tableAminoAlleles.allColumnsText=True
tableAminoAlleles.LoadFile(basedir+"/Definition-AminoAlleles.tab")
tableAminoAlleles.RemoveEmptyRows()
tableAminoAlleles.ColumnRemoveQuotes('Literature Report')

tableAminoAlleles.ColumnRemoveQuotes('Nt')
tableAminoAlleles.MapCol('Nt', lambda st: [int(cell.lstrip(' ')) for cell in st.split(',')])


#-------------------------------------------------------------------------
tableHaplotypes=VTTable.VTTable()
tableHaplotypes.allColumnsText=True
tableHaplotypes.LoadFile(basedir+"/Definition-Haplotypes.tab")
tableHaplotypes.RemoveEmptyRows()
tableHaplotypes.ColumnRemoveQuotes('Comments')

#-------------------------------------------------------------------------
tableHaplotypeAlleles=VTTable.VTTable()
tableHaplotypeAlleles.allColumnsText=True
tableHaplotypeAlleles.LoadFile(basedir+"/Definition-HaplotypeAlleles.tab")
tableHaplotypeAlleles.RemoveEmptyRows()
tableHaplotypeAlleles.ColumnRemoveQuotes('Literature Report')


tableHaplotypes.ColumnRemoveQuotes('Amino Acid Positions')
tableHaplotypes.MapCol('Amino Acid Positions', lambda st: [int(cell.lstrip(' ')) for cell in st.split(',')])

#Some general tools
MapGeneName2ChromoId={ row['GeneName']:row['Chromosome'] for row in tableGenes.ToListOfMaps()}
#print(str(MapGeneName2ChromoId))
def GeneName2ChromoId(GeneName):
    if GeneName not in MapGeneName2ChromoId: raise Exception('Invalid gene name '+GeneName) 
    return MapGeneName2ChromoId[GeneName]

MapGeneNameAndAa2NucleotideRange={ row['Gene']+'_'+row['Aa']:row['Nt'] for row in tableAminoAlleles.ToListOfMaps()}
#print(str(MapGeneNameAndAa2NucleotideRange))
def GeneNameandAa2NucleotideRange(GeneName,Aa):
    token=GeneName+'_'+str(Aa)
    if token not in MapGeneNameAndAa2NucleotideRange: raise Exception('Invalid gene name + aminoacid '+token) 
    return MapGeneNameAndAa2NucleotideRange[token]



#Calculate genomic regions for haplotypes
tableHaplotypes.AddColumn(VTTable.VTColumn('GenomicRegion','Text'))
tableHaplotypes.FillColumn('GenomicRegion',None)
for RowNr in range(tableHaplotypes.GetRowCount()):
    GeneName=tableHaplotypes.GetValue(RowNr,tableHaplotypes.GetColNr('GeneName'))
    ChromoId=GeneName2ChromoId(GeneName)
    AaList=tableHaplotypes.GetValue(RowNr,tableHaplotypes.GetColNr('Amino Acid Positions'))
    FirstNucleotide=99999999
    LastNucleotide=0
    for Aa in AaList:
        Nucleotides=GeneNameandAa2NucleotideRange(GeneName,Aa)
        FirstNucleotide=min(FirstNucleotide,min(Nucleotides))
        LastNucleotide=max(LastNucleotide,max(Nucleotides))
    tableHaplotypes.SetValue(RowNr,tableHaplotypes.GetColNr('GenomicRegion'),'{0}:{1}-{2}'.format(ChromoId,FirstNucleotide,LastNucleotide))

#Add LocusID for AminoAlleles    
tableAminoAlleles.MergeColsToString('LocusID', '{0}-{1}','Gene','Aa')

#Create table with aminoacid information
tableAminoAcids=VTTable.VTTable()
tableAminoAcids.AddColumn(VTTable.VTColumn('Num','Text'))
tableAminoAcids.AddColumn(VTTable.VTColumn('LocusID','Text'))
tableAminoAcids.AddColumn(VTTable.VTColumn('LocusType','Text'))
tableAminoAcids.AddColumn(VTTable.VTColumn('Gene','Text'))
tableAminoAcids.AddColumn(VTTable.VTColumn('Aa','Text'))
tableAminoAcids.AddColumn(VTTable.VTColumn('Nt','Text'))
tableAminoAcids.AddColumn(VTTable.VTColumn('GenomicRegion','Text'))
mappedLoci={}
for RowNr in range(tableAminoAlleles.GetRowCount()):
    LocusID=tableAminoAlleles.GetValue(RowNr, tableAminoAlleles.GetColNr('Gene'))+'-'+tableAminoAlleles.GetValue(RowNr, tableAminoAlleles.GetColNr('Aa'))
    if LocusID not in mappedLoci:
        mappedLoci[LocusID]=True
        tableAminoAcids.AddRowEmpty()
        tableAminoAcids.SetValue(tableAminoAcids.GetRowCount()-1,tableAminoAcids.GetColNr('LocusID'),LocusID)
        GeneName=tableAminoAlleles.GetValue(RowNr, tableAminoAlleles.GetColNr('Gene'))
        NucleotideList=tableAminoAlleles.GetValue(RowNr, tableAminoAlleles.GetColNr('Nt'))
        tableAminoAcids.SetValue(tableAminoAcids.GetRowCount()-1,tableAminoAcids.GetColNr('Num'), tableAminoAlleles.GetValue(RowNr, tableAminoAlleles.GetColNr('Num')))
        tableAminoAcids.SetValue(tableAminoAcids.GetRowCount()-1,tableAminoAcids.GetColNr('Gene'), GeneName)
        tableAminoAcids.SetValue(tableAminoAcids.GetRowCount()-1,tableAminoAcids.GetColNr('Aa'), tableAminoAlleles.GetValue(RowNr, tableAminoAlleles.GetColNr('Aa')))
        tableAminoAcids.SetValue(tableAminoAcids.GetRowCount()-1,tableAminoAcids.GetColNr('Nt'), NucleotideList)
        FirstNucleotide=min(NucleotideList)
        LastNucleotide=max(NucleotideList)
        GenomicRegion='{0}:{1}-{2}'.format(GeneName2ChromoId(GeneName),FirstNucleotide,LastNucleotide)
        tableAminoAcids.SetValue(tableAminoAcids.GetRowCount()-1,tableAminoAcids.GetColNr('GenomicRegion'), GenomicRegion)
tableAminoAcids.FillColumn('LocusType','AMINO')

#Rename columns of Genes
tableGenes.DropCol('GeneId')

#Rename columns of tableAminoAcids
tableAminoAcids.RenameCol('Num', 'ordr')
tableAminoAcids.RenameCol('Gene', 'GeneName')
tableAminoAcids.AddColumn(VTTable.VTColumn('Comments','Text'))
tableAminoAcids.FillColumn('Comments','')
tableAminoAcids.MergeColsToString('Name','{0}','LocusID')
tableAminoAcids.ArrangeColumns(['LocusID','ordr','GenomicRegion','LocusType','GeneName','Name','Comments'])
tableAminoAcids.DropCol('Aa')
tableAminoAcids.DropCol('Nt')

#Rename columns of AminoAlleles
tableAminoAlleles.RenameCol('Num','ordr')
tableAminoAlleles.MergeColsToString('VariantID','{0}','Allele')
tableAminoAlleles.RenameCol('Allele','Name')
tableAminoAlleles.RenameCol('Literature Report','Comments')
tableAminoAlleles.AddColumn(VTTable.VTColumn('Color','Text'))
tableAminoAlleles.FillColumn('Color','Auto')
tableAminoAlleles.ArrangeColumns(['LocusID','VariantID','ordr','Mutant','Name','Color','Comments'])
tableAminoAlleles.DropCol('Gene')
tableAminoAlleles.DropCol('Aa')
tableAminoAlleles.DropCol('Nt')
tableAminoAlleles.DropCol('Variation')

#Rename columns of Haplotypes
tableHaplotypes.MergeColsToString('Name','{0}','Haplotype')
tableHaplotypes.RenameCol('Haplotype','LocusID')
tableHaplotypes.RenameCol('Num','ordr')
tableHaplotypes.AddColumn(VTTable.VTColumn('LocusType','Text'))
tableHaplotypes.FillColumn('LocusType','HAPLO')
tableHaplotypes.ArrangeColumns(['LocusID','ordr','GenomicRegion','LocusType','GeneName','Name','Comments'])
tableHaplotypes.DropCol('Amino Acid Positions')

#Rename columns of HaplotypeAlleles
tableHaplotypeAlleles.RenameCol('Haplotype', 'LocusID')
tableHaplotypeAlleles.MergeColsToString('VariantID','{0}','Allele')
tableHaplotypeAlleles.RenameCol('Allele','Name')
tableHaplotypeAlleles.RenameCol('Num','ordr')
tableHaplotypeAlleles.RenameCol('Literature Report','Comments')
tableHaplotypeAlleles.AddColumn(VTTable.VTColumn('Color','Text'))
tableHaplotypeAlleles.FillColumn('Color','Auto')
tableHaplotypeAlleles.ArrangeColumns(['LocusID','VariantID','ordr','Mutant','Name','Color','Comments'])
tableHaplotypeAlleles.DropCol('Composition')

#-------------------------------------------------------------------------
#print('\nGenes')
#tableGenes.PrintRows(0,99999999)
#print('\nHaplotypes')
#tableHaplotypes.PrintRows(0,5)
#print('\nAminoAlleles')
#tableAminoAlleles.PrintRows(0,5)
#print('\nAmino')
#tableAminoAcids.PrintRows(0,5)
#print('\nHaplotypeAlleles')
#tableHaplotypeAlleles.PrintRows(0,15)

#Merge to LociVariants 
tableLociVariants=VTTable.VTTable()
tableLociVariants.CopyFrom(tableHaplotypeAlleles)
tableLociVariants.Append(tableAminoAlleles)

 #Merge to Loci
tableLoci=VTTable.VTTable()
tableLoci.CopyFrom(tableHaplotypes)
tableLoci.Append(tableAminoAcids)

tableLociVariants.PrintRows(0,99999)
tableLoci.PrintRows(0,99999)

#Some integrity checks
locusMap=tableLoci.BuildColDict('LocusID', False)