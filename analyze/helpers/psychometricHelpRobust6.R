library(splines)
library(ggplot2) 
library(boot) 
library(modelfree)
library(brglm)
library(plyr)
#library(Cairo) #for windows
#Alex Holcombe, started November 2010
#previous versions of this file were called things like lapseRateSearchDataSeparate
source('helpers/psychometricRobustify4.R') #load my custom version of binomfit_lims

#global variables this code expects:  
#threshCriterion, 
#linkf
###end global variables

calcGlmCustomLinkDeviance<- function(fitModel,numCorrect,numTrials,xs,
  				                  	 guessing=guessing,lapsing=l, lapseAffectBothEnds=FALSE) {
	#Note that this means you'll be using penalized deviance within a lapse rate but comparing standard deviance across lapse rates
	#dataFit <- model.frame(fitModel) #Don't use this because it is scaled.
	bottom = guessing
  if (lapseAffectBothEnds) {
    bottom = guessing + lapsing/2
  }
	#numCorrect<<-numCorrect; numTrials<<-numTrials; xs<<-xs; guessing<<-guessing; lapsing<<-lapsing
	modelToCalcDeviance<- suppressWarnings( 
    		binomfit_limsAlex(numCorrect, numTrials, xs, guessing=bottom, lapsing=lapsing, 
    						  initial="glmCustomlink", tryOthers=FALSE)   )

	modelToCalcDeviance$coefficients[1] <- fitModel$fit$coefficients[1]
	modelToCalcDeviance$coefficients[2] <- fitModel$fit$coefficients[2]
	modelCheck <- modelToCalcDeviance
	mu<- suppressWarnings( predict(modelToCalcDeviance$fit,data.frame(x=xs),type="response") )
	#If you call the above without suppressWarnings, then it returns a "prediction from a rank-deficient fit may be misleading" error. After some investigation, I find nothing wrong with the design matrix. So I think it has something unimportant to do with the xs I'm calling it with for the prediction
	
	#Calc raw deviance - null model deviance for each point
	deviances<- binomial()$dev.resids(numCorrect/numTrials,mu,numTrials) 
	deviance<- sum(deviances)
	return(deviance)
}

