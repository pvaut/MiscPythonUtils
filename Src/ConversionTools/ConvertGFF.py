

class GFFParser:
    def __init__(self):
        self.features=[]

    def GetParentFeature(self,feat):
        parentid=feat['parentid']
        if len(parentid)==0:
            return None
        key=feat['seqid']+parentid
        if not(key in self.featindex):
            return None
        idx=self.featindex[key]
        #print(idx)
        return self.features[idx]

    def parseGTF(self,filelist):
        #read the feature list
        self.features=[]
        self.featindex={}
        for filename in filelist:
            print('processing file '+filename)
            f=open(filename,'r')
            for line in f.readlines():
#                if len(self.features)>20000: break#!!!
                line=line.rstrip('\n')
                if line[0]!='#':
                    parts=line.split('\t')
                    feattype=parts[2]
                    if (feattype=='CDS') or (feattype=='exon'):
                        if len(self.features)%1000==0: print('read: '+str(len(self.features)))
                        feat={}
                        feat['nr']=len(self.features)
                        feat['children']=[]
                        feat['seqid']='chr'+parts[0]
                        feat['type']=feattype
                        feat['start']=int(parts[3])
                        feat['end']=int(parts[4])
                        attribs=parts[8].split(';')
                        feat['id']=''
                        feat['parentid']=''
                        feat['name']=''
                        for attribstr in attribs:
                            attribstr=attribstr.lstrip()
                            attribstr=attribstr.rstrip()
                            #                            prt=attribstr.partition(' "')
                            key,sp,value=attribstr.partition(' "')
                            value=value[:-1]
                            if feattype=='CDS':
                                if key=='gene_id': feat['id']=value
                                if key=='gene_name': feat['name']=value
                                feat['type']='gene'
                            else:
                                if key=='gene_id': feat['parentid']=value
                        self.features.append(feat)
            f.close()

    def parseGFF(self,filelist):
        #read the feature list
        self.features=[]
        for filename in filelist:
            print('processing file '+filename)
            f=open(filename,'r')
            header=f.readline().rstrip('\n')
            if header!='##gff-version 3':
                raise Exception('Invalid GFF file')
            for line in f.readlines():
                line=line.rstrip('\n')
                if line=='##FASTA':
                    break
                if line[0]!='#':
                    parts=line.split('\t')
                    feat={}
                    feat['children']=[]
                    feat['seqid']=parts[0]
                    feat['type']=parts[2]
                    feat['start']=int(parts[3])
                    feat['end']=int(parts[4])
                    attribs=parts[8].split(';')
                    feat['id']=''
                    feat['parentid']=''
                    feat['name']=''
                    for attribstr in attribs:
                        if '=' in attribstr:
                            key,value=attribstr.split('=')
                            if key=='ID': feat['id']=value
                            if key=='Parent': feat['parentid']=value
                            if key=='Name': feat['name']=value
                    self.features.append(feat)
            f.close()

    def Process(self):

        #remove duplicates
        print('removing duplicates')
        dind={}
        featnr=0
        while featnr<len(self.features):
            feat=self.features[featnr]
            key=feat['seqid']+feat['id']
            if (feat['type']=='gene') and (key in dind):
                origfeat=self.features[dind[key]]
                origfeat['start']=min(origfeat['start'],feat['start'])
                origfeat['end']=max(origfeat['end'],feat['end'])
                self.features.pop(featnr)
            else:
                dind[key]=featnr
                featnr+=1

        print('building index')
        for i in range(len(self.features)):
            self.features[i]['nr']=i
            #Build an index
        self.featindex={}
        for feat in self.features:
            if feat['id'] in self.featindex:
                raise Exception('Duplicate feature')
            self.featindex[feat['seqid']+feat['id']]=feat['nr']

        #extending genes with exon regions
        print('extending')
        for feat in self.features:
            myfeat=feat
            if myfeat['type']=='exon':
                parentfeat=self.GetParentFeature(myfeat)
                if parentfeat!=None:
                    if parentfeat['end']<feat['end']:
                        print('Right extending {0} from {1} to {2}'.format(parentfeat['id'],parentfeat['end'],feat['end']))
                        parentfeat['end']=feat['end']
                    if parentfeat['start']>feat['start']:
                        print('Left extending {0} from {1} to {2}'.format(parentfeat['id'],parentfeat['start'],feat['start']))
                        parentfeat['start']=feat['start']



        #collect children of each feature
        for feat in self.features:
            myfeat=feat
            while self.GetParentFeature(myfeat)!=None:
                myparent=self.GetParentFeature(myfeat)
                myparent['children'].append(feat)
                myfeat=myparent
            myparent=self.GetParentFeature(feat)


    def save(self,filename):
        print('saving')
        f=open(filename,'w')
        for feat in self.features:
            if (feat['type']=='gene'):
                f.write(feat['seqid']+'\t')
                f.write(str(feat['start'])+'\t')
                f.write(str(feat['end'])+'\t')
                f.write(feat['id']+'\t')
                f.write(''+'\t')
                f.write(feat['type']+'\t')
                f.write(feat['name'])
                f.write('\n')
                for child in feat['children']:
                    if child['type']=='exon':
                        f.write(child['seqid']+'\t')
                        f.write(str(child['start'])+'\t')
                        f.write(str(child['end'])+'\t')
                        f.write(child['id']+'\t')
                        f.write(feat['id']+'\t')
                        f.write(child['type']+'\t')
                        f.write(child['name'])
                        f.write('\n')
        f.close()



#chromlist=range(1,15)
#basepath="C:/Data/Genomes/Plasmodium"
#filelist=['{0}/Pf3D7_{1}.gff'.format(basepath,str(nr).zfill(2)) for nr in chromlist]
#parser=GFFParser()
#parser.parseGFF(filelist)
#parser.Process()
#parser.save('{0}/features.txt'.format(basepath))


basepath="C:/Data/Genomes/Human"
filelist=['{0}/Homo_sapiens.GRCh37.68.gtf'.format(basepath)]
parser=GFFParser()
parser.parseGTF(filelist)
parser.Process()
parser.save('{0}/features.txt'.format(basepath))