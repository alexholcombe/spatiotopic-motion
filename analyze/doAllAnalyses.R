#This file analyses anonymized data provided by "loadAnonymiseSaveData.R" in exp-specific directory
#Working directory is set hopefully by Rproj file to directory that it's in.
setwd("/Users/alexh/Documents/vision/neuropsych_palinopsia_Michael_Beckett/Szinte_Cavanagh_Spatiotopic/psychopy_SzinteCavanagh/analyze/")
expName="123targets269objects" 
load("../data/MB.RData",verbose=TRUE) #E1 #returns dat
datE1 = dat
expName="SzinteCavanagh" 

# colsNotInE1 = setdiff(colnames(dat),colnames(datE1))
# datE1[,colsNotInE1] = -999 #dummy value
# colsNotInThisOne = setdiff(colnames(datE1),colnames(dat))
# dat[,colsNotInThisOne] = -999 #dummy value
# dat = rbind(dat,datE1)

source('analyzeMakeReadyForPlot.R') #returns fitParms, psychometrics, and function calcPctCorrThisSpeed
source('plotIndividDataWithPsychometricCurves.R') 
  #should also do it normalizing by subjects' speed limits
  source("analyze/extractThreshesAndPlot.R") #provides threshes, plots

  varName=paste("threshes_",iv,"_",expName,sep='') #combine threshes
  assign(varName,threshes)
  save(list=varName,file=paste("data/",varName,".Rdata",sep='')) #e.g. threshes_tf_123targets269objects.Rdata


factorsPlusSubject=c("numObjects","subject","direction","ecc","device") 

E2threshes<- ddply(E2, factorsPlusSubject,meanThreshold) #average over trialnum,startSpeed

#then plot
tit<-"E2threshesSpeed"
quartz(title=tit,width=2.8,height=2.9) #create graph of thresholds
g=ggplot(E2threshes, aes(x=numObjects-1, y=thresh, color=device, shape=factor(ecc)))
g<-g + xlab('Distractors')+ylab('threshold speed (rps)')
dodgeAmt=0.35
SEerrorbar<-function(x){ SEM <- sd(x) / (sqrt(length(x))); data.frame( y=mean(x), ymin=mean(x)-SEM, ymax=mean(x)+SEM ) }
g<-g+ stat_summary(fun.data="SEerrorbar",geom="point",size=2.5,position=position_dodge(width=dodgeAmt))
#g<-g+ stat_summary(fun.y=mean,geom="point",size=2.5,position=position_dodge(width=dodgeAmt))
g<-g+stat_summary(fun.data="SEerrorbar",geom="errorbar",width=.25,position=position_dodge(width=dodgeAmt)) 
g=g+theme_bw() #+ facet_wrap(~direction)
g<-g+ coord_cartesian( ylim=c(1.0,2.5), xlim=c(0.6,2.4))
g<-g+ scale_x_continuous(breaks=c(1,2))
g<-g+ theme(axis.title.y=element_text(vjust=0.22))
g<-g+theme(panel.grid.minor=element_blank(),panel.grid.major=element_blank())# hide all gridlines.
show(g)
ggsave( paste('figs/',tit,'.png',sep='') )
