
setwd("C:/Users/ahmet/Documents/R/rdata")
options(java.parameters = "-Xmx1024m")
memory.limit(size=60000)

#install.packages("xlsx")
library("xlsx")
library(gplots)
library(ggplot2)
library(gplots)
library("RColorBrewer")

#Read values from excel files for spatial chromatin neighborhood map

excel.data1 <- read.xlsx("GTchromatinspatialtissue4p300-data1.xlsx", sheetIndex = 1,header=FALSE)
colnames(excel.data1)<-c("Dnax","Dnay","Dnaval")

excel.data2 <- read.xlsx("GTchromatinspatialtissue4p300-data2.xlsx", sheetIndex = 1,header=FALSE)
colnames(excel.data2)<-c("Prox","Proy","Proval")

excel.data3 <- read.xlsx("GTchromatinspatialtissue4p300-data3.xlsx", sheetIndex = 1,header=FALSE)
colnames(excel.data3)<-c("Dnaxall","Dnayall","Dnavalall")

excel.data4 <- read.xlsx("GTchromatinspatialtissue4p300-data4.xlsx", sheetIndex = 1,header=FALSE)
colnames(excel.data4)<-c("Point1","Point2","Point3","Trix","Triy","Triperim")


#now create size(excel.data4)=6081 vs G1:1,G2:2,G3:3,T1:4,T2:5,T3:6,and Trix:7,Triy:8
mtx1<-as.data.frame(excel.data1)
mtx<-as.data.frame(excel.data4)
mtxdna<-as.data.frame(excel.data3)

xlength<-nrow(mtx)
pthresh<-nrow(mtx1)

newdata<-matrix(0,8,xlength)
tt<-4
gg<-1

for (i in 1:xlength){
  
  point1pos<-data.matrix(mtx[i,1])
  dnaval1<-data.matrix(mtxdna[point1pos,3])
  if (point1pos<pthresh+1){
    newdata[tt,i]<-log2(dnaval1)
    eval.parent(substitute(tt <- tt + 1))
  }
  else if (point1pos>pthresh){newdata[gg,i]<-log2(dnaval1)
  eval.parent(substitute(gg <- gg + 1))}
  
  point2pos<-data.matrix(mtx[i,2])
  dnaval2<-data.matrix(mtxdna[point2pos,3])
  if (point2pos<pthresh+1){
    newdata[tt,i]<-log2(dnaval2)
    eval.parent(substitute(tt <- tt + 1))
  }
  else if (point2pos>pthresh) {newdata[gg,i]<-log2(dnaval2)
  eval.parent(substitute(gg <- gg + 1))}
  
  
  point3pos<-data.matrix(mtx[i,3])
  dnaval3<-data.matrix(mtxdna[point3pos,3])
  if (point3pos<pthresh+1){
    newdata[tt,i]<-log2(dnaval3)
    eval.parent(substitute(tt <- tt + 1))
  }
  else if (point3pos>pthresh){newdata[gg,i]<-log2(dnaval3)
  eval.parent(substitute(gg <- gg + 1))}  
  
  trixpos<-data.matrix(mtx[i,4])
  newdata[7,i]<-log2(trixpos)
  
  
  triypos<-data.matrix(mtx[i,5])
  newdata[8,i]<-log2(triypos)  
  
  eval.parent(substitute(tt <- 4))
  eval.parent(substitute(gg <- 1))
}

row.names(newdata)<-c("Sulphur1","Sulphur2","Sulphur3","Phos1","Phos2","Phos3","X-Spatial","Y-Spatial")

par(cex.main=1.7)

heatmap.2(newdata,
          #cellnote = mat,  # same data set for cell labels
          main = "2D molecular neighborhood map in tissues", # heat map title
          notecol="gray",      # change font color of cell labels to black
          trace="none",         # turns off trace lines inside the heat map
          margins =c(8,8),     # widens margins around plot
          col = colorpanel(100,"black","gray","green"), 
          #col = brewer.pal(11,"RdBu"),
          cexRow = 2,
          offsetRow = -0.4,
          cexCol=0.2,
          offsetCol = 0.3,
          adjCol=c(0.2,0.5),
          #srtCol=75,
          dendrogram="column", 
          Rowv=FALSE,
          density.info = c("none"),
          key = TRUE,
          key.xlab = "log2(counts)",
          keysize = 1,
          xlab=NULL,
          ylab = NULL,
          labCol = FALSE)


#heatmap(newdata, Rowv=NULL,col = colorpanel(100,"black","gray","red"))