fitBrglmKludge<- function( df, lapseMinMax, returnAsDataframe, initialMethod, lapseAffectBothEnds=FALSE, verbosity=0 ) {
#for each possible lapse rate, from lapseMinMax[1] to lapseMinMax[2] in steps of .01
#do probit regression. Return estimate of lapseRate and mean and stdev of underlying Gaussian
#requires countWarnings() function that I wrote and put in psychometricHelpersAlex.R
#If returnAsDataframe, that means return the fit params as data frame. This allows returning the text of the warning.
#Boot can't deal with a dataframe or list, so boot-related functions will call with returnAsDataframe=FALSE.
  if (!is.null(df$chanceRate))
  	chanceRate<- df$chanceRate[1] #assume it's same for all these trials
  else stop("df dataframe passed in must have chanceRate")
  if (verbosity) { cat("fitBrglmKludge trying to fit\n"); print(df) }
  #round min up to the nearest .01
  min01 = ceiling(lapseMinMax[1]*100) /100
  #round max down to the nearest .01
  max01 = floor(lapseMinMax[2]*100) /100
  lapseRates= seq(min01,max01,.01)
  if (min01 != lapseMinMax[1])
    lapseRates= c(lapseMinMax[1],lapseRates) #tack on the minimum 
  if (max01 != lapseMinMax[2])
    lapseRates= c(lapseRates,lapseMinMax[2]) #tack on the minimum 
  deviances = c(); predictors=c()
  parms=c()
  warned=c(); errored=c(); warnMsgs=c(); linkFxs=c(); methods=c()
  for (l in lapseRates)	{
  	#print(paste('trying lapseRate=',l)) #debugOFF
    bottom = chanceRate
    if (lapseAffectBothEnds) {
      bottom = chanceRate + l/2 #when lapse, half the time give that end's response, half time the other
    }
	  cntrl = list(epsilon=1e-6,maxit=10000) 
    iv <- df[,1] #assume first column is independent variable, be it speed or be it tf
	  #problem below is that if warning occurs, we don't get the value returned because of error-catching stupidity
  	fitModel<-countWarnings( 
  				binomfit_limsAlex(df$numCorrect,df$numTrials,iv,link="logit",
  				                  guessing=bottom,lapsing=l,control=cntrl,initial=initialMethod)
  			  ) 
	  importantWarns <- attributes(fitModel)$warningMsgs
	  importantWarns<- importantWarns[ which(attributes(fitModel)$warningMsgs!="non-integer #successes in a binomial glm!") ]
  	if (length(importantWarns) >0) {
  		if (verbosity>0) {
	  		cat("fitModel WARNED with: "); cat(  paste(importantWarns, " ") ); 
  		}
  		#"glm.fit: fitted probabilities numerically 0 or 1 occurred" suggests separation or quasi-separation
  		# Was ubiquitous with standard logistic regression, so stopped counting it I think
  		#if (attributes(fitModel)$warningMsgs[[1]] != "glm.fit: fitted probabilities numerically 0 or 1 occurred") {
	  	#	warned<-c(warned,TRUE);   
	  	#	firstWarnMsg<- attributes(fitModel)$warningMsgs[1]
	  	#	warnMsgs<-c(warnMsgs,firstWarnMsg)
	  	#} else warned<-c(warned,FALSE)
	  	warned<-c(warned,TRUE)   
	  	firstWarnMsg<- importantWarns[1]
	  	warnMsgs<-c(warnMsgs,firstWarnMsg)	  	
  	} else warned<-c(warned,FALSE)
  	
  	if(is(fitModel,"error")) { 
  		errored=c(errored,TRUE); print(fitModel)   		
  	}  else errored=c(errored,FALSE)

  	#To compare models with different lapse rates, use deviance which is "up to a constant, minus twice the maximized log-likelihood"
  	#Save all this stuff so know details of winning model at end.
  	method<- fitModel$fit$method
  	if (method=="brglm.fit") {
  		#deviances=c(deviances,fitModel$fit$penalized.deviance)  #use penalized deviance
  		#Deviance, penalized deviance calculated by brglm is wrong because is after data has been rescaled and truncated (chance to 1-lapseRate) 
  		#It's ok for arriving at the best model for a particular lapse rate, but no good for comparing models across lapse rates.
  		#cat('about to calcGlmCustomLinkDeviance')
  		deviance<- calcGlmCustomLinkDeviance(fitModel,df$numCorrect,df$numTrials,iv,guessing=bottom,lapsing=l)
  		#cat('leaving calcGlmCustomLinkDeviance with deviance=',deviance)
  		deviances<-c(deviances,deviance)
  	}
  	else
  		deviances<-c(deviances,fitModel$fit$deviance)
  	addsigma=c(fitModel$b,fitModel$sigma)
  	#parms= rbind(parms,fitModel$b)
  	parms= rbind(parms,addsigma)
  	predictors=c(predictors,fitModel$fit)
  	# if (!exists(fitModel$fit$method)) #because glmrob doesn't have that field
  	  # method<- fitModel$method #glmrob puts it here
  	methods<- c(methods,method)

  	linkFxs<- c(linkFxs,fitModel$fit$family$link)
  	if (verbosity>1)
  		cat(paste("With lapseRate=",l,", fitModel$fit$deviance=", fitModel$fit$deviance, "\n"))
  } #END lapseRates loop
  if (length(which(warned)) >0)
  	cat( 'WARNED on lapseRates (',lapseRates[which(warned)], ') '  )
  if (length(which(warned))==length(lapseRates))
  	cat("Got WARNING (possibly nonconvergence) for every lapse rate, but assuming nonconvergence is OK ")
  if (length(which(errored)) >0)
  	cat( 'ERRORed on lapseRates (',lapseRates[which(errored)], ') '  )
  if (length(which(errored))==length(lapseRates))
  	warning("Got ERROR for every lapse rate, so we will CRASH SOON ")
  
  notErrored= which(!errored) #list of indexes of lapse rates for which no error
  #of those where did not error, determine which had best fit
  #unfortunately glmrob doesn't provide any deviance measure, so I would have to calculate it myself
  bestIofNotErrored = which.min( deviances[notErrored] )  #index of lowest deviance, among those which converged
  #cat('bestIofNotErrored=', bestIofNotErrored)
  bestI= notErrored[bestIofNotErrored]
  lapseRate = lapseRates[bestI]
  bestParms = parms[bestI,]
  bestPredictor = predictors[bestI]
  #cat('all parms for this run of lapseRates=',parms)
  mean=bestParms[1]; slope=bestParms[2]; 
  sigma=bestParms[3]
  nWarns<- length(which(warned));  nErrs<- length(which(errored))
  if (is.null(warnMsgs))
  	firstWarn<- "NA"
  else firstWarn<- warnMsgs[[1]]
  #cat('method[bestI]=',methods[bestI]," ") #debugOFF
  #cat('linkFxs[bestI]=',linkFxs[bestI]," ") #debugOFF
  if (returnAsDataframe)
  	dg<- data.frame(mean,slope,chanceRate,lapseRate,sigma,method=methods[bestI],linkFx=linkFxs[bestI],nWarns,nErrs,firstWarn)
  else  #boot wants only a vector back. Can't handle a dataframe. So, cant pass text warning message back because all vec vals
  	dg<- cbind(mean,slope,chanceRate,lapseRate,sigma,nWarns,nErrs) #have to be same type
  
  if (verbosity>1)
  	cat('exiting fitBrglmKludge with:\n'); print(dg)
  return( dg )  	#before I had the following which eventually crapped out inside boot return( list(dg,bestPredictor) )  
}

