t=read.table("C:/Data/Articles/PositiveSelection/DataSaturn/XPEHH/CEU_Reference/test.txt",header=T)
x=unlist(t["Start"])
y=unlist(t["Val"])
plot(x,y, cex=0.6, pch=16, xlim=c(55000000,58000000))
