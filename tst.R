t=read.table("C:/Data/Articles/PositiveSelection/DataSaturn/XPEHH//_PV_XPEHHwindowed.txt", header=T)

x=unlist(t["WinStart"])
y=unlist(t["Fula_AvVal"])

##x=unlist(t[4])
##y=unlist(t[5])



##pdf("C:\\Users\\pvaut\\workspace\\PythonTest01\\rs01.pdf")
plot(x,y, cex=0.5, col=rainbow(1,alpha=0.3), pch=16, type="o")
##dev.off()