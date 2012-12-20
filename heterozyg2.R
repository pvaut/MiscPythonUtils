

filename="C:/Data/Tmp/output.txt"

t=read.table(filename, header=T)
conc=unlist(t["ConcLen"])
disc=unlist(t["DiscLen"])

pts <- c(seq(0,12, .25))



h1 <- hist(conc, breaks=30, plot=FALSE)
plot(h1$counts, pch=20, col="blue",
 xlab="Average max. poly(A,T) length", ylab="Count")
lines(h1$counts, col="blue")


h2 <- hist(disc, breaks=30,  plot=FALSE)
points(h2$counts, pch=20, col="red")
lines(h2$counts, col="red")
