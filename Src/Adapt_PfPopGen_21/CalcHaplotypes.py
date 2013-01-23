from TableUtils import VTTable
import MySQLdb
import sys
import math
import DataProviders


meta={
      'DBSRV':'localhost',
      'DBUSER':'root',
      'DBPASS':'1234',
      'DB':'world',
      'SOURCEDIR':'C:/Data/Genomes/PlasmodiumFalciparum/Release_21',
      'ORIGDIR':'OriginalData_01'
      }

if False:
    lst=['107450','107451','107452','107453','107454','107455','107456','107457']
    f=open('C:/Data/Genomes/PlasmodiumFalciparum/Release_21/{0}/ReadCounts-nref.tab'.format(meta['ORIGDIR']))
    print(f.readline().rstrip())
    for line in f:
        line=line.rstrip()
        cells=line.split('\t')
        if cells[0] in lst:
            print(line)
    f.close()
    sys.exit()


        

################################################################################################
# Some hacked stuff for missingness stats

stats={}        
missingprop="Study"
s_cnt=0
s_sumfrac=0

NRState_459003=True
NRState_459001=True
NRState_458998=True
Discostate='TRUE'

def StatDoAll(SampleId):#Currenly a hack
    global stats
    global s_cnt
    global s_sumfrac
    sampleNr=SampleGenoTypeData.GetSampleNr(SampleId)
   
    
    snptry459001=SampleGenoTypeData.GetSampleSNP(sampleNr, 'MAL7:459001')
    snptry458998=SampleGenoTypeData.GetSampleSNP(sampleNr, 'MAL7:458998')
    snptry459003=SampleGenoTypeData.GetSampleSNP(sampleNr, 'MAL7:459003')
        
    snpa=SampleGenoTypeData.GetSampleSNP(sampleNr, 'MAL7:458990')
    snpb=SampleGenoTypeData.GetSampleSNP(sampleNr, 'MAL7:459065')
    
    
    if SampleData.GetSampleInfo(SampleId, 'UsedInSnpDiscovery')==Discostate:
        if snpa.IsPresent and snpb.IsPresent and snptry459001.IsPresent and snptry459003.IsPresent and snptry458998.IsPresent:
            covsurround=(snpa.ReadCountNonRef+snpa.ReadCountRef+snpb.ReadCountNonRef+snpb.ReadCountRef)/2.0
            covsnp=(snptry459001.ReadCountNonRef+snptry459001.ReadCountRef+snptry459003.ReadCountNonRef+snptry459003.ReadCountRef)/2.0
            frc=covsnp/covsurround
            if (snptry459001.IsNonRef==NRState_459001) and (snptry459003.IsNonRef==NRState_459003) and (snptry458998.IsNonRef==NRState_458998):
                s_cnt+=1
                s_sumfrac+=frc
    
    prop=SampleData.GetSampleInfo(SampleId, missingprop)
    if not(prop in stats):
        stats[prop]={'all':0, 'missing':0 } 
    stats[prop]['all']+=1;

def StatDoMissing(SampleId):#Currenly a hack
    prop=SampleData.GetSampleInfo(SampleId, missingprop)
    if not(prop in stats):
        stats[prop]={'all':0, 'missing':0 } 
    stats[prop]['missing']+=1;
    
    
def ReportMissing():
    #print('CovFrac Ref '+str(sumfrac_ref/cnt_ref)+' samples: '+str(cnt_ref))
    print('NRState_459003: '+str(NRState_459003))
    print('NRState_459001: '+str(NRState_459001))
    print('NRState_458998: '+str(NRState_458998))
    print('Discostate: '+str(Discostate))
    print('CovFrac '+str(s_sumfrac/s_cnt)+' samples: '+str(s_cnt))
    #print('Missing statistics over '+missingprop)
    #for it in stats:
    #    print('"'+it+'"  =\t '+str(stats[it]['missing'])+' ;\t '+str(stats[it]['all'])+' ;\t '+'%0.1f'%(100*stats[it]['missing']/stats[it]['all'])+'%'  )
    
    
# End of hacked stuff
################################################################################################        
        
    
    

