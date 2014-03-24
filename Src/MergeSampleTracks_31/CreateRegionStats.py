import gzip
import Utils.config as config
import Utils.DQXMathUtils as DQXMathUtils
import os
import sys

if len(sys.argv) > 1:
    filename = config.basedir + '/pysamstats/' + sys.argv[1]
else:
    filename = config.basedir + '/pysamstats/ARC3/PH0128-CW.coverage.txt.gz'

maxlinecount = 100000
#maxlinecount = -1




regionsfile = 'regions2'

regions = []

class Region:
    def __init__(self, line):
        cols = line.split('\t')
        self.name = cols[0]
        if cols[1] == 'all':
            self.all = True
        else:
            self.all = False
            self.reg_chroms = []
            self.reg_starts = []
            self.reg_stops = []
            if cols[1][0:5] == 'file:':
                print('reading regions from file')
                with open(config.basedir + '/' + cols[1][5:]) as fp:
                    for lne in fp:
                        self.reg_chroms.append(lne.split(' ')[0])
                        self.reg_starts.append(int(lne.split(' ')[1]))
                        self.reg_stops.append(int(lne.split(' ')[2]))
            else:
                cols = cols[1].split(';')
                for col in cols:
                    self.reg_chroms.append(col.split(':')[0])
                    self.reg_starts.append(int(col.split(':')[1].split('-')[0]))
                    self.reg_stops.append(int(col.split(':')[1].split('-')[1]))
            self.regcount=len(self.reg_chroms)
        self.stat = DQXMathUtils.BasicStatAcummulator(not(self.all))

    def ToString(self):
        st = self.name+' '
        if (self.all):
            st += 'All'
        else:
            for i in range(self.regcount):
                st += self.reg_chroms[i]+':'+str(self.reg_starts[i])+'-'+str(self.reg_stops[i])+'  '
        st += ' --> '
        st += 'Count: {0}, Mean: {1}, Median: {2}, Stdev: {3}'.format(
            self.stat.getN(),
            self.stat.getMean(),
            self.stat.getMedian(),
            self.stat.getStDev()
        )
        return st

    def IsInside(self, chrom, pos):
        if self.all:
            return True
        for i in range(self.regcount):
            if self.reg_chroms[i] == chrom:
                if (pos>=self.reg_starts[i]) and (pos<=self.reg_stops[i]):
                    return True
        return False

with open(regionsfile) as fl:
    for line in fl:
        regions.append(Region(line.rstrip('\r\n')))



#Get sample id from filename
sampleid = os.path.split(filename)[1].split('.')[0]
print('SAMPLEID: '+sampleid)

colindex = 2

linecount = 0
with gzip.open(filename) as fl:
    print(fl.readline())
    for line in fl:
        cols = line.rstrip('\r\n').split('\t')
        chrom = cols[0]
        pos = int(cols[1])
        val = float(cols[colindex])
        #print(str(cols))
        for region in regions:
            if region.IsInside(chrom, pos):
                region.stat.add(val)
        linecount += 1
        if linecount%50000 == 0:
            print(linecount)
        if (maxlinecount > 0) and (linecount >= maxlinecount):
             break


output = []
for region in regions:
    output.append(region.stat.getMean())
    output.append(region.stat.getMedian())
    output.append(region.stat.getStDev())
    output.append(region.stat.getQuantileRange(0.25))
    output.append(region.stat.getQuantileRange(0.05))
    output.append(region.stat.getMin())
    output.append(region.stat.getMax())
    print(region.ToString())
output = sampleid + '\t' + '\t'.join([str(val) for val in output])
print('OUTPUT:' + output)

if not(os.path.exists('results')):
    os.makedirs('results')


with open(os.path.join('results', sampleid), 'w') as fp:
    fp.write(output+'\n')

