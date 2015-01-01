#This file analyses anonymized data provided by "loadAnonymiseSaveData.R" in exp-specific directory
#Working directory is set hopefully by Rproj file to directory that it's in.
setwd("/Users/alexh/Documents/vision/neuropsych_palinopsia_Michael_Beckett/Szinte_Cavanagh_Spatiotopic/psychopy_SzinteCavanagh/analyze/")
expName="123targets269objects" 
load("../data/MB.RData",verbose=TRUE) #E1 #returns dat
datMB <- dat; datMB$tilt <- datMB$Tilt
load("../data/E1.RData",verbose=TRUE) #E1 #returns dat

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
source("extractThreshesAndPlot.R") #provides threshes, plots

#save threshes to file
varName=paste("threshes_",iv,"_",expName,sep='') #combine threshes
assign(varName,threshes)
save(list=varName,file=paste("../data/",varName,".Rdata",sep='')) 
print( paste("Saved threshes to file", varName, ".Rdata",sep='') )

