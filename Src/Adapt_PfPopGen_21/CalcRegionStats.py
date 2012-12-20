from TableUtils import VTTable

sourcedir='C:/Data/Genomes/PlasmodiumFalciparum/Release_21/OriginalData'

sampleTable=VTTable.VTTable()
sampleTable.allColumnsText=True
sampleTable.LoadFile(sourcedir+'/metadata-2.0.2.txt')
sampleTable.PrintRows(0,10)


#Information
regionTypes=[
             { 'regionTypeId':-1,'regionColName':"SubCont"},
             { 'regionTypeId':0, 'regionColName':"Country"},
             { 'regionTypeId':1, 'regionColName':"Region"},
             ]

colNrInclude=sampleTable.GetColNr("Exclude")
flagInclude="FALSE"
colNrStudy=sampleTable.GetColNr("Study")


fileRegionInfo=open("C:/Data/Genomes/PlasmodiumFalciparum/Release_21/RegionInfo.txt","w")
fileRegionStudyInfo=open("C:/Data/Genomes/PlasmodiumFalciparum/Release_21/RegionStudyInfo.txt","w")

for regionType in regionTypes:
    
    regionTypeId=regionType['regionTypeId']
    colNrRegion=sampleTable.GetColNr(regionType['regionColName'])
    
    sampleCount=0
    regionsMap={}
    regionsStudiesMap={}
    for sampleNr in range(0,sampleTable.GetRowCount()):
        if sampleTable.GetValue(sampleNr, colNrInclude) == flagInclude:
            region=sampleTable.GetValue(sampleNr, colNrRegion)
            study=sampleTable.GetValue(sampleNr, colNrStudy)
            sampleCount+=1
            if not(region in regionsMap):
                regionsMap[region]={'cnt':0}
            regionsMap[region]['cnt']+=1
            regionStudy=(region,study)
            if not(regionStudy in regionsStudiesMap):
                regionsStudiesMap[regionStudy]={'cnt':0}
            regionsStudiesMap[regionStudy]['cnt']+=1
    
    print("Number of samples: "+str(sampleCount))
    
    for reg in regionsMap:
        fileRegionInfo.write('{0}\t{1}\t{2}\n'.format(regionTypeId,reg,regionsMap[reg]['cnt']))
        
    for regStudy in regionsStudiesMap:
        fileRegionStudyInfo.write('{0}\t{1}\t{2}\t{3}\n'.format(regionTypeId,regStudy[0],regStudy[1],regionsStudiesMap[regStudy]['cnt']))
    
fileRegionInfo.close()
fileRegionStudyInfo.close()