summarizNumTrials<-function(df) {
  if ( !("correct" %in% names(df)) )
   warning("your dataframe must have a column named 'correct'",immediate.=TRUE)
  #cat('Passed to summarizNumTrials=\n'); print(df) #debugOFF
  numCorrect<-sum(df$correct==1)
  numTrials<- sum(complete.cases(df$correct))
  chanceRate<- sum(df$chanceRate)/numTrials
  
  df= data.frame(numCorrect,numTrials,chanceRate) #,correctY,correctN)
  return(df)
}  

#construct a function to use for one-shot (non-bootstrapping) fit
makeParamFit <- function(iv, lapseMinMax, initialMethod, lapseAffectBothEnds=FALSE, verbosity=0) {
  #iv is independent variable
  fn2 <- function(df) {
    #data comes in one row per trial, but binomFit wants total correct, numTrials
    #so now I have to count number of correct, incorrect trials for each speed
    #assuming there's no other factors to worry about
    if ( !(iv %in% names(df)) )
      warning("your dataframe must contain iv as an independent variable",immediate.=TRUE)
    sumry = ddply(df,iv,summarizNumTrials) #also calculates chanceRate
    #print( paste("ddply df with factor ",iv, " summariz, yielding ")) #debugOFF
    #print(sumry) #debugOFF
    #curveFit(sumry$speed,sumry$correct,sumry$numTrials,subjectname,lapsePriors,meanPriors,widthPriors,'MAPEstimation')  
    returnAsDataframe=TRUE #this allows keeping the text of the warning messages. (Boot can't do this)
    fitParms = fitBrglmKludge(sumry,lapseMinMax, returnAsDataframe,initialMethod,verbosity)
    #print( paste('fitParms=',fitParms) )
    return( fitParms )
  }
  return (fn2)
}

