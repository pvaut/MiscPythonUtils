import sys

basedir='.'

#============= FAKE STUFF FOR DEBUGGING; REMOVE FOR PRODUCTION ==============
#basedir='C:/Data/Test/Genome/Test/T3'
#sys.argv=['','RefGenome.fa']
#============= END OF FAKE STUFF ============================================

if len(sys.argv)<2:
    print('Usage: COMMAND Sourcefilename')
    print('   Sourcefilename= fasta file')
    sys.exit()

filename=sys.argv[1]


ifile=open(basedir+'/'+filename,'r')

chromoname=''
while True:
    line=ifile.readline()
    if not(line):
        break
    line=line.rstrip('\n')
    if line[0]=='>':
        if chromoname:
            ofile.close()
        chromoname=line[1:]
        print('Reading chromosome {0}'.format(chromoname))
        ofile=open(basedir+'/'+chromoname+'.txt','w')
        ofile.write('Position\tBase\n')
        posit=0
    else:
        if chromoname:
            for base in line:
                posit+=1
                ofile.write(str(posit))
                ofile.write('\t')
                ofile.write(base)
                ofile.write('\n')

ifile.close()
ofile.close()