#Returns a string that highlights the difference between two strings of equal length
def CreateDifferenceMask(st1,st2):
    if len(st1)!=len(st2):
        raise Exception('Incompatible string lengths ({0}-{1}'.format(st1,st2))
    rs=[]
    for i in range(len(st1)):
        if st1[i]==st2[i]:
            rs.append("'")
        else:
            rs.append('^')
    return ''.join(rs)

#A class that translates nucleic acid sequences into aminoacid sequencies (currently using the standard translation table)
class SequenceTranslator:
    def __init__(self):
        #the following is the standard translation table:
        self.AAs  =   'FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
        self.Starts = '---M---------------M---------------M----------------------------'
        self.Base1  = 'TTTTTTTTTTTTTTTTCCCCCCCCCCCCCCCCAAAAAAAAAAAAAAAAGGGGGGGGGGGGGGGG'
        self.Base2  = 'TTTTCCCCAAAAGGGGTTTTCCCCAAAAGGGGTTTTCCCCAAAAGGGGTTTTCCCCAAAAGGGG'
        self.Base3  = 'TCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAG'
        self.mapNucl2Amino={}
        for i in range(len(self.AAs)):
            self.mapNucl2Amino[self.Base1[i]+self.Base2[i]+self.Base3[i]]=self.AAs[i]
    def Nucl2Amino(self,seq,kodonOffset):
        rs=[]
        ps=kodonOffset
        sqlen=len(seq)
        while ps<=sqlen-3:
            rs.append(self.mapNucl2Amino[seq[ps:ps+3]])
            ps+=3
        return ''.join(rs)
        
#A class that contains the nucleic acid sequences for a set of chromosomes
class Genome:
    def __init__(self):
        self.sequences={}
    def ReadFASTA(self,filename):
        f=open(filename)
        currentSeq=None
        for line in f:
            line=line.rstrip()
            if len(line)>0:
                if line[0]=='>':
                    currentSeq=line[1:]
                    self.sequences[currentSeq]=[]
                    print('reading sequence '+currentSeq)
                else:
                    if not(currentSeq):
                        raise Exception('Invalid fasta file')
                    self.sequences[currentSeq].append(line)
        f.close()
        for currentSeq in self.sequences:
            self.sequences[currentSeq]=''.join(self.sequences[currentSeq])
    def GetRange(self,seqId,pos,length):#1-based
        if not(seqId in self.sequences):
            raise Exception('Invalid fasta file sequence index '+seqId)
        return self.sequences[seqId][pos-1:pos-1+length]


class CallingError(Exception):
    def __init__(self, tpe, msg):
        self.tpe = tpe
        self.msg = msg

#A class that encapsulates a specific variant for a haplotype locus
class HaplotypeVariant:
    def __init__(self,Locus,Id):
        self.Id=Id
        self.Locus=Locus#should contain HaplotypeLocus
        self.SeqNucl=''
        self.SeqAmin=''
        self.Locus.AddVariant(self)
        self.PositionIsNonRef=None#for each monitored position, determines if the position is ref(false) or nonref(true) for this variant
        
    def SetSeqNucl(self,seq):
        if len(seq)!=len(self.Locus.SeqNuclRef):
            raise Exception('Inconsistent sequence lengths')
        self.SeqNucl=seq
        self.SeqAmin=self.Locus.Caller.Translator.Nucl2Amino(self.SeqNucl,self.Locus.KodonOffset)
        self.PositionIsNonRef=[seq[ps-self.Locus.PositionFirst]!=self.Locus.SeqNuclRef[ps-self.Locus.PositionFirst] for ps in self.Locus.Positions]

    def IsThis(self,haplo):
        if (len(self.PositionIsNonRef)!=len(haplo)):
            raise Exception('Internal error: incompatible haplotype position vectors')        
        for posNr in range(len(self.PositionIsNonRef)):
            if haplo[posNr]!=self.PositionIsNonRef[posNr]:
                return False
        return True
        
            
    def DumpData(self):#Writes the elementary data to stdout
        print('    VARIANT='+self.Id)
        print('        SEQ NUCL='+str(self.SeqNucl))
        print('        EQ AMIN='+str(self.SeqAmin))
        print('        DEVIATING POSITIONS:'+''.join([str(int(vl)) for vl in self.PositionIsNonRef]))
    
    
