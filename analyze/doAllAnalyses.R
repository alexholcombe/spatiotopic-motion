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
I THINK I STARTED CONVERTING THIS BUT THEN PAUSED WHILE FAJOU GOT STUFF WORKING WITH EYETRACKING
source('helpers/psychometricHelpRobust6.R') #load fit,
expThis=1
iv="tilt"
lapseMinMax=c(.01,.01)
xLims=c(-1,1)
numPointsPerCurve=150
thisDat <- subset(dat,exp==expThis)
factors<-c("subject","startLeft","durWithoutProbe")
names(factors) <- c("columns","color","rows")
thisDat$correct = thisDat$respLeftRight
initialMethod<-"brglm.fit"  
fitParms<-fit(thisDat,iv,unname(factors),lapseMinMax,lapseAffectBothEnds=TRUE,
              initialMethod=initialMethod,verbosity=FALSE) 
#calculate psychometric curves
myPlotCurve <- makeMyPlotCurve4(iv,xLims[1],xLims[2],numxs=numPointsPerCurve,lapseAffectBothEnds=TRUE)
psychometrics<-ddply(fitParms,unname(factors),myPlotCurve)  

source('plotIndividDataWithPsychometricCurves.R')
bootstrapTheFit = TRUE
if (bootstrapTheFit) ########################do bootstrapping of psychometric function###############
{
  getFitParmsForBoot <- makeParamFitForBoot(iv,lapseMinMax,initialMethod,lapseAffectBothEnds=TRUE,verbosity=0)   
  bootForDdply <- makeMyBootForDdply(getFitParmsForBoot,"tilt",lapseMinMax,iteratns=200,
                                     confInterval=.6827)
  #calculate confidence interval for mean parameter and slope parameter
  paramCIs= ddply(thisDat,unname(factors),bootForDdply)
  #below command because these fields needed by PlotCurve. Assume boot used same as fitParms
  paramCIs[,c("linkFx","method","chanceRate")]=fitParms[1,c("linkFx","method","chanceRate")]
  calcMinMaxWorstCaseCurves<- makeMyMinMaxWorstCaseCurves(myPlotCurve,iv)
  worstCasePsychometricRegion= ddply(paramCIs, unname(factors), calcMinMaxWorstCaseCurves)
} else  #########end bootstrapping######################
{ worstCasePsychometricRegion = NULL }

#extract threshes 
threshCriterion<-0.5
myThreshGet= makeMyThreshGetNumerically(iv,threshCriterion)
threshesThis = ddply(psychometrics,unname(factors),myThreshGet) 
fitParms<- merge(threshesThis,fitParms)
#plot
figTitle = paste("E",expThis,"_",factors["rows"],"_by_",factors["columns"],sep='')
if (length(unique(thisDat$subject))==1) #only one subject
  figTitle = paste(figTitle,unique(thisDat$subject)[1],sep='_')
#quartz(figTitle,width=2*length(unique(thisDat$subject)),height=2.5) #,width=10,height=7)
g<-plotIndividDataAndCurves(thisDat,iv,factors,psychometrics,worstCasePsychometricRegion,threshesThis)
#PUT AN ERROR BAR ON THE INDIVIDUAL PARTICIPANT'S THRESH?
ggsave( paste(figDir,figTitle,'.png',sep='')  )
#################################################################################################
#ALSO LOOK AT JITTER AND UP/DOWN
#LOOK AT UP/DOWN
factors=c("subject","startLeft","upDown")
names(factors) <- c("columns","color","rows")
fitParms<-fit(thisDat,iv,factors,lapseMinMax,lapseAffectBothEnds=TRUE,
              initialMethod=initialMethod,verbosity=FALSE) 
psychometrics<-ddply(fitParms,factors,myPlotCurve)  
if (length(unique(thisDat$subject))==1) #only one subject
  figTitle = paste(figTitle,unique(thisDat$subject)[1],sep='_')
# quartz(figTitle,width=2*length(unique(thisDat$subject)),height=2.5) #,width=10,height=7)  
bootstrapTheFit = TRUE
if (bootstrapTheFit) ########################do bootstrapping of psychometric function###############
{
  getFitParmsForBoot <- makeParamFitForBoot(iv,lapseMinMax,initialMethod,lapseAffectBothEnds=TRUE,verbosity=0)   
  bootForDdply <- makeMyBootForDdply(getFitParmsForBoot,"tilt",lapseMinMax,iteratns=200,
                                     confInterval=.6827)
  #calculate confidence interval for mean parameter and slope parameter
  paramCIs= ddply(thisDat,unname(factors),bootForDdply)
  #below command because these fields needed by PlotCurve. Assume boot used same as fitParms
  paramCIs[,c("linkFx","method","chanceRate")]=fitParms[1,c("linkFx","method","chanceRate")]
  calcMinMaxWorstCaseCurves<- makeMyMinMaxWorstCaseCurves(myPlotCurve,iv)
  worstCasePsychometricRegion= ddply(paramCIs, unname(factors), calcMinMaxWorstCaseCurves)
} else  #########end bootstrapping######################
{ worstCasePsychometricRegion = NULL }
#extract threshes 
myThreshGet= makeMyThreshGetNumerically(iv,threshCriterion)
threshesThis = ddply(psychometrics,unname(factors),myThreshGet) 
fitParms<- merge(threshesThis,fitParms)
#plot
figTitle = paste("E",expThis,"_",factors["rows"],"_by_",factors["columns"],sep='')
if (length(unique(thisDat$subject))==1) #only one subject
  figTitle = paste(figTitle,unique(thisDat$subject)[1],sep='_')
quartz(figTitle,width=2*length(unique(thisDat$subject)),height=2.5) #,width=10,height=7)
g<-plotIndividDataAndCurves(thisDat,iv,factors,psychometrics,worstCasePsychometricRegion,threshesThis)
ggsave( paste(figDir,figTitle,'.png',sep='')  )
#IM GOING TO NEED AN ERROR BAR FOR EACH SUBJECT ON A THRESH PLOT

#save threshes to file
varName=paste("threshes_",iv,"_",expName,sep='') #combine threshes
assign(varName,threshes)
save(list=varName,file=paste("../data/",varName,".Rdata",sep='')) 
print( paste("Saved threshes to file", varName, ".Rdata",sep='') )

