#Variables expected:
#dat
#iv 
#maybe write a function that plots the psychometric functions for a dataset / experiment /criterion,
plotIndividDataAndCurves <- function(df,psychometricCurves) {
  #draw individual psychometric functions
  #to generalize below line, use aes_string
  g=ggplot(data= df,aes(x='Tilt',y=correct,color=factor(numTargets),shape=factor(separatnDeg)))
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

for ( expThis in sort(unique(dat$exp)) ) {  #draw individual Ss' data, for each experiment
  title<-paste('E',expThis,' individual Ss data',sep='')
  quartz(title,width=3,height=2.5) #,width=10,height=7)
  thisExpDat <- subset(dat,exp==expThis)
  g=ggplot(data= thisExpDat,aes(x=Tilt,y=correct,color=factor(startLeft)))
  g=g+stat_summary(fun.y=mean,geom="point", position=position_jitter(w=0.04,h=0),alpha=.95)
  g=g+facet_grid(. ~ subject)+theme_bw()
  #g<-g+ coord_cartesian( xlim=c(xLims[1],xLims[2]), ylim=yLims ) #have to use coord_cartesian here instead of naked ylim()
  show(g)
  #draw individual psychometric functions, for only one experiment  
  thisPsychometrics <- subset(psychometrics,exp==expThis)
  thisPsychometrics$correct = thisPsychometrics$pCorr 
  g=g+geom_line(data=thisPsychometrics)
  g=g+ geom_hline(mapping=aes(yintercept=chanceRate),lty=2)  #draw horizontal line for chance performance
  g=g+xlab(iv)+ylab('Proportion respLeftRight')
  #g=g+theme(panel.grid.minor=element_blank(),panel.grid.major=element_blank())# hide all gridlines.
  #g<- g+ theme(axis.title.y=element_text(size=12,angle=90),axis.text.y=element_text(size=10),axis.title.x=element_text(size=12),axis.text.x=element_text(size=10))
  g<-g+ scale_x_continuous(breaks=c(0.5,1.0,1.5,2.0,2.5),labels=c("0.5","","1.5","","2.5"))
  #g<-g+ scale_x_continuous(breaks=speeds)
  show(g)
  ggsave( paste('../figures/individPlotsE',expThis,'.png',sep='')  )
}
