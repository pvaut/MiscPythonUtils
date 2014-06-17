import VTTable

tb = VTTable.VTTable()
tb.allColumnsText = True
tb.LoadFile('/Users/pvaut/Documents/Genome/Ag1000g/Genes/mart_export-2.txt')

tb.RenameCol('Gene stable ID', 'Gene_stable_ID')
tb.RenameCol('Transcript stable ID', 'Transcript_stable_ID')
tb.RenameCol('Gene start (bp)', 'Gene_start')
tb.RenameCol('Gene end (bp)', 'Gene_end')
tb.RenameCol('Chromosome/scaffold name', 'Chromosome')
#tb.RenameCol('Protein stable ID', 'Protein_stable_ID')
#tb.RenameCol('Transcript start (bp)', 'Transcript_start')
#tb.RenameCol('Transcript end (bp)', 'Transcript_end')
tb.RenameCol('Gene name', 'Gene_name')
tb.RenameCol('Gene description', 'Gene_description')
tb.RenameCol('Uniprot Gene Name', 'Uniprot_Gene_Name')

tb.PrintRows(0,10)

genesMap = {}
for rownr in tb.GetRowNrRange():
    id = tb.GetValue(rownr,0)
    name = tb.GetValue(rownr, 3)
    syn = tb.GetValue(rownr, 2)
    descr = tb.GetValue(rownr, 4)
    if id not in genesMap:
        genesMap[id] = {
            'name': {},
            'syn': {},
            'descr': {}
        }
    gene = genesMap[id]
    if name not in gene['name']:
        gene['name'][name] = True
    if (syn not in gene['syn']) and (syn not in gene['name']):
        gene['syn'][syn] = True
    if descr not in gene['descr']:
        gene['descr'][descr] = True

with open('/Users/pvaut/Documents/Genome/Ag1000g/Genes/mart_export_processed.txt', 'w') as fp:
    fp.write('id\tname\tsyn\tdescr\n')
    for id in genesMap:
        gene = genesMap[id]
        fp.write('{id}\t{name}\t{syn}\t{descr}\n'.format(
            id=id,
            name=';'.join([v for v in gene['name']]),
            syn=';'.join([v for v in gene['syn']]),
            descr=';'.join([v for v in gene['descr']])
        ))

tb = VTTable.VTTable()
tb.allColumnsText = True
tb.LoadFile('/Users/pvaut/Documents/Genome/Ag1000g/Genes/mart_export_processed.txt')

tb.PrintRows(0,9999999)



tb.SaveSQLDump('/Users/pvaut/Documents/Genome/Ag1000g/Genes/biomart.sql', 'genes_biomart', True)