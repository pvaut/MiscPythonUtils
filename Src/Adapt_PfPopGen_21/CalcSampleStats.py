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
tableAggregations.PrintRows(0,10)

fileStudiesCount=open(meta['SOURCEDIR']+'/SampleCount_Aggregations_Studies.tab','w')
fileStudiesCount.write('AggrType\tAggrShortName\tStudy\tCount\n')
fileSitesCount=open(meta['SOURCEDIR']+'/SampleCount_Aggregations_Sites.tab','w')
fileSitesCount.write('AggrType\tAggrShortName\tSite\tCount\n')

for aggrNr in tableAggregations.GetRowNrRange():
    aggrType=tableAggregations.GetValue(aggrNr,'AggregTypeID')
    print('')
    print('####################################')
    print('Processing '+aggrType+' '+tableAggregations.GetValue(aggrNr,'AggregShortName'))
    studiesCount={}
    sitesCount={}
    for sampleID in sampleData.GetSampleIDs():
        if sampleData.GetSampleInfo(sampleID, 'Exclude')=='FALSE':
            inSet=True
            if aggrType!='Global':
                aggr=sampleData.GetSampleInfo(sampleID, aggrType)
                if aggr!=tableAggregations.GetValue(aggrNr,'AggregShortName'):
                    inSet=False
            if inSet:
                study=sampleData.GetSampleInfo(sampleID,'Study')
                if study not in studiesCount:
                    studiesCount[study]=0
                studiesCount[study]+=1
                site=sampleData.GetSampleInfo(sampleID,'Site')
                if site not in sitesCount:
                    sitesCount[site]=0
                sitesCount[site]+=1
    for study in studiesCount:
        fileStudiesCount.write('{0}\t{1}\t{2}\t{3}\n'.format(aggrType,tableAggregations.GetValue(aggrNr,'AggregShortName'),study,studiesCount[study]))
    for site in sitesCount:
        fileSitesCount.write('{0}\t{1}\t{2}\t{3}\n'.format(aggrType,tableAggregations.GetValue(aggrNr,'AggregShortName'),site,sitesCount[site]))



fileStudiesCount.close()
fileSitesCount.close()
