from TableUtils import VTTable
import MySQLdb
import sys
import math


class SNPInfoProvider_Database:
    def __init__(self,MetaInfo):
        self.MetaInfo=MetaInfo
        
    def OpenDatabase(self):
        return MySQLdb.connect(host=self.MetaInfo['DBSRV'], user=self.MetaInfo['DBUSER'], passwd=self.MetaInfo['DBPASS'], db=self.MetaInfo['DB'])
    
    def GetSNPInRange(self,chromoId,start,stop):
        if chromoId[0:3]!='MAL':
            raise Exception('Invalid chromosome identifier '+chromoId)
        chromoNr=int(chromoId[3:])
        rs=[]
        db=self.OpenDatabase()
        cur = db.cursor()
        whereclause='SELECT pos, snpid, ref, nonrref FROM pfsnprel21 WHERE (chrom={0}) and (pos>={1}) and (pos<={2}) ORDER BY pos'.format(chromoNr,start,stop)
        cur.execute(whereclause)
        for row in cur.fetchall() :
            rs.append({
                       'pos':row[0],
                       'snpid':row[1],
                       'ref':row[2],
                       'nonref':row[3]
                       })
        return rs
    
    

class SampleInfoProvider:
    def __init__(self,imeta):
        self.meta=imeta
        self.table=VTTable.VTTable()
        self.table.allColumnsText=True
        self.table.LoadFile(self.meta['SOURCEDIR']+'/OriginalData/metadata-2.0.2_withsites.txt')
        self.sampleIndex=self.table.BuildColDict("Sample",False)
        self.sampleIDs=[self.table.GetValue(rownr,'Sample') for rownr in self.table.GetRowNrRange()]
    def GetSampleIDs(self):
        return self.sampleIDs
    def GetSampleInfo(self,SampleId,PropertyName):
        if not(SampleId in self.sampleIndex):
            raise Exception('Sample not present: '+SampleId)
        return self.table.GetValue(self.sampleIndex[SampleId],PropertyName)



#Encapsulates information about a single SNP on a single sample
class SampleSNP:
    def __init__(self,Id):
        self.Id=Id
        self.IsPresent=False#true if information about this snp is present
        self.IsNonRef=None#binary call, None means undefined
        self.Freq=None#frequency of the non-ref variant
        self.ReadCountRef=None
        self.ReadCountNonRef=None
    
#Encapsulates information about a single sample genotype
class SampleGenoType:
    def __init__(self,sampleId):
        self.sampleId=sampleId
        self.SNPs={}
    def GetSNP(self,snpid):
        return self.SNPs[snpid]
    
# UsedSNPMap:SNP infor will be collected for each SNP in this map (id is the key)
class SampleGenoTypeProvider_TabFile:
    def __init__(self,UsedSNPMap,imeta):
        self.meta=imeta
        self.scanSourceFiles=False#True: scan original files (needed for new data, default for production)  |   False: scan previous digest (much faster, useful for development)
        #Fetch all data for all relevant snps
        self.snpQuantifs=[
                     {'type':'call', 'origfile':'GenotypesNum.tab'},
                     {'type':'freq', 'origfile':'GenotypesFreq.tab'},
                     {'type':'rcnt', 'origfile':'ReadCounts-ref.tab'},
                     {'type':'nrcnt', 'origfile':'ReadCounts-nref.tab'}
                     ]
            
        #Scan the sample genotypes and accumulate information for the relevant snps
        sampleOffset=4#Start column of sample genotypes
        snpCol=3#Column containing the SNP id
        self.sampleIds=None
        self.GenoTypes={snpid:{}  for snpid in UsedSNPMap}
        self.SNPIds=[snpid for snpid in UsedSNPMap]
        self.sampleIds=None
        for quantif in self.snpQuantifs:
            if self.scanSourceFiles:
                f=open(self.meta['SOURCEDIR']+'/OriginalData/'+quantif['origfile'],'r')
                of=open(self.meta['SOURCEDIR']+'/ActiveSnpSampleInfo_'+quantif['type']+'.txt','w')
            else:
                f=open(self.meta['SOURCEDIR']+'/ActiveSnpSampleInfo_'+quantif['type']+'.txt','r')
            print('SCANNING SAMPLE GENOTYPE DATA '+quantif['origfile'])    
            line=f.readline()
            if self.scanSourceFiles:
                of.write(line)
            line=line.rstrip()
            sampleList=line.split('\t')[sampleOffset:]
            if self.sampleIds is None:
                self.sampleIds=sampleList
                print('Samples: '+str(self.sampleIds))
            else:
                if '\t'.join(self.sampleIds)!='\t'.join(sampleList):
                    raise Exception('Something is seriously wrong here')
            linenr=0
            for line in f:
                cells=line.rstrip().split('\t')
                snpid=cells[snpCol]
                data=cells[sampleOffset:]
                if snpid in UsedSNPMap:
                    if self.scanSourceFiles:
                        of.write(line)
                    self.GenoTypes[snpid][quantif['type']]=data
                linenr+=1
                if linenr%1000==0: print('Scanning genotypes '+str(linenr))
            f.close()
            if self.scanSourceFiles:
                of.close()
        self.SampleIndex={}
        for nr in range(len(self.sampleIds)):
            self.SampleIndex[self.sampleIds[nr]]=nr
                
                
    def GetSampleNr(self,sampleId):
        return self.SampleIndex[sampleId]
                
    #returns a single snp for a sample
    def GetSampleSNP(self,sampleNr,SNPId):
        snp=SampleSNP(SNPId)
        if self.GenoTypes[SNPId]['call'][sampleNr]=='0':
            return snp#no info is present
        snp.IsPresent=True
        snp.IsNonRef=(self.GenoTypes[SNPId]['call'][sampleNr]=='2')
        snp.Freq=float(self.GenoTypes[SNPId]['freq'][sampleNr])
        snp.ReadCountRef=int(self.GenoTypes[SNPId]['rcnt'][sampleNr])
        snp.ReadCountNonRef=int(self.GenoTypes[SNPId]['nrcnt'][sampleNr])
        return snp
    
    #Returns all observed snps for a sample
    def GetSampleGenoType(self,sampleNr):
        result=SampleGenoType(self.sampleIds[sampleNr])
        for snpid in self.SNPIds:
            result.SNPs[snpid]=self.GetSampleSNP(sampleNr,snpid)    
        return result
                
    def DumpData(self,tpe):
        lne='SAMPLE'
        for snp in self.SNPIds:
            lne+='\t'+snp
        print(lne)
        for sampleNr in range(len(self.sampleIds)):
            lne=self.sampleIds[sampleNr]
            for snp in self.SNPIds:
                lne+='\t'+self.GenoTypes[snp][tpe][sampleNr]
            print(lne)