#A class that encapsulates a locus on the genome for which we want to call haplotypes
class HaplotypeLocus:
    def __init__(self,Caller,Id,Name):
        self.Id=Id
        self.Caller=Caller;#should contain HaplotypeCaller
        self.Name=Name
        self.ChromosomeId=''
        self.PositionFirst=1#1-based
        self.PositionLast=1#1-based, this position is included
        self.KodonOffset=0
        self.Positions=None#a list of positions that will be monitored for the haplotype determination (positions are 1-based)
        self.Positions2Index=None#a map that, for each monitored position, converts genomic positions to the position index nr
        self.SeqNuclRef=''
        self.SeqAminRef=''
        self.variants=[]#A list of all possible variants, represented by instances of HaplotypeVariant
        self.variantIndex={}#Maps variant id's to indices in the variant vector
        self.ObservedSNPList=None#a list of all SNPs observed in this region, containing HaplotypeSNPInfo instances
        self.Caller.AddLocus(self)
        self.FreqErrorThreshold=0.05#Assumed accuracy limit for frequencies. Note: ideally, this decision should be based on read counts!
        self.CountTotal=0
        self.CountMissing=0
        self.CountPureCalls=0
        self.CountMixedCalls=0
        self.CountPureUnmatchedCalls=0
        self.CountMixedUnmatchedCalls=0
        self.Errors=[]
        
    #Define a region as haplotype, and monitor every position in this region
    def SetRegion(self,ChromosomeId,PositionFirst,PositionLast,KodonOffset):
        self.ChromosomeId=ChromosomeId
        self.PositionFirst=PositionFirst
        self.PositionLast=PositionLast
        self.KodonOffset=KodonOffset
        #Monitor each position in the full range
        self.Positions=range(self.PositionFirst,self.PositionLast+1)
        self.Positions2Index={}
        for i in range(len(self.Positions)):
            self.Positions2Index[self.Positions[i]]=i
        self.SeqNuclRef=self.Caller.RefGenome.GetRange(self.ChromosomeId,self.PositionFirst,self.PositionLast-self.PositionFirst+1)
        self.SeqAminRef=self.Caller.Translator.Nucl2Amino(self.SeqNuclRef,self.KodonOffset)
        #Obtain list of observed SNPs in this region
        self.ObservedSNPList=[]
        observedSNPList=self.Caller.SnpInfoProvider.GetSNPInRange(self.ChromosomeId,self.PositionFirst,self.PositionLast)
        for snpinfo in observedSNPList:
            snp=HaplotypeSNPInfo(snpinfo['snpid'])
            snp.ChromosomeId=locus.ChromosomeId
            snp.Position=snpinfo['pos']
            snp.Ref=snpinfo['ref']
            snp.NonRef=snpinfo['nonref']
            self.ObservedSNPList.append(snp)
            self.Caller.AddSNP(snp)
            #Basic sanity check
            if snp.Ref!=self.SeqNuclRef[snp.Position-self.PositionFirst]:
                raise Exception('SNP is incompatible with reference sequence')
        
        
    def AddVariant(self,variant):
        self.variantIndex[variant.Id]=len(self.variants)
        self.variants.append(variant)
        
    def DumpData(self):#Writes the elementary data to stdout
        print('LOCUS ID='+self.Id)
        print('NAME='+self.Name)
        print('POSITION={0}:{1}-{2}'.format(self.ChromosomeId,self.PositionFirst,self.PositionLast))
        print('TRANSLATION OFFSET='+str(self.KodonOffset))
        print('REFSEQ NUCL='+str(self.SeqNuclRef))
        print('REFSEQ AMIN='+str(self.SeqAminRef))
        for variant in self.variants:
            variant.DumpData()
            
    def PrintStats(self):
        print('LOCUS: '+self.Name)
        print('Total number of calls: '+str(self.CountTotal))
        print('Calls with missing SNPs: '+str(self.CountMissing))
        print('Pure calls: '+str(self.CountPureCalls))
        print('Mixed calls: '+str(self.CountMixedCalls))
        print('Pure UNMATCHED calls: '+str(self.CountPureUnmatchedCalls))
        print('Mixed UNMATCHED calls: '+str(self.CountMixedUnmatchedCalls))
        print('')
        
    def DumpErrors(self,fle):
        for err in self.Errors:
            fle.write(err['sampleid'])
            fle.write('\t'+err['type'])
            fle.write('\t'+err['frequencies'])
            fle.write('\t'+err['coverages'])
            fle.write('\n')
            
    #Converts genotype info for a single sample into a list of SNP info at the monitored haplotype positions
    def GenotypeInfo2PositionSNPs(self,SampleGenoTypeInfo):
        #set all positions to defaults
        freqs=[None]*len(self.Positions)
        for snp in self.ObservedSNPList:
            if snp.Position in self.Positions2Index:
                freqs[self.Positions2Index[snp.Position]]=SampleGenoTypeInfo.GetSNP(snp.Id)
        return freqs


    def _CallPure(self,samplePositionInfo):
        self.CountPureCalls+=1
        #create single sample single haplotype
        haplo=[]
        for snp in samplePositionInfo:
            if snp is None:
                haplo.append(False)
            else:
                haplo.append(snp.IsNonRef)
        #find matching variant
        matchVariant=None
        for variant in self.variants:
            if variant.IsThis(haplo):
                if not(matchVariant is None):
                    raise Exception('Dual outcome for haplotype determination')
                matchVariant=variant
        if matchVariant is None:
            print('*** UNMATCHED HAPLOTYPE')
            self.CountPureUnmatchedCalls+=1
            raise CallingError('UnmatchedPure','')
        print('Pure call: '+matchVariant.Id)
        return [{'variantid':matchVariant.Id, 'frequency':1.0}]


    def _CallMixed(self,samplePositionInfo):
        self.CountMixedCalls+=1
        print('PERFORMING MIXED CALL')
        hits=[]
        #Loop all possible combinations of two variants
        for variantNr1 in range(len(self.variants)):
            for variantNr2 in range(variantNr1):
                variant1=self.variants[variantNr1]
                variant2=self.variants[variantNr2]
                #estimate fraction of variant2, using all positions that segregate between the variants
                frac2=0
                frac2count=0
                for positNr in range(len(self.Positions)):
                    if variant1.PositionIsNonRef[positNr]!=variant2.PositionIsNonRef[positNr]:
                        if variant2.PositionIsNonRef[positNr]:
                            frac2+=samplePositionInfo[positNr].Freq
                        else:
                            frac2+=1-samplePositionInfo[positNr].Freq
                        frac2count+=1
                frac2/=frac2count
                #calculate distortion
                maxDist=0
                for positNr in range(len(self.Positions)):
                    estimFrac=(1-frac2)*int(variant1.PositionIsNonRef[positNr])+frac2*int(variant2.PositionIsNonRef[positNr])
                    observedFraq=0
                    if not(samplePositionInfo[positNr] is None):
                        observedFraq=samplePositionInfo[positNr].Freq
                    maxDist=max(maxDist,math.fabs(estimFrac-observedFraq))
                hits.append({'haplo1':variant1, 'haplo2':variant2, 'frac2':frac2, 'maxdist':maxDist})
        hits=sorted(hits, key=lambda el: el['maxdist'])
        if (hits[0]['maxdist']>self.FreqErrorThreshold) or (hits[0]['maxdist']>0.5*hits[1]['maxdist']):
            print('*** UNMATCHED HAPLOTYPE')
            self.CountMixedUnmatchedCalls+=1
            raise CallingError('UnmatchedMixed','')
        mixedCall=hits[0]['haplo1'].Id+'+'+hits[0]['haplo2'].Id
        print(mixedCall)
        return[
               {'variantid':hits[0]['haplo1'].Id, 'frequency':1.0-hits[0]['frac2']},
               {'variantid':hits[0]['haplo2'].Id, 'frequency':hits[0]['frac2']},
               ]
        
    def GetCalledItemIDs(self):
        return [self.Id+'|'+variant.Id for variant in self.variants]
            
    def Call(self,SampleGenoTypeInfo):
        self.CountTotal+=1
        samplePositionInfo=self.GenotypeInfo2PositionSNPs(SampleGenoTypeInfo)
        resultList=[None]*len(self.variants)
        StatDoAll(SampleGenoTypeInfo.sampleId)#Currently a bit of a hack

        try:
            #Print some basic info
            freqstr='|'
            covstr='|'
            for snp in samplePositionInfo:
                if snp is None:
                    freqstr+='-'
                    covstr+='-'
                else:
                    if (snp.IsPresent):
                        freqstr+='%0.3f'%snp.Freq
                        covstr+=str(snp.ReadCountRef)+';'+str(snp.ReadCountNonRef)
                    else:
                        freqstr+='X'
                        covstr+='X'
                freqstr+='|'
                covstr+='|'
            print('FREQUENCIES: '+freqstr)
            
            #Determine list of missing SNP info
            missingList=[]
            for snp in samplePositionInfo:
                if not(snp is None):
                    if not(snp.IsPresent):
                        missingList.append(snp.Id)
            if len(missingList)>0:
                StatDoMissing(SampleGenoTypeInfo.sampleId)#Currenly a hack
                self.CountMissing+=1
                raise CallingError('MissingData','')
            
            #determine mixedness
            mixedness=0
            for snp in samplePositionInfo:
                if not(snp is None):
                    mixedness=max(mixedness,min(snp.Freq,1-snp.Freq))
            print('MIXEDNESS '+str(mixedness))
            if mixedness<self.FreqErrorThreshold:#we assume a pure call
                call=self._CallPure(samplePositionInfo)
            else:#we assume a mixed call
                call=self._CallMixed(samplePositionInfo)
                resultList=[0]*len(self.variants)
            resultList=[0]*len(self.variants)
            for callItem in call:
                resultList[self.variantIndex[callItem['variantid']]]=callItem['frequency']
            #basic check
            if math.fabs(sum(resultList)-1.0)>0.00001:
                raise Exception('Variant frequencies do not sum to 1')
        except CallingError as e:
            print('*** CALLING ERROR ***'+e.tpe)
            self.Errors.append({'sampleid':SampleGenoTypeInfo.sampleId, 'type':e.tpe, 'frequencies':freqstr, 'coverages':covstr})
        return resultList
            
            
        
