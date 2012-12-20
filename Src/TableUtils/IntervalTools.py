
class IntervalOverlapFinder:
    def __init__(self):
        self.starts=[]
        self.ends=[]
        self.keys=[]
        self.currentmaxend=0
        self.maxends=[]#for each interval, maintains the maximum end position of this interval or any interval on the left of it
        
    #NOTE: interval have to be added with increasing start position
    def AddInterval(self, start, end, key):
        if (len(self.starts)>0) and (start<self.starts[len(self.starts)-1]):
            raise Exception('Please add intervals in ordered form according to start position')
        #if (len(self.maxends)>0) and (self.maxends[len(self.maxends)-1]>start): print('NOTIFY: THERE IS OVERLAP')
        self.currentmaxend=max(self.currentmaxend,end)
        self.starts.append((start))
        self.ends.append(end)
        self.keys.append(key)
        self.maxends.append(self.currentmaxend)
        
    def FindOverlapsNaive(self, teststart, testend):
        result=[]
        for inr in range(0,len(self.starts)):
            if (teststart<=self.ends[inr]) and (testend>self.starts[inr]):
                result.append(self.keys[inr])
        return(result)
    
    def FindOverlapsFast(self, teststart, testend):
        #using binary intersection, find leftmost interval that lies completely on the right of the test interval
        result=[]
        i1=0
        i2=len(self.starts)-1
        if self.starts[i1]>testend:#no overlap because test interval lies left of leftmost interval
            return(result)
        if (self.starts[i2]<testend):#rightmost interval starts left of test interval, so we simply begin with this one
            lastscaninterval=i2
        else:#do a binary search to find the rightmost interval that is not completely right of the test interval
            while i2>i1+1:
                im=int((i1+i2)/2)
                if self.starts[im]<testend:
                    i1=im
                else:
                    i2=im
            lastscaninterval=i1#this is the rightmost interval that is not positioned completely right of the test interval
            #some sanity checks:
            if (self.starts[lastscaninterval]>testend): raise Exception('Ouch1! itv={0}'.format(lastscaninterval))
            if (lastscaninterval<len(self.starts)-1) and (self.starts[lastscaninterval+1]<testend-0.5): 
                raise Exception('Ouch2! itv={0} {1}<{2}'.format(lastscaninterval,self.starts[lastscaninterval+1],testend))
            
        #loop over all interval to the left, starting with lastscaninterval
        #and repeat this until maxends of the interval is smaller than start position of test interval
        #(meaning that no interval to the left ends beyond start of test interval) 
        finished=False
        while not(finished):
            if (teststart<=self.ends[lastscaninterval]) and (testend>=self.starts[lastscaninterval]):
                result.append(self.keys[lastscaninterval])
            lastscaninterval=lastscaninterval-1
            if (lastscaninterval<0) or (self.maxends[lastscaninterval]<teststart):
                finished=True
            
        #to be nice, we invert the match list so that we have again the original ordering
        result.reverse()    
            
#        #do the comparison test with the naive method
#        result2=self.FindOverlapsNaive(teststart, testend)
#        if result!=result2:
#            raise Exception('Ouch! fast method result does not match naive method result: '+str(result)+' '+str(result2))
        
        return(result)
