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

#-------------------------------------------------------------------------
print('\nGenes')
tableGenes.PrintRows(0,99999999)
print('\nHaplotypes')
tableHaplotypes.PrintRows(0,5)
print('\nAminoAlleles')
tableAminoAlleles.PrintRows(0,5)
