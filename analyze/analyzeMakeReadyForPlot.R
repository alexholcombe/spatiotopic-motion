setwd("/Users/alexh/Documents/vision/neuropsych_palinopsia_Michael_Beckett/Szinte_Cavanagh_Spatiotopic/psychopy_SzinteCavanagh/analyze/")
iv='tilt'
source('helpers/psychometricHelpRobust6.R') #load my custom version of binomfit_lims

varyLapseRate = FALSE
#global variables needed by psychometricGgplotHelpRobust.R
if (varyLapseRate) { lapseMinMax= c(0,0.05) }  else  #range of lapseRates to try for best fit
	{ lapseMinMax = c(0.01,0.01) }
#factorsForBreakdown = c('exp','startLeft')
factorsForBreakdown = c('exp','startLeft','durWithoutProbe')

xLims=c(-1,1)
yLims=c(-.05,1.05)
numPointsForPsychometricCurve=150 #250
#end global variables expected
verbosity=0 #0-don't print much debugging stuff, 1 prints more, and 2 even more

colrFactr = paste('factor(',factorsForBreakdown[1],')',sep='')
if ( length(factorsForBreakdown)>1 ) 
  shapeFactr = paste('factor(',factorsForBreakdown[2],')',sep='') else #can't break line before else
  { shapeFactr = colrFactr }
facetCols='subject' #'.'
facetRows='.'
if (length(factorsForBreakdown)>1)
  facetRows = factorsForBreakdown[2]
faceting=paste('~',facetCols,sep='')
factorsPlusSubject<-factorsForBreakdown
factorsPlusSubject[ length(factorsForBreakdown)+1 ]<- "subject"

dat$correct <- dat$respLeftRight #temporary bc fitting requires this to be dv

##OLD BELOW###
initialMethod<-"brglm.fit"  # "glmCustomlink" #  
getFitParms <- makeParamFit(iv,lapseMinMax,initialMethod,lapseAffectBothEnds=TRUE,verbosity) #use resulting function for one-shot curvefitting
getFitParmsPrintProgress <- function(df) {  #So I can see which fits yielded a warning, print out what was fitting first.
  cat("Finding best fit (calling fitParms) for ")
  for (i in 1:length(factorsPlusSubject) ) #Using a loop print them all on one line
    cat( paste( factorsPlusSubject[i],"=",df[1,factorsPlusSubject[i]])," " )
  cat("\n")
  if (length(unique(df$tilt))==1) {
    cat("Only one tilt value, so not fitting psychometric function.")
    return (data.frame())
  }
  print( table(df$tilt) ) #debugON
  return( getFitParms(df) )
}
dat$subject <- factor(dat$subject)
dat$correct <- dat$respLeftRight #temporary bc fitting requires this to be dv
#tempDat<- subset(dat,numObjects==2 & numTargets==1 & subject=="AH" ) #Does this well now, using penalized.deviance to compare across lapse rates
fitParms <- ddply(dat, factorsPlusSubject, getFitParmsPrintProgress)
#To-do. Change psychometrics myCurve to accommodate rescaling based on method
#       Stop setting global variables
#     Figure out way to pass method thgough to binomfit_limsAlex

#prediction tracking two if only can track one. myPlotCurve then calculates it.
#use the fitted parameters to get the actual curves
myPlotCurve <- makeMyPlotCurve4(iv,xLims[1],xLims[2],numPointsForPsychometricCurve,lapseAffectBothEnds=TRUE)
#ddply(fitParms,factorsPlusSubject,function(df) { if (nrow(df)>1) {print(df); STOP} })  #debugOFF
psychometrics<-ddply(fitParms,factorsPlusSubject,myPlotCurve)  
psychometrics$correct <- psychometrics$pCorr #some functions expect one, some the other

#Below are just helper functions. Consider migration into a helper function file
#Usually ggplot with stat_summary will collapse the data into means, but for some plots and analyses can't do it that way.
#Therefore calculate the means
calcMeans<-function(df) {
  if ( !("correct" %in% names(df)) )
    warning("your dataframe must have a column named 'correct'",immediate.=TRUE)
  numCorrect<-sum(df$correct==1)
  numTrials= sum(complete.cases(df$correct))
  pCorr <- numCorrect/numTrials
  df= data.frame(pCorr)
  return(df)
}  
factorsPlusSubjectAndIv <- factorsPlusSubject
factorsPlusSubjectAndIv[ length(factorsPlusSubjectAndIv)+1 ] <- iv
datMeans<- ddply(dat,factorsPlusSubjectAndIv,calcMeans)

calcPctCorrThisIvVal <- function(df,iv,val) {
  #Take dataframe with fitted psychometric function, 
  #where only one row tests this iv val, or none and must interpolate
  thisValIdx<- which(df[,iv]==val)
  if (length(thisValIdx) > 1) {
    stop('calcPctCorrThisSpeed passed a dataframe with more than one instance of speed s')
  }
  if (length(thisValIdx) ==1) {
    answer<- df$pCorr[thisValIdx] #equivalent to df[thisSpeedIdx,'pCorr']
  } else {  #This speed wasn't tested, so have to interpolate to estimate pCorr
    smallers <- which(df[,iv]<val)
    if (length(smallers)==0)
      stop(paste('IV val queried,',val,' is smaller than smallest val tested,',min(df[,iv])))
    closestSmaller<- max( df[smallers,iv] )
    largers <- which(df[,iv]>val)
    if (length(largers)==0)
      stop(paste('IV val queried,',val,' is larger than largest val tested,',max(df[,iv])))
    closestLarger<- min( df[largers,iv] )
    #calculate what fraction of the way s is to the larger
    fractionWayToLarger<- (val-closestSmaller)/(closestLarger-closestSmaller)
    largerPctCorr<- df$pCorr[ which(df[,iv]==closestLarger) ]
    smallerPctCorr<- df$pCorr[ which(df[,iv]==closestSmaller) ]
    answer<- smallerPctCorr + fractionWayToLarger*(largerPctCorr-smallerPctCorr)
    #print(paste('closestSmalledfr=',closestSmaller,'closestLarger=',closestLarger))
    #print(paste('fractionWayToLarger=',fractionWayToLarger,'largerPctCorr=',largerPctCorr,'smallerPctCorr=',smallerPctCorr,'answer=',answer))
  }
  return (answer)
}

cat(paste('I give you fitParms, psychometrics, datMeans, and function calcPctCorrThisIvVal.'))
if (bootstrapTheFit) {
  cat(paste('I also give you bootstrapped worstCasePsychometricRegion '))
  stopifnot(exists("worstCasePsychometricRegion"))
}
stopifnot(exists("fitParms"))
stopifnot(exists("psychometrics"))
stopifnot(exists("datMeans"))
stopifnot(exists("calcPctCorrThisIvVal"))
