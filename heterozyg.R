

filename="C:/Data/Tmp/output.txt"
filename_random="C:/Data/Tmp/output_random.txt"


t=read.table(filename, header=T)
combined=unlist(t["Het"])
single=unlist(t["SHet"])


tr=read.table(filename_random, header=T)
combined_random=unlist(tr["Het"])
single_random=unlist(tr["SHet"])

pts <- c(seq(0,0.65, .01))

h_combined <- hist(combined, breaks=pts, plot=FALSE)
h_single <- hist(single, breaks=pts, plot=FALSE)


h_combined_random <- hist(combined_random, breaks=pts, plot=FALSE)
h_single_random <- hist(single_random, breaks=pts, plot=FALSE)


plot(h_combined_random$counts, log="y", pch=21, col="blue",
    yaxt="n",
    xlab="Heterozygocity (%)", ylab="Count (log)") 

axis(2, at = c(1,10,100,1000,10000,100000))

points(h_single_random$counts,  pch=21, col="red") 



points(h_combined$counts, pch=20, col="blue") 

points(h_single$counts, pch=20, col="red") 