#A class that contains information about a SNP on the genome
class HaplotypeSNPInfo:
    def __init__(self,Id):
        self.Id=Id
        self.ChromosomeId=None
        self.Position=None
        self.Ref=None
        self.NonRef=None
    def DumpData(self):
        print(self.Id+' '+self.ChromosomeId+':'+str(self.Position)+' '+self.Ref+'>'+self.NonRef)
        
#A class that will call haplotypes on genotype data
class HaplotypeCaller:
    def __init__(self,SnpInfoProvider,RefGenome,Translator):
        self.SnpInfoProvider=SnpInfoProvider#A class that returns lists of snps in ranges
        self.RefGenome=RefGenome#should contain an instance of Genome
        self.Translator=Translator#should contain an instance of SequenceTranslator
        self.loci=[]#A list loci we will call, represented by instances of HaplotypeLocus
        self.GlobalObservedSNPList=[]
        self.GlobalObservedSNPMap={}
        
    def AddLocus(self,locus):
        self.loci.append(locus)
        
    def AddSNP(self,snp):
        if not(snp.Id in self.GlobalObservedSNPMap):
            self.GlobalObservedSNPList.append(snp)
            self.GlobalObservedSNPMap[snp.Id]=snp
        
    def DumpData(self):#Writes the elementary data to stdout
        print('\n\nLOCI')
        for locus in self.loci:
            print('\n\n###########################################################################')
            locus.DumpData()
        print('\n\nGLOBAL OBSERVED SNPS')
        for snp in self.GlobalObservedSNPList:
            snp.DumpData()
            
    def PrintStats(self):
        for locus in self.loci:
            locus.PrintStats()

    def DumpErrors(self,fle):
        for locus in self.loci:
            locus.DumpErrors(fle)

    def GetCalledItemIDs(self):
        result=[]
        for locus in self.loci:
            result=result+locus.GetCalledItemIDs()
        return result
            
    def Call(self,SampleGenoTypeInfo):
        result=[]
        for locus in self.loci:
            result=result+locus.Call(SampleGenoTypeInfo)
        return result




