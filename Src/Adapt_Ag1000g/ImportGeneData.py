import VTTable

tb = VTTable.VTTable()
tb.allColumnsText = True
tb.LoadFile('/Users/pvaut/Documents/Genome/Ag1000g/Genes/mart_export-2.txt')

tb.RenameCol('Gene stable ID', 'Gene_stable_ID')
tb.RenameCol('Transcript stable ID', 'Transcript_stable_ID')
tb.RenameCol('Gene start (bp)', 'Gene_start')
tb.RenameCol('Gene end (bp)', 'Gene_end')
tb.RenameCol('Chromosome/scaffold name', 'Chromosome')
tb.RenameCol('Protein stable ID', 'Protein_stable_ID')
tb.RenameCol('Transcript start (bp)', 'Transcript_start')
tb.RenameCol('Transcript end (bp)', 'Transcript_end')
tb.RenameCol('Gene name', 'Gene_name')
tb.RenameCol('Gene description', 'Gene_description')

tb.PrintRows(0,10)

tb.SaveSQLDump('/Users/pvaut/Documents/Genome/Ag1000g/Genes/biomart.sql', 'genes_biomart', True)