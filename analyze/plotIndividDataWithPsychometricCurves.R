#Variables expected:
#dat
#iv 
#maybe write a function that plots the psychometric functions for a dataset / experiment /criterion,
plotIndividDataAndCurves <- function(dat,iv,psychometricCurves=NULL,worstCasePsychometricRegion=NULL,
                                     colorFactor=".",rowFactor=".",colFactor=".") {
  #draw individual psychometric functions
  #to generalize below line, use aes_string
  #thisExpDat$saccadeDir <- c("leftward","rightward")[ thisExpDat$startLeft + 1 ]
  g=ggplot(data= dat,aes_string(x=iv,y="correct",color=colorFactor))  
  g=g+stat_summary(fun.y=mean,geom="point",alpha=.95) + theme_bw()
  #have to indicate colors when change legend values and name below 
  #colrs = ggplot_build(g)$data[[1]]$colour #returns colors auto-chosen by ggplot http://stackoverflow.com/questions/15130497/changing-ggplot-factor-colors
  #g=g+scale_color_manual(values=colrs[1:2],labels=c("leftward saccade","rightward saccade"),name="")
  if (rowFactor != "." | colFactor != ".") {
      facetString = paste(rowFactor,"~",colFactor)
      g=g+facet_grid(facetString)
  }
  g=g+theme(panel.grid.minor=element_blank(),panel.grid.major=element_blank())# hide all gridlines.
  #g<-g+ coord_cartesian( xlim=c(xLims[1],xLims[2]), ylim=yLims ) #have to use coord_cartesian here instead of naked ylim()
  show(g)
  #draw individual psychometric functions, for only one experiment
  if (!is.null(psychometricCurves)) {
    psychometricCurves$correct = psychometricCurves$pCorr 
    g=g+geom_line(data=psychometricCurves)
    g=g+ geom_vline(mapping=aes(xintercept=0),lty=2)  #draw horizontal line for chance performance
  }
  g=g+xlab(iv)+ylab('Proportion respLeftRight')
  #g<- g+ theme(axis.title.y=element_text(size=12,angle=90),axis.text.y=element_text(size=10),axis.title.x=element_text(size=12),axis.text.x=element_text(size=10))
  #g<-g+ scale_x_continuous(breaks=c(0.5,1.0,1.5,2.0,2.5),labels=c("0.5","","1.5","","2.5"))
  g<-g+stat_summary(fun.data="propCiForGgplot",geom="errorbar",conf.int=.685,size=.2, width=.12) 
  if (!is.null(worstCasePsychometricRegion)) {
    worstCasePsychometricRegion$correct=.5 #in this df tp send to geom_ribbon, must have y-variable that was specified in initial call, otherwise ggplot tries to do something funky that results in an error
    #g=g+geom_ribbon(data=worstCasePsychometricRegion,aes(x=tilt,ymin=lower,ymax=upper,
    #                                                     color=NULL,fill=factor(startLeft)),alpha=0.2)
    g=g+geom_ribbon(data=worstCasePsychometricRegion,aes_string(x=iv,ymin="lower",ymax="upper",
                                                    color=NULL,fill=colorFactor,alpha=0.2))
    #g=g+scale_fill_manual(values=colrs[1:2],labels=c("leftward saccade","rightward saccade"),name="",
    #                      guide=FALSE)  #actually guide=FALSE doesnt prevent lines from being drawn  
  }
  show(g)
  return(g)
}


# figDir = "../figures/"
# rowFactor = "durWithoutProbe"
# colFactor = "subject"
# thisDat <- subset(dat,exp==1)
# figTitle = paste("E",expThis,"_",rowFactor,"_by_",colFactor,sep='')
# if (length(unique(thisDat$subject))==1) #only one subject
#   figTitle = paste(figTitle,unique(thisDat$subject)[1],sep='_')
# quartz(figTitle,width=2*length(unique(thisDat$subject)),height=2.5) #,width=10,height=7)
# g<-plotIndividDataAndCurves(thisDat,psychometricCurves=psychometrics,
#                          worstCasePychometricRegion=worstCasePsychometricRegion,rowFactor="durWithoutProbe",colFactor="subject")
#   
#   
# ggsave( paste(figDir,figTitle,'.png',sep='')  )