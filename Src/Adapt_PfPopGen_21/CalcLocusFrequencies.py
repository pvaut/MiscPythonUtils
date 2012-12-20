from TableUtils import VTTable
import MySQLdb
import sys
import math
import DataProviders
import sets


meta={
      'DBSRV':'localhost',
      'DBUSER':'root',
      'DBPASS':'1234',
      'DB':'world',
      'SOURCEDIR':'C:/Data/Genomes/PlasmodiumFalciparum/Release_21'
      }

sampleData=DataProviders.SampleInfoProvider(meta)

tableAggregationTypes=VTTable.VTTable()
tableAggregationTypes.allColumnsText=True
tableAggregationTypes.LoadFile(meta['SOURCEDIR']+'/OriginalData/Haplotypes/AggregationTypes.tab')
aggregationTypes=[item['AggregTypeID'] for item in tableAggregationTypes.ToListOfMaps()]
print('\nAggregation types: '+str(aggregationTypes)+'\n')

if False:#Obtain list of all aggregationID's
    for aggregationType in aggregationTypes:
        values=set()
        for sampleid in sampleData.GetSampleIDs():
            if sampleData.GetSampleInfo(sampleid,'Exclude')=='FALSE':
                values.add(sampleData.GetSampleInfo(sampleid, aggregationType))
        for val in values:
            print(aggregationType+'\t'+val)
    sys.exit()
    
tableAggregations=VTTable.VTTable()
tableAggregations.allColumnsText=True
tableAggregations.LoadFile(meta['SOURCEDIR']+'/OriginalData/Haplotypes/Aggregations.tab')
tableAggregations.PrintRows(0,999)
    


tableLoci=VTTable.VTTable()
tableLoci.allColumnsText=True
tableLoci.LoadFile(meta['SOURCEDIR']+'/OriginalData/Haplotypes/Loci.tab')
tableLoci.PrintRows(0,999)
indexLociLocusID=tableLoci.BuildColDict('LocusID', False)

tableLocusVariants=VTTable.VTTable()
tableLocusVariants.allColumnsText=True
tableLocusVariants.LoadFile(meta['SOURCEDIR']+'/OriginalData/Haplotypes/LociVariants.tab')
tableLocusVariants.PrintRows(0,999)

sourceDataFilesNames=[
                 meta['SOURCEDIR']+'/OriginalData/Haplotypes/CompositeGenotypes-Amino.tab',
                 meta['SOURCEDIR']+'/OriginalData/Haplotypes/CompositeGenotypes-Haplo.tab'
                 ]

outputfile=file(meta['SOURCEDIR']+'/LocusFrequencies.tab','w')
outputfile.write('AggregTypeID\tAggregShortName\tLocusID\tVariantID\tCount\n')


for aggregationType in aggregationTypes:
    print('\n###########################################')
    print('Aggregation type: '+aggregationType)
    print('###########################################')
    
    #get list of aggregations
    aggregationList=[]
    for rownr in tableAggregations.GetRowNrRange():
        if tableAggregations.GetValue(rownr,'AggregTypeID')==aggregationType:
            aggregationList.append(tableAggregations.GetValue(rownr,'AggregShortName'))
    print('Aggregations: '+str(aggregationList))
    
    for sourceDataFilesName in sourceDataFilesNames:
        sourceData=VTTable.VTTable()
        sourceData.allColumnsText=True
        sourceData.LoadFile(sourceDataFilesName)
        for locusNr in sourceData.GetRowNrRange():
            locusID=sourceData.GetValue(locusNr,0)
            print('\n')
            print('PROCESSING LOCUS '+locusID)
            if locusID not in indexLociLocusID:
                raise Exception('Unable to find locus ID')
            
            variantList=['-','<Het>']
            for rownr in tableLocusVariants.GetRowNrRange():
                if tableLocusVariants.GetValue(rownr,'LocusID')==locusID:
                    variantList.append(tableLocusVariants.GetValue(rownr,'VariantID'))
            variantMap={variantID:True for variantID in variantList}
            
            variantCount={ aggrid:{variantID:0 for variantID in variantList} for aggrid in aggregationList}
            
            for sampleNr in range(sourceData.GetColCount()-1):
                sampleID=sourceData.GetColName(sampleNr+1)
                if sampleData.GetSampleInfo(sampleID,'Exclude')!='FALSE':
                    raise Exception('Rejected sample in data set')
                aggregationName='Global'
                if aggregationType!='Global':
                    aggregationName=sampleData.GetSampleInfo(sampleID,aggregationType)
                state=sourceData.GetValue(locusNr,sampleID)
                if state not in variantMap:
                    raise Exception('State {0} for sample {1} not found in possible variants of locus {2}'.format(state,sampleID,locusID))
                variantCount[aggregationName][state]+=1
            print(str(variantCount))
            for aggrName in variantCount:
                counts=variantCount[aggrName]
                for state in counts:
                    outputfile.write('{0}\t{1}\t{2}\t{3}\t{4}\n'.format(aggregationType,aggrName,locusID,state,counts[state]))


outputfile.close()
print('--- FINISHED ---')