#construct a function to use for function fitting and bootstrapping. Will be sent one row per trial
makeParamFitForBoot <- function(iv,lapseMinMax,initialMethod,lapseAffectBothEnds=FALSE,verbosity=0) { #default chancePerformanceRate=.5
  #so boot function will provide a random list of idxs. The problem is partialling these out among speeds. Old way of doing it is putting the whole experiment in a single hat, so you can end up with
  #fake datasets that don't even test at certain speeds
  fn2 <- function(df,idxs) {
    #data comes in one row per trial, but binomFit wants total correct, numTrials
    #so now I have to count number of correct, incorrect trials for each speed
    #assuming there's no other factors to worry about
    if ( !(iv %in% names(df)) )
      warning("your dataframe must contain iv as an independent variable",immediate.=TRUE)
    if (length(unique(df[,iv]))==1) {
      cat("Only one iv level, so not fitting psychometric function.")
      return (data.frame())
    }
    thisData <- df[idxs,]  
    sumry = ddply(thisData,iv,summarizNumTrials)
    if (verbosity>1) {
      print('sumry='); print(sumry)
    }	
    if ( nrow(sumry[iv])==1 )
      print('boot has unluckily drawn a bootstrapped experiment with only one iv value. Perhaps stratify by iv') #actually, bootstrapping should have separate hats for each speed. this is called stratified bstrapping in R terms
    returnAsDataframe=FALSE #Boot can't handle dataframes. Would allow keeping the text of the warning messages.
    #sumry should have chanceRate as a field but I dont know if it does
    fitParms<- fitBrglmKludge(sumry,lapseMinMax, returnAsDataframe, initialMethod, verbosity)
    if (verbosity>0) 
      print( paste('fitParms=',fitParms) )
    return( fitParms )
    #return( c(fitParms$mean,fitParms$slope,fitParms$lapseRate) )
  }
  return( fn2 )
}
makeParamFitPrintProgress<-function(iv,factors,lapseMinMax,
                                    lapseAffectBothEnds,initialMethod,verbosity=0) { #use resulting function for one-shot curvefitting
  fn3<- function(df) {
    cat("Finding best fit (calling fitParms) for ")
    for (i in 1:length(factors) ) #Using a loop print them all on one line
      cat( paste( factors[i],"=",df[1,factors[i]])," " )
    cat("\n")
    if (length(unique(df[,iv]))==1) {
      cat("Only one iv level, so not fitting psychometric function.")
      return (data.frame())
    }
    #print( table(df[,iv]) ) #debugON    
    getFitParms <- makeParamFit(iv,lapseMinMax,initialMethod,lapseAffectBothEnds,verbosity) #use resulting function for one-shot curvefitting
    parms<- getFitParms(df)
    return (parms)
  }
}

#fit psychometric functions to data ########################################
fit <- function(dat,iv,factors,lapseMinMax,lapseAffectBothEnds,
                initialMethod="brglm.fit",verbosity=FALSE) 
{  
  fitAndPrintProgress<- makeParamFitPrintProgress(iv,factors,lapseMinMax,
                           lapseAffectBothEnds,initialMethod,verbosity) #use resulting function for one-shot curvefitting
  print(fitAndPrintProgress)
  #fitAndPrintProgress(dat) #debugOFF
  fitParms <- ddply(dat, factors, fitAndPrintProgress)
  return (fitParms)
}


makeMyPsychoCorr2<- function(iv, lapseAffectBothEnds=FALSE) { #Very similar to makeMyPlotCurve below, only for just one x
  fnToReturn<-function(df) {
    #expecting to be passed df with fields:
    # mean, slope, lapseRate, chanceRate, method, linkFx
    df = data.frame(df) #in case it wasn't a dataframe yet
    #set up example model with fake data
    #I don't know why the below didn't work with example01 but it doesn't work
    dh=data.frame(speed=c(.7,1.0,1.4,1.7,2.2),tf=c(3.0,4.0,5.0,6.0,7.0),
                  numCorrect=c(46,45,35,26,32),numTrials=c(48,48,48,48,49))
    dh$lapseRate=df$lapseRate
    bottom = df$chanceRate
    if (lapseAffectBothEnds) {
      bottom= df$chanceRate + df$lapseRate/2
    }
    if(iv=="speed") {
      exampleModel<-suppressWarnings( 
        binomfit_limsAlex(dh$numCorrect, dh$numTrials, dh$speed, link=as.character(df$linkFx), 
                          guessing=bottom, lapsing=df$lapseRate, initial=as.character(df$method))  #, tryAlts=FALSE  ) 
      ) } else if (iv=="tf") {
        exampleModel<-suppressWarnings( 
          binomfit_limsAlex(dh$numCorrect, dh$numTrials, dh$tf, link=as.character(df$linkFx), 
                            guessing=bottom, lapsing=df$lapseRate, initial=as.character(df$method))  #, tryAlts=FALSE  ) 
        ) } else {
          print(paste("iv must be either speed or tf, but what was passed was",tf))
        }    
    exampleModel=exampleModel$fit
    #modify example fit, use its predictor only plus parameters I've found by fitting
    exampleModel[1]$coefficients[1] = df$mean
    exampleModel[1]$coefficients[2] = df$slope

    if (iv=="speed") {
      pfit= suppressWarnings( predict( exampleModel, data.frame(x=df$speed), type = "response" ) ) #because of bad previous fit, generates warnings
    } else if (iv=="tf")
      pfit= suppressWarnings( predict( exampleModel, data.frame(x=df$tf), type = "response" ) ) #because of bad previous fit, generates warnings
    
    if (df$method=="brglm.fit" | df$method=="glm.fit") {#Doesn't support custom link function, so had to scale from guessing->1-lapsing manually
      pfit<-unscale0to1(pfit,bottom,df$lapseRate)
    }
    #only one should exist
    stopifnot( !all(c("targets","numTargets") %in% colnames(psychometricsSpeed)) ) 
    numTargets = ifelse("targets" %in% colnames(psychometricsSpeed),df$targets,df$numTargets)
    if(numTargets=="2P"){ #Parameters were duplicate of numTargets==1, and p's are corresponding prediction averaged with chance
      pfit<-0.5*(df$chanceRate+pfit)
    }  
    return (pfit)
  }
  return (fnToReturn)
}
  
