
#install.packages("xlsx")
#library("xlsx")

setwd("C:/Users/ahmet/Documents/R/rdata")


excel.data <- read.xlsx("TranscriptioninhibitstatsNormalized.xlsx", sheetIndex = 1,header=FALSE)

colnames(excel.data)<-c("Normal","Alpha-Amanitin")

vermatrix<-as.matrix(append(excel.data[,1],excel.data[,2]))



colnameslist<-colnames(excel.data)

namesmtx1<-rep(colnameslist[1],each=nrow(excel.data))
namesmtx2<-rep(colnameslist[2],each=nrow(excel.data))

namesmtxAll<-as.matrix(append(namesmtx1,namesmtx2))

# png("C:/Users/ahmet/Documents/R/rdata/mathmibiresults/REPLICATION.png",    # create PNG for the heat map
#     width = 10*500,        # 5 x 300 pixels
#     height = 8*500,
#     res = 400,            # 300 pixels per inch
#     pointsize = 16)        # smaller font size

genesumname<-cbind(vermatrix,namesmtxAll)
rownames(genesumname) <- NULL
colnames(genesumname)<-c("Transcription","Treatment")
genesumname<-as.data.frame(genesumname)
genesumname$Treatment<-as.factor(genesumname$Treatment)
genesumname$Transcription<-as.numeric(as.character(genesumname$Transcription))
head(genesumname)

pval<-wilcox.test(as.matrix(excel.data[,1]),as.matrix(excel.data[,2]))
# install.packages("ggsignif") 
library(ggplot2)
library(ggsignif)


p<-ggplot(genesumname, aes(x=Treatment, y=Transcription,fill=Treatment))+  geom_boxplot(alpha=0.5)+theme(text = element_text(size=55))+theme(legend.position="none",legend.text = element_text( size=30),legend.title = element_blank())

p + geom_jitter(shape=16, position=position_jitter(0.2),colour="gray48",alpha=0.2)

p+geom_signif(comparisons = list(c("Normal","Alpha-Amanitin")), 
              map_signif_level=TRUE,test="wilcox.test",textsize=15)+ ylim(0, 13)+geom_jitter(shape=16, position=position_jitter(0.2),colour="gray48",alpha=0.5)

# dev.off()

