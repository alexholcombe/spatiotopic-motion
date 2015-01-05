#This file analyses anonymized data provided by "loadAnonymiseSaveData.R" in exp-specific directory
#Working directory is set hopefully by Rproj file to directory that it's in.
setwd("/Users/alexh/Documents/vision/neuropsych_palinopsia_Michael_Beckett/Szinte_Cavanagh_Spatiotopic/psychopy_SzinteCavanagh/analyze/")
expName="123targets269objects" 
load("../data/MB.RData",verbose=TRUE) #E1 #returns dat
datMB <- dat
load("../data/E1.RData",verbose=TRUE) #E1 #returns dat
datE1 = dat
datMB$ran=NA; datMB$order=NA #because wasnt saved by psychopy-native, I guess
#dat=version.merge(datMB,datE1,verbose=TRUE) #better than R-base "merge" command
dat=rbind(datMB,datE1)
expName="SzinteCavanagh" 
figDir = "../figures/"

source('helpers/psychometricHelpRobust6.R') #load fit,
# colsNotInE1 = setdiff(colnames(dat),colnames(datE1))
# datE1[,colsNotInE1] = -999 #dummy value
# colsNotInThisOne = setdiff(colnames(datE1),colnames(dat))
# dat[,colsNotInThisOne] = -999 #dummy value
# dat = rbind(dat,datE1)
expThis=1
iv="tilt"
lapseMinMax=c(.01,.01)
xLims=c(-1,1)
numPointsPerCurve=150

thisDat <- subset(dat,exp==expThis)
factors=c("subject","startLeft")
thisDat$correct = thisDat$respLeftRight
initialMethod<-"brglm.fit"  
fitParms<-fit(thisDat,iv,factors,lapseMinMax,lapseAffectBothEnds=TRUE,
              initialMethod=initialMethod,verbosity=FALSE) 
#calculate psychometric curves
myPlotCurve <- makeMyPlotCurve4(iv,xLims[1],xLims[2],numxs=numPointsPerCurve,lapseAffectBothEnds=TRUE)
psychometrics<-ddply(fitParms,factors,myPlotCurve)  
psychometrics$correct <- psychometrics$pCorr #some functions expect one, some the other

source('plotIndividDataWithPsychometricCurves.R')
colFactor=factors[1]
rowFactor="."
 figTitle = paste("E",expThis,"_",rowFactor,"_by_",colFactor,sep='')
 if (length(unique(thisDat$subject))==1) #only one subject
   figTitle = paste(figTitle,unique(thisDat$subject)[1],sep='_')

# quartz(figTitle,width=2*length(unique(thisDat$subject)),height=2.5) #,width=10,height=7)  
g<-plotIndividDataAndCurves(thisDat,psychometricCurves=psychometrics,worstCasePsychometricRegion=NULL,
                                     rowFactor=rowFactor,colFactor=colFactor) 
ggsave( paste(figDir,figTitle,'.png',sep='')  )

bootstrapTheFit = TRUE
if (bootstrapTheFit) ########################do bootstrapping of psychometric function###############
{
  getFitParmsForBoot <- makeParamFitForBoot(iv,lapseMinMax,initialMethod,lapseAffectBothEnds=TRUE,verbosity=0)   
  bootForDdply <- makeMyBootForDdply(getFitParmsForBoot,"tilt",lapseMinMax,iteratns=200,
                                     confInterval=.6827)
  #calculate confidence interval for mean parameter and slope parameter
  paramCIs= ddply(thisDat,factors,bootForDdply)
  paramCIs$linkFx <- fitParms[1,"linkFx"] #needed by myPlotCurve. Assume boot is same
  paramCIs$method <- fitParms[1,"method"] #needed by myPlotCurve. Assume boot is same
  paramCIs$chanceRate <- fitParms[1,"chanceRate"] #needed by myPlotCurve. Assume boot is same
  minMaxWorstCaseCurves<- makeMyMinMaxWorstCaseCurves(myPlotCurve,iv)
  worstCasePsychometricRegion= ddply(paramCIs, factors, minMaxWorstCaseCurves)
} #########end bootstrapping######################
else { worstCasePsychometricRegion = NULL }

#plot
colFactor = factors[1]
colorFactor = factors[2]
rowFactor="."
figTitle = paste("E",expThis,"_",rowFactor,"_by_",colFactor,sep='')
if (length(unique(thisDat$subject))==1) #only one subject
  figTitle = paste(figTitle,unique(thisDat$subject)[1],sep='_')
quartz(figTitle,width=2*length(unique(thisDat$subject)),height=2.5) #,width=10,height=7)
g<-plotIndividDataAndCurves(thisDat,psychometrics,
                            worstCasePsychometricRegion,rowFactor="durWithoutProbe",colFactor="subject")
ggsave( paste(figDir,figTitle,'.png',sep='')  )


source("extractThreshesAndPlot.R") #provides threshes, plots

#save threshes to file
varName=paste("threshes_",iv,"_",expName,sep='') #combine threshes
assign(varName,threshes)
save(list=varName,file=paste("../data/",varName,".Rdata",sep='')) 
print( paste("Saved threshes to file", varName, ".Rdata",sep='') )

