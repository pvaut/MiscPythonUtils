outputfile="$OUTPUTFILE$"
labelstring="$LABELSTRING$"
centerpos=$CENTERPOS$


pops=c("YRI","Malawi","Mandinka","Wolof","Fula","Jola","Akan","Northerner")

alpha=1
colors=c(rgb(1,0,0,alpha),rgb(0,0,1,alpha),rgb(0,0.5,0,alpha),rgb(0.5,0.3,0,alpha),rgb(0,0.5,0.5,alpha),rgb(0.75,0.0,0.75,alpha),rgb(0,0.7,0.8,alpha),rgb(0.8,0.5,0,alpha))

##pops=c("YRI")

basepath="C:/Data/Articles/PositiveSelection/DataSaturn"

minval=-5
maxval=5

png(file=outputfile,width=1600,height=800)
plot.new()




first=1
nr=1
for (pop in pops) {

   filename=paste(basepath,"/ChartData/IHS/",pop,".txt",sep="")
   t=read.table(filename, header=T)
   x=unlist(t["Posit"])
   y=unlist(t["StatVal"])

   colname<-paste(pop,"",sep="")
   if (first) plot(x,y, cex=0.6, col=colors[nr], pch=16, ylim=c(minval,maxval), ann=FALSE, cex.axis=1.3)
   if (!first) points(x,y, cex=0.6, col=colors[nr], pch=16,)
   first=0
   nr=nr+1
}


title(ylab=labelstring, col.lab=rgb(0,0,0),cex.lab=1.3)


#grid()
abline(v=centerpos, lty=3)
abline(v=centerpos-100000, lty=3)
abline(v=centerpos+100000, lty=3)


##legend(1, 4.0, pops, cex=1.0, 
##   colors, pch=16);


dev.off()