########################################################################################################################
# START OF THE MAIN BODY
########################################################################################################################

#The one and only reader that reads the SNP info from a database table
SnpInfoProvider=DataProviders.SNPInfoProvider_Database(meta)

#The one and only reference genome
refGenome=Genome()
refGenome.ReadFASTA(meta['SOURCEDIR']+'/{0}/sequences.dat'.format(meta['ORIGDIR']))
transl=SequenceTranslator()
        
#The one and only caller instance
caller=HaplotypeCaller(SnpInfoProvider,refGenome,transl)

            
#########################################################################################################################
# COLLECTING INFORMATION FROM THE DATA TABLE FILES
# note: ultimately, this will be read from database tables
#########################################################################################################################
tableHaplotypes=VTTable.VTTable()
tableHaplotypes.allColumnsText=True
tableHaplotypes.LoadFile(meta['SOURCEDIR']+'/Haplotypes/Haplotypes.txt')
tableHaplotypes.PrintRows(0,999)
haplotypes=tableHaplotypes.ToListOfMaps()

tableHaplotypeLoci=VTTable.VTTable()
tableHaplotypeLoci.allColumnsText=True
tableHaplotypeLoci.LoadFile(meta['SOURCEDIR']+'/Haplotypes/HaplotypeLoci.txt')
tableHaplotypeLoci.ConvertColToValue('PositionFirst')
tableHaplotypeLoci.ConvertColToValue('PositionLast')
tableHaplotypeLoci.ConvertColToValue('KodonOffset')
tableHaplotypeLoci.PrintRows(0,999)
haplotypeLoci=tableHaplotypeLoci.ToListOfMaps()

