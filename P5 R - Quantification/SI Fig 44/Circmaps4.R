





setwd("C:/Users/ahmet/Documents/R/rdata")



data1<-read.delim("C:/Users/ahmet/Desktop/IBT-Files/062730mIdu30mBrduresult-IduAllM.csv", header = TRUE, sep = ",")
data1s<-data1[,4]
namesmtx1<-rep("EarlyReplicatedDNA",each=nrow(data1))



data2<-read.delim("C:/Users/ahmet/Desktop/IBT-Files/062730mIdu30mBrduresult-BrduAllM.csv", header = TRUE, sep = ",")
data2s<-data2[,4]
namesmtx2<-rep("LateReplicatedDNA",each=nrow(data2))

data3<-read.delim("C:/Users/ahmet/Desktop/IBT-Files/062730mIdu30mBrduresult-PhosAllM.csv", header = TRUE, sep = ",")
data3s<-data3[,4]
namesmtx3<-rep("Phoshphorus",each=nrow(data3))

data4<-read.delim("C:/Users/ahmet/Desktop/IBT-Files/062730mIdu30mBrduresult-SulphurAllM.csv", header = TRUE, sep = ",")
data4s<-data4[,4]
namesmtx4<-rep("Proteins",each=nrow(data4))

# data5<-read.delim("C:/Users/ahmet/Desktop/IBT-Files/07132018IduBrrU2hresult-carbon12T.csv", header = TRUE, sep = ",")
# data5s<-data5[,4]
# namesmtx5<-rep("Carbon",each=nrow(data5))



Cellmtx <-as.matrix(cbind(data1s,data2s,data3s,data4s))
Cellmtx2 <-as.matrix(cbind(data1s,data2s))



colnames(Cellmtx)<-c("Early.Replicated.DNA","Late.Replicated.DNA","Phosphorus","Proteins")
colnames(Cellmtx2)<-c("Early.Replicated.DNA","Late.Replicated.DNA")

Cellmtx<-eval(Cellmtx[rowSums(data.frame(Cellmtx) != 0) != 0, ] )
Cellmtx2<-eval(Cellmtx2[rowSums(data.frame(Cellmtx2) != 0) != 0, ] )


#install.packages("factoextra")
require(gplots)
library(factoextra)
dist.eucl <- dist(scale(Cellmtx2[1:500,]), method = "euclidean")
#vermatrix<-as.matrix(append(excel.data[,1],excel.data[,2]))

fviz_dist(dist.eucl)
fviz_pca(as.matrix(Cellmtx2))


#vermatrix<-as.matrix(append(excel.data[,1],excel.data[,2]))

library(corrplot)

Cellmtx<-data.frame(Cellmtx)


Cellmtx<-eval(Cellmtx[! Cellmtx$Early.Replicated.DNA<0, ])
Cellmtx<-eval(Cellmtx[! Cellmtx$Late.Replicated.DNA<2, ])
#Cellmtx<-eval(Cellmtx[! Cellmtx$Phosphorus<100, ])


# Cellmtx<-eval(Cellmtx[Cellmtx$Phosphorus>25, ])
# Cellmtx<-eval(Cellmtx[Cellmtx$New.RNA>3, ])
# Cellmtx<-eval(Cellmtx[Cellmtx$Replicated.DNA>5, ])



m<-cor(Cellmtx)

par(cex = 2)
corrplot(m, method="color",tl.col = "black",cl.offset="-0.8",cl.align.text='r')

install.packages("qgraph")

library(qgraph)

Q <- qgraph(cor(m),layout = "spring")
title("Subcell correlations", line = 2.5)



Cellmtxmap<-log2(Cellmtx)+1

Cellmtxmap<-eval(Cellmtxmap[which(rowSums(Cellmtxmap) > 0),] )

Cellmtxmap<-(as.matrix(Cellmtxmap))

#nstall.packages("corrplot")
library(gplots)
library(ggplot2)
library(gplots)
library("RColorBrewer")

par(cex.main=1.7)

#heatmap(Cellmtxmap,

#          col = colorpanel(100,"black","gray","red") 
#        )

par(cex.main=1.7)

#heatmap.2(Cellmtxmap,
# #cellnote = mat,  # same data set for cell labels
# main = "Subcellular map", # heat map title
# notecol="gray",      # change font color of cell labels to black
# trace="none",         # turns off trace lines inside the heat map
# margins =c(6,6),     # widens margins around plot
# col = colorpanel(100,"black","gray","red"), 
# #col = brewer.pal(11,"RdBu"),
# cexRow = 2,
# offsetRow = -0.4,
# cexCol=0.2,
# offsetCol = 0.3,
# adjCol=c(0.2,0.5),
# #srtCol=75,
# 
# density.info = c("none"),
# key = TRUE,
# key.xlab = "log2(counts)",
# keysize = 1,
# 
# ylab = NULL,
# labCol = FALSE)



#m<-m*10
#Filter correlation matrix
m[upper.tri(m,diag=T)]<-0
cutoff<-0.005
#m[m<=cutoff]<-0

mat<-m




library(circlize)
circos.par(gap.degree = 8)
chordDiagram(mat, grid.col = 1:4, directional = TRUE, annotationTrack = "grid",
             preAllocateTracks = list(list(track.height = 0.05),
                                      list(track.height = 0.05)))
circos.trackPlotRegion(track.index = 1, panel.fun = function(x, y) {
  xlim = get.cell.meta.data("xlim")
  ylim = get.cell.meta.data("ylim")
  sector.index = get.cell.meta.data("sector.index")
  circos.text(mean(xlim), mean(ylim), sector.index, facing = "bending", niceFacing = TRUE, cex=1)
}, bg.border = NA)

#circos.trackPlotRegion(track.index = 2, panel.fun = function(x, y) {
#  circos.axis("bottom", major.tick.percentage = 0.2, labels.cex = 0.4)
#}, bg.border = NA)
circos.clear()

