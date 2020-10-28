


setwd("C:/Users/ahmet/Documents/R/rdata")



data1<-read.delim("C:/Users/ahmet/Desktop/IBT-Files/Fig3Iduimg50to150.csv", header = TRUE, sep = ",")
data1s<-data1[,4]
namesmtx1<-rep("EarlyReplicatedDNA",each=nrow(data1))



data2<-read.delim("C:/Users/ahmet/Desktop/IBT-Files/Fig3Brduimg50to150.csv", header = TRUE, sep = ",")
data2s<-data2[,4]
namesmtx2<-rep("LateReplicatedDNA",each=nrow(data2))

data3<-read.delim("C:/Users/ahmet/Desktop/IBT-Files/Fig3Phosimg50to150.csv", header = TRUE, sep = ",")
data3s<-data3[,4]
namesmtx3<-rep("Phoshphorus",each=nrow(data3))



# data5<-read.delim("C:/Users/ahmet/Desktop/IBT-Files/07132018IduBrrU2hresult-carbon12T.csv", header = TRUE, sep = ",")
# data5s<-data5[,4]
# namesmtx5<-rep("Carbon",each=nrow(data5))





Cellmtx <-as.matrix(cbind(data1s,data2s,data3s))
Cellmtx2 <-as.matrix(cbind(data1s,data2s))


colnames(Cellmtx)<-c("IdU.Replicated.DNA","BrdU.Replicated.DNA","Phosphorus")

Cellmtx<-eval(Cellmtx[rowSums(data.frame(Cellmtx) != 0) != 0, ] )
Cellmtx2<-eval(Cellmtx2[rowSums(data.frame(Cellmtx2) != 0) != 0, ] )



library(factoextra)
dist.eucl <- dist(scale(Cellmtx2[1:500,]), method = "euclidean")
#vermatrix<-as.matrix(append(excel.data[,1],excel.data[,2]))

fviz_dist(dist.eucl)



# X.dist <- dist(scale(Cellmtx[1:500,]))
# hier.cls <- hclust(X.dist, method = "ward.D2")
# plot(hier.cls,cex=.7)

library(corrplot)

Cellmtx<-data.frame(Cellmtx)


Cellmtx<-eval(Cellmtx[! Cellmtx$IdU.Replicated.DNA<3, ])
Cellmtx<-eval(Cellmtx[! Cellmtx$BrdU.Replicated.DNA<3, ])
#Cellmtx<-eval(Cellmtx[Cellmtx$Phoshphorus>3, ])

m<-cor(Cellmtx)
par(cex = 2)
corrplot(m, method="color",tl.col = "black",cl.offset="-0.9",cl.align.text='r')

Cellmtxmap<-log2(Cellmtx)+1

Cellmtxmap<-eval(Cellmtxmap[which(rowSums(Cellmtxmap) > 0),] )

Cellmtxmap<-(as.matrix(Cellmtxmap))

#nstall.packages("corrplot")
library(gplots)
library(ggplot2)
library(gplots)
library("RColorBrewer")

par(cex.main=1.7)

heatmap(Cellmtxmap[1:500,],
        
        col = colorpanel(100,"black","gray","red") 
)

par(cex.main=1.7)

heatmap.2(Cellmtxmap[1:500,],
          #cellnote = mat,  # same data set for cell labels
          main = "Subcellular map", # heat map title
          notecol="gray",      # change font color of cell labels to black
          trace="none",         # turns off trace lines inside the heat map
          margins =c(6,6),     # widens margins around plot
          col = colorpanel(100,"black","gray","red"), 
          #col = brewer.pal(11,"RdBu"),
          cexRow = 2,
          offsetRow = -0.4,
          cexCol=0.2,
          offsetCol = 0.3,
          adjCol=c(0.2,0.5),
          #srtCol=75,
          
          density.info = c("none"),
          key = TRUE,
          key.xlab = "log2(counts)",
          keysize = 1,
          
          ylab = NULL,
          labCol = FALSE)



#m<-m*10
#Filter correlation matrix
m[upper.tri(m,diag=T)]<-0
cutoff<-0.005
m[m<=cutoff]<-0

mat<-m




library(circlize)
circos.par(gap.degree = 8)
chordDiagram(mat, grid.col = 1:3, directional = TRUE, annotationTrack = "grid",
             preAllocateTracks = list(list(track.height = 0.05),
                                      list(track.height = 0.05)))
circos.trackPlotRegion(track.index = 1, panel.fun = function(x, y) {
  xlim = get.cell.meta.data("xlim")
  ylim = get.cell.meta.data("ylim")
  sector.index = get.cell.meta.data("sector.index")
  circos.text(mean(xlim), mean(ylim), sector.index, facing = "bending", niceFacing = TRUE, cex=2.5)
}, bg.border = NA)

#circos.trackPlotRegion(track.index = 2, panel.fun = function(x, y) {
 # circos.axis("bottom", major.tick.percentage = 0.2, labels.cex = 0.6)
#}, bg.border = NA)
circos.clear()

