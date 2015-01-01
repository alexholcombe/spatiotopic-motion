#Variables expected:
#dat
#iv 
#maybe write a function that plots the psychometric functions for a dataset / experiment /criterion,
plotIndividDataAndCurves <- function(df,psychometricCurves) {
  #draw individual psychometric functions
  #to generalize below line, use aes_string
  g=ggplot(data= df,aes(x='tilt',y=correct,color=factor(numTargets),shape=factor(separatnDeg)))
  g=g+stat_summary(fun.y=mean,geom="point", position=position_jitter(w=0.04,h=0),alpha=.95)
  g=g+facet_wrap(separatnDeg ~ subject,ncol=8)+theme_bw()
  g
  
  #can't do this right now because depends on criterion
  # thisThreshes<- subset(threshesThisNumeric, exp==1)
  # threshLines <- ddply(thisThreshes,factorsPlusSubject,threshLine)
  # g<-g+ geom_line(data=threshLines,lty=3,size=0.9)  #,color="black") #emphasize lines so can see what's going on
  
  g<-g+ coord_cartesian( xlim=c(xLims[1],xLims[2]), ylim=yLims ) #have to use coord_cartesian here instead of naked ylim()
  g
  g=g+geom_line(data=psychometricCurves)
  g=g+ geom_hline(mapping=aes(yintercept=chanceRate),lty=2)  #draw horizontal line for chance performance
  g=g+xlab(iv)+ylab('Proportion Correct')
  g=g+theme(panel.grid.minor=element_blank(),panel.grid.major=element_blank())# hide all gridlines.
  g <- g+ theme(axis.title.y=element_text(size=12,angle=90),axis.text.y=element_text(size=10),axis.title.x=element_text(size=12),axis.text.x=element_text(size=10))
  g<-g+ scale_x_continuous(breaks=c(0.5,1.0,1.5,2.0,2.5),labels=c("0.5","","1.5","","2.5"))
  g		
}

library(PropCIs)
add4ciForGgplot <- function(x,conf.int) {
  numCorrect <- sum(x)
  numTrials <- length(x)
  CI <- blakerci(numCorrect,numTrials,conf.int) #Agresti-Coull, aka adjusted Wald method
  #Blaker, H. (2000). Confidence curves and improved exact confidence intervals for discrete distributions,
  #Canadian Journal of Statistics 28 (4), 783–798
  CI <- CI$conf.int
  triplet <- data.frame( y=numCorrect/numTrials, ymin=CI[1], ymax=CI[2] )
  return (triplet)
}

for ( expThis in sort(unique(dat$exp)) ) {  #draw individual Ss' data, for each experiment
  title<-paste('E',expThis,' individual Ss data',sep='')
  quartz(title,width=4,height=2.5) #,width=10,height=7)
  thisExpDat <- subset(dat,exp==expThis)
  g=ggplot(data= thisExpDat,aes(x=tilt,y=correct,color=factor(startLeft)))
  g=g+stat_summary(fun.y=mean,geom="point",alpha=.95)
  g=g+facet_grid(. ~ subject)+theme_bw()
  g=g+theme(panel.grid.minor=element_blank(),panel.grid.major=element_blank())# hide all gridlines.
  #g<-g+ coord_cartesian( xlim=c(xLims[1],xLims[2]), ylim=yLims ) #have to use coord_cartesian here instead of naked ylim()
  show(g)
  #draw individual psychometric functions, for only one experiment  
  thisPsychometrics <- subset(psychometrics,exp==expThis)
  thisPsychometrics$correct = thisPsychometrics$pCorr 
  g=g+geom_line(data=thisPsychometrics)
  g=g+ geom_hline(mapping=aes(yintercept=chanceRate),lty=2)  #draw horizontal line for chance performance
  g=g+xlab(iv)+ylab('Proportion respLeftRight')
  #g<- g+ theme(axis.title.y=element_text(size=12,angle=90),axis.text.y=element_text(size=10),axis.title.x=element_text(size=12),axis.text.x=element_text(size=10))
  #g<-g+ scale_x_continuous(breaks=c(0.5,1.0,1.5,2.0,2.5),labels=c("0.5","","1.5","","2.5"))
  g<-g+stat_summary(fun.data="add4ciForGgplot",geom="errorbar",conf.int=.685,size=.2, width=.12) 
  if (bootstrapTheFit) {
    worstCasePsychometricRegion$correct=.5 #in this df tp send to geom_ribbon, must have y-variable that was specified in initial call, otherwise ggplot tries to do something funky that results in an error
    g=g+geom_ribbon(data=worstCasePsychometricRegion,aes(x=tilt,ymin=lower,ymax=upper,color=NULL,fill=factor(startLeft)),alpha=0.2)
  }
  show(g)
  
  figTitle = paste("../figures/bySubjectE",expThis,sep='')
  if (length(unique(thisExpDat$subject))==1) #only one subject
    figTitle = paste(figTitle,unique(thisExpDat$subject)[1],sep='')
  ggsave( paste(figTitle,'.png',sep='')  )
}
