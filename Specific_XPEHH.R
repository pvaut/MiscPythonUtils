

stattype="_AvVal"
maxval=7
chromnr="17"

minpos=5.2e7
maxpos=5.8e7

basepath="C:/Data/Articles/PositiveSelection/DataSaturn/XPEHH/_PV_ChromoSplit"

filename=paste(basepath,"/XPEHH_windowed_",chromnr,".txt",sep="")

t=read.table(filename, header=T)

x=unlist(t["WinStart"])


##outputfile=paste(basepath,"/plot",chromnr,stattype,".png",sep="")
##png(file=outputfile,width=1600,height=600)

plot.new()

first<-1
pops=c("YRI","Malawi","Mandinka","Wolof","Fula","Jola","Akan","Northerner")
colors=c(rgb(1,0,0,0.5),rgb(0,0,1,0.5),rgb(0,0.5,0,0.5),rgb(0.5,0.3,0,0.5),rgb(0,0.5,0.5,0.5),rgb(0.75,0.0,0.75,0.5),rgb(0,0.7,0.8,0.5),rgb(0.8,0.5,0,0.5))

nr=0
for (pop in pops) {
   colname<-paste(pop,stattype,sep="")
   y=unlist(t[colname])
   if (first) plot(x,y, cex=0.8, col=colors[nr], pch=16, type="o", xlim=c(minpos,maxpos), ylim=c(0,maxval), ann=FALSE)
   if (!first) lines(x,y, cex=0.8, col=colors[nr], pch=16, type="o")
   first<-0
   nr=nr+1
}

##axis(1,at=10000000*(0:40))
##axis(2,0:maxval)


title(ylab=paste("XPEHH chr=",chromnr,stattype), col.lab=rgb(0,0,0))


grid()

legend(minpos, maxval, pops, cex=1.0, 
   colors, pch=16);

##dev.off()