makeMyPlotCurve4<- function(iv,xmin,xmax,numxs,lapseAffectBothEnds=FALSE) {#create psychometric curve plotting function over specified domain
  fnToReturn<-function(df) {
  	#expecting to be passed df with fields:
  	# mean, slope, lapseRate, chanceRate,
  	# method, linkFx
    df = data.frame(df) #in case it wasn't a dataframe yet
    #set up example model with fake data
    #I don't know why the below didn't work with example01 but it doesn't work
    dh=data.frame(speed=c(.7,1.0,1.4,1.7,2.2),tf=c(3.0,4.0,5.0,6.0,7.0),
                  numCorrect=c(46,45,35,26,32),numTrials=c(48,48,48,48,49))
    dh[,iv] = c(.7,1.0,1.4,1.7,2.2) 
    dh$lapseRate=df$lapseRate
    print(head(df)) #debugON
    bottom = df$chanceRate
    if (lapseAffectBothEnds) {
      bottom = df$chanceRate + df$lapseRate/2 #when lapse, half the time give that end's response, half time the other
    }
    exampleModel<-suppressWarnings(    
        binomfit_limsAlex(dh$numCorrect, dh$numTrials, dh[,iv], link=as.character(df$linkFx), 
                          guessing=bottom, lapsing=df$lapseRate, initial=as.character(df$method))  #, tryAlts=FALSE  ) 
        )    
    exampleModel=exampleModel$fit
    
    #modify example fit, use its predictor only plus parameters I've found by fitting
    exampleModel[1]$coefficients[1] = df$mean
    exampleModel[1]$coefficients[2] = df$slope
  
    xs = (xmax-xmin) * (0:numxs)/numxs + xmin
    pfit<- suppressWarnings( predict( exampleModel, data.frame(x=xs), type = "response" ) ) #because of bad previous fit, generates warnings
    if (df$method=="brglm.fit" | df$method=="glm.fit") {#Doesn't support custom link function, so had to scale from guessing->1-lapsing manually
		  pfit<-unscale0to1(pfit,bottom,df$lapseRate)
	  }
    if ('numTargets' %in% colnames(df))
      if(df$numTargets=="2P"){ #Parameters were duplicate of numTargets==1, and p's are corresponding prediction averaged with chance
        pfit<-0.5*(bottom+pfit)
      }	
    #returning the dependent variable with two names because some functions expect one
    #Reason is that want to be able to plot it with same ggplot stat_summary as use for raw
    #data that expects "correct"
    df = data.frame(xs,pfit,pfit)
    
    colnames(df) <- c(iv,"pCorr","pfit")
    df$correct <- df$pCorr #some subsequent function needs it to be called correct
    #print("returning curve with head()"); print(head(df)) #debugOFF
    return(df)
  }
  return (fnToReturn)
}

