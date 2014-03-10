import gzip

regionsfile = 'regions1'

regions = []

class Region:
    def __init__(self, line):
	cols = line.split('\t')
	self.name = cols[0]
	cols = cols[1].split(';')
	self.reg_chroms = []
	self.reg_starts = []
	self.reg_stops = []
	for col in cols:
	    self.reg_chroms.append(col.split(':')[0])
	    self.reg_starts.append(int(col.split(':')[1].split('-')[0]))
	    self.reg_stops.append(int(col.split(':')[1].split('-')[1]))
	self.regcount=len(self.reg_chroms)

    def ToString(self):
	st = ''
	for i in range(self.regcount):
	    st += self.reg_chroms[i]+':'+str(self.reg_starts[i])+'-'+str(self.reg_stops[i])+'  '
	return st

with open(regionsfile) as fl:
    for line in fl:
	regions.append(Region(line.rstrip('\r\n')))
	print(regions[len(regions)-1].ToString())
	

filename = 'pysamstats/ARC3/PH0128-CW.coverage.txt.gz'

colnr = 3

linecount = 0
with gzip.open(filename) as fl:
    fl.readline()
    for line in fl:
	cols = line.rstrip('\r\n').split('\t')
	chrom = cols[0]
	pos = int(cols[1])
	val = float(cols[colnr])
	print(str(cols))
	linecount += 1
	if linecount >= 20:
	     break