for locusinfo in haplotypeLoci:
    locus=HaplotypeLocus(caller,locusinfo['Id'],locusinfo['Name'])
    locus.SetRegion(locusinfo['ChromosomeId'],int(locusinfo['PositionFirst']),int(locusinfo['PositionLast']),int(locusinfo['KodonOffset']))
    for haplotype in haplotypes:
        if locus.Id==haplotype['LocusId']:
            variant=HaplotypeVariant(locus,haplotype['Name'])
            variant.SetSeqNucl(haplotype['Sequence'])
    
caller.DumpData()


#The one and only sample genotype data provider

usedSnpMap={id:0 for id in caller.GlobalObservedSNPMap}
#manually add 2 surrounding snps
usedSnpMap['MAL7:458990']=0
usedSnpMap['MAL7:459065']=0

SampleData=DataProviders.SampleInfoProvider(meta)
SampleGenoTypeData=DataProviders.SampleGenoTypeProvider_TabFile(usedSnpMap,meta)
#SampleGenoTypeData.DumpData('call')


#Calculate absence stats for each SNP
for snp in SampleGenoTypeData.SNPIds:
    missingcount=0
    totcount=0
    for sampleNr in range(len(SampleGenoTypeData.sampleIds)):
        totcount+=1
        if not SampleGenoTypeData.GetSampleSNP(sampleNr, snp).IsPresent:
            missingcount+=1
    print('Missing samples for '+snp+' : '+str(missingcount)+' (total='+str(totcount)+')');
    
#Calculate haplotype info for each sample
resultFile=open(meta['SOURCEDIR']+'/HaplotypeCalls.txt','w')
resultFile.write('SampleID')
result=caller.GetCalledItemIDs()
for rs in result:
    resultFile.write('\t'+rs)
resultFile.write('\n')
for sampleNr in range(len(SampleGenoTypeData.sampleIds)):
    genotypeInfo=SampleGenoTypeData.GetSampleGenoType(sampleNr)
    print('========= CALLING '+SampleGenoTypeData.sampleIds[sampleNr]+' ============================================================================================================');
    result=caller.Call(genotypeInfo)
    contribcount=0
    for rs in result:
        if rs>0:
            contribcount+=1
    if contribcount>1:
        resultFile.write(SampleGenoTypeData.sampleIds[sampleNr])
        for rs in result:
            if rs is None:
                resultFile.write('\t'+'-')
            else:
                resultFile.write('\t'+'%0.4f'%rs)
        resultFile.write('\n')
    print('')
    
resultFile.close()
print('')
caller.PrintStats()

errorFile=open(meta['SOURCEDIR']+'/HaplotypeCallingErrors.txt','w')
caller.DumpErrors(errorFile)
errorFile.close()

ReportMissing()

sys.exit()


