makeMyThreshGetNumerically<- function(iv,threshCriterion) {#create function that can use with ddply once have psychometric curves for each condition
  fnToReturn<-function(df) { #after function has been fit, determine x-value needed for criterion performance
    #So if there's an error, return info about what it errored on. And also indicate there was an error
    #in the dataframe.
    if ( !("correct" %in% names(df)) )
      warning("your dataframe must have a column named 'correct'",immediate.=TRUE)
    ans<- tryCatch( {
      threshSlop<- threshold_slope(df$correct,df[,iv],criterion= threshCriterion)
      return( data.frame(threshThisCrit=threshSlop$x_th, slopeThisCrit=threshSlop$slope, 
                         criterion=threshCriterion, error=FALSE) )
    }, 
                    error = function(e) {
                      cat("\nERROR occurred with")  
                      if ("separatnDeg" %in% names(df))
                        cat(paste(' separatnDeg=',df$separatnDeg[1]),' ') #debugON
                      if ("exp" %in% names(df))
                        cat(paste('exp=',df$exp[1]),' ') #debugON
                      if ("subject" %in% names(df))
                        cat(paste('subject=',df$subject[1]),' ') #debugON
                      if ("numObjects" %in% names(df))
                        cat(paste('numObjects=',df$numObjects[1]),' ') #debugON
                      if ("numTargets" %in% names(df))
                        cat(paste('numTargets=',df$numTargets[1])) #debugON
                      print(e)
                      return( data.frame(threshThisCrit=NA, slopeThisCrit=NA, 
                                         criterion=threshCriterion,error=TRUE) )
                    }#,
                    #       finally = function(e) { #just return the normal answer
                    #         return( data.frame(thresh=threshSlop$x_th, error=FALSE) )
                    #       }
    )
    
    print(ans)
    return (ans)
  }
}

makeMyThreshGetAnalytically<- function(threshCriterion,linkingFunctionType) { #create function that can use with 
#ddply once have function fits for each condition
#based on knowledge of function fit,
#calculate x-value corresponding to threshCriterion (threshold)
  fnToReturn<-function(df) {
  	 dg= calcThresh(df, linkingFunctionType, chanceRate, threshCriterion) #should be in psychometricHelpersAlex file
  	 dg
  }
}

makeMyThreshLine<- function(iv,threshColumnName,criterion,xMin,yMin) {
  fnToReturn <- function(df) {   #should be sent a one-row piece of data frame with thresh
    threshes = df[,threshColumnName]
    ivs=c(xMin,threshes[1],threshes[1])
    corrects=c(criterion,criterion,yMin) #draw down to horizontal axis. The -.2 makes sure it extends into margin
    pointsForLines<-data.frame(ivs,corrects)
    names(pointsForLines) <- c(iv,"correct")
    #print('grid='); print (grid)
    return (pointsForLines) 
  }  
}
options(warn=0) #needs to be 0, otherwise no way to catch warnings while also letting function to continue 
#options(warn=1)#instead of default zero which waits until top-level function returns, this will print warnings as we go
#ALERT THIS OPTIONS STUFF SHOULD BE INSIDE A FUNCTION, IF IT'S NEEDED AT ALL

