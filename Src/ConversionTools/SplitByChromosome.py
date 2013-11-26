import sys

basedir='.'

#============= FAKE STUFF FOR DEBUGGING; REMOVE FOR PRODUCTION ==============
#basedir='C:/Data/Test/Genome/Test/T2'
#sys.argv=['','Uniqueness']
#============= END OF FAKE STUFF ============================================


if len(sys.argv)<2:
    print('Usage: COMMAND Sourcefilename')
    print('   Sourcefilename= file containing the source data, without the ".txt" extension')
    sys.exit()

filename=sys.argv[1]



ifile=open(basedir+'/'+filename+'.txt','r')
chromoname=''
while True:
    line=ifile.readline()
    if not(line):
        break
    line=line.rstrip('\n')
    comps=line.split('\t')
    if chromoname!=comps[0]:
        if chromoname:
            ofile.close()
        chromoname=comps[0]
        print('Reading chromosome {0}'.format(chromoname))
        ofile=open(basedir+'/'+chromoname+'.txt','w')
        ofile.write('Position\t{0}\n'.format(filename))
    if (len(line)>0) and chromoname:
        ofile.write('{0}\t{1}\n'.format(comps[1],comps[2]))

ifile.close()
ofile.close()