########################do bootstrapping####################
#get confidence interval on parameters, so can draw confidence region
#bootstrap for each subset of experiment sent by ddply
makeMyBootForDdply<- function(getFitParmsForBoot,iv,lapseMinMax,iteratns,confInterval,verbosity=0) {  #create a psychometric curve plotting function over specified domain
	#assumes getFitParmsForBoot has already been constructed
  #For the parametric bootstrap it is necessary for the user to specify how the resampling is to be #conducted. The best way of accomplishing this is to specify the function ran.gen which will return a #simulated data set from the observed data set and a set of parameter estimates specified in mle	
	fnToReturn<-function(df) {
	  #send to boot the dataframe piece with one row per trial
	  if (verbosity) { print('boostrapping with'); print(df[1,]) }
	  #lastDfForBoot <<-df
    #do all the actual bootstrapping. After this, everything is about getting the answer out
    print( table(df[iv]) ) #debugON
	  if (length(unique(df[,iv]))==1) {
	    cat("Only one iv level, so not passing to boot.")
      return (data.frame()) #this should prevent any entries for this condition in final dataframe
	  }
	  b<-boot(df,getFitParmsForBoot,R=iteratns,
            strata=df[,iv]) #strata has to be vector, not dataframe so have to include comma to get iv out
	  #print('finished boot call, and boot returned:'); print(b)
	  
	  ciMethod= 'perc'  #'bca' don't use until investigate why sometimes get error. #with 'bca' boot method using Christina's data, get this error: Error in bca.ci(boot.out, conf, index[1L], L = L, t = t.o, t0 = t0.o,  :   estimated adjustment 'a' is NA
	                          #index=1 meaning bootstrap only the mean?
    ciMeanWithWarnings<- countWarnings(   boot.ci(b,conf=confInterval,index=1,type=ciMethod)    ) 
	  
	  if (length(attributes(ciMeanWithWarnings)$warningMsgs) >0) {
	    print("ciMean boot.ci warned with:"); print(attributes(ciMeanWithWarnings)$warningMsgs); 
	    if (verbosity>0) {
	      cat("but gave value of:"); print(ciMeanWithWarnings);
	    }
	  }
	  ciMean <- ciMeanWithWarnings
	  if (is.null(ciMeanWithWarnings)) #calculating statistic on resamplings always yielded the same value
	    ciMean= data.frame(percent=c(-1,-1,-1,b$t[1,1],b$t[2,1]), bca=c(-1,-1,-1,b$t[1,1],b$t[2,1])) 
	  #set both ends of CI to that value. Should take notice of warning
	                                                   #index=2 meaning bootstrap only the slope?
	  ciSlopeWithWarnings<- countWarnings(   boot.ci(b,conf=confInterval,index=2,type=ciMethod)    ) 
	  if (length(attributes(ciSlopeWithWarnings)$warningMsgs) >0) {
	    print("ciSlope boot.ci warned with:"); print(attributes(ciSlopeWithWarnings)$warningMsgs); 
	    if (verbosity>0) {
	      cat("but gave value of:"); print(ciSlopeWithWarnings);
	    }
	  }
	  
	  ciSlope <- ciSlopeWithWarnings
	  if (is.null(ciSlopeWithWarnings)) #calculating statistic on resamplings always yielded the same value
	    #slope not successfully bootstrapped, so set up dummy bootstrap value return
	    ciSlope= data.frame(percent=c(-1,-1,-1,b$t[1,2],b$t[2,2]), bca=c(-1,-1,-1,b$t[1,2],b$t[2,2])) 
	  
		slopesEachResampling=b$t[,2]
  	failures = which( is.na(slopesEachResampling) )
		numFailures = length( failures )
		#how many times was NA returned. CI calculation will gag if any
		if (numFailures>0) {
		  print(paste('There were',numFailures,' cases where fitting function returned NaN for the slope'))
		  #b$t[failures,2]=-1
		}
		if (lapseMinMax[1] != lapseMinMax[2]) {
                                                                   #4th parameter- lapseRate
  			ciLapseRateWithWarnings<- countWarnings( boot.ci(b,conf=confInterval,index=4,type= ciMethod) ) 
  			print('ciLapseRateWithWarnings='); print(ciLapseRateWithWarnings)
        if (length(attributes(ciLapseRateWithWarnings)$warningMsgs) >0) {
  				print("ciSlope boot.ci warned with:"); print(attributes(ciLapseRateWithWarnings)$warningMsgs); 
  				if (verbosity>0) {
  					cat("but gave value of:"); print(ciLapseRateWithWarnings);
  				}
  	    }
  			ciLapseRate <- ciLapseRateWithWarnings
  	    if (is.null(ciLapseRateWithWarnings)) #calculating statistic on resamplings always yielded the same value
  				#lapseRates not successfully bootstrapped, so set up dummy bootstrap value return
  				ciLapseRate = data.frame(percent=c(-1,-1,-1,b$t[1,4],b$t[2,4]), bca=c(-1,-1,-1,b$t[1,4],b$t[2,4])) 
  			
  	} else { 
  			#lapseRates not bootstrapped, so set up dummy bootstrap value return
  			ciLapseRate= data.frame(percent=c(-1,-1,-1,lapseMinMax[1],lapseMinMax[2]), bca=c(-1,-1,-1,lapseMinMax[1],lapseMinMax[2])) 
  		}  

		#pull confidence interval out of objects produced by boot.ci
		if (ciMethod=='perc') { #then confidence interval is in 'percent' field
  			ciMean <- ciMean$percent[4:5]
  			ciSlope <- ciSlope$percent[4:5]
  			ciLapseRate <- ciLapseRate$percent[4:5]
  		} else if (ciMethod=='bca') { #then confidence interval is in 'bca' field
  			ciMean <- ciMean$bca[4:5]
  			ciSlope <- ciSlope$bca[4:5]  	
  			ciLapseRate <- ciLapseRate$bca[4:5]
  		} else print('unexpected ciMethod')
  		print(c('ciMean$percent[4:5]=',ciMean,' ciSlope$percent[4:5]=',ciSlope))
  		
  		data.frame(meanLo=ciMean[1],meanHi=ciMean[2],slopeLo=ciSlope[1],slopeHi=ciSlope[2],
                 lapserateLo=ciLapseRate[1],lapserateHi=ciLapseRate[2])
  	}
  	return (fnToReturn)
}

makeMyMinMaxWorstCaseCurves<- function(myPlotCurve,iv) {
	fn2<-function(df) { 
		#calculate curves for factorial combination of the confidence interval parameters. Then, plot the most extreme of them all by assigning them to response.inf and response.sup
  		allCombos= expand.grid( mean=c(df$meanLo,df$meanHi), slope=c(df$slopeLo,df$slopeHi), 
                              lapseRate=c(df$lapserateLo,df$lapserateHi) )
  		allCombos$linkFx=df[1,"linkFx"] #needed by myPlotCurve
  		allCombos$method=df[1,"method"] #needed by myPlotCurve
      allCombos$chanceRate=df[1,"chanceRate"]
  		#print(c('allCombos=',allCombos))
  		worstCasePsychometrics= adply(allCombos,1,myPlotCurve)
  		minmaxCIpsychometrics= ddply(worstCasePsychometrics,iv, 
		     myMinMax<- function(df) { data.frame(lower=min(df$pCorr),
		  									                      upper=max(df$pCorr),
                                              linkFx=df[1,"linkFx"],
                                              method=df[1,"method"],
                                              chanceRate=df[1,"chanceRate"]) } )
		return(minmaxCIpsychometrics)
	}
	return (fn2)
}

library(PropCIs)
propCiForGgplot <- function(x,conf.int) { #confidence interval for a proportion
  numCorrect <- sum(x)
  numTrials <- length(x)
  CI <- blakerci(numCorrect,numTrials,conf.int) #Agresti-Coull, aka adjusted Wald method
  #Blaker, H. (2000). Confidence curves and improved exact confidence intervals for discrete distributions,
  #Canadian Journal of Statistics 28 (4), 783–798
  CI <- CI$conf.int
  triplet <- data.frame( y=numCorrect/numTrials, ymin=CI[1], ymax=CI[2] )
  return (triplet)
}

#shortcut to set ggplot options, by adding this to a ggplot object, e.g. g + themeAxisTitleSpaceNoGridLinesLegendBox
themeAxisTitleSpaceNoGridLinesLegendBox = theme_classic() + #Remove gridlines, show only axes, not plot enclosing lines
  theme(axis.line = element_line(size=.3, color = "grey"), 
        axis.title.y=element_text(vjust=0.24), #Move y axis label slightly away from axis
        axis.title.x=element_text(vjust=.10), #Move x axis label slightly away from axis
        strip.background = element_rect(fill="transparent",color=NA),
        legend.key = element_blank(), #don't put boxes around legend bits
        legend.background= element_rect(color="grey90"), #put big light grey box around entire legend
        panel.background = element_rect(fill = "transparent",colour = NA),
        plot.background = element_rect(fill = "transparent",colour = NA)   )
