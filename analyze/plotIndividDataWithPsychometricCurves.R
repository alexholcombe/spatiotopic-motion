#Variables expected:
#dat
#iv 
#maybe write a function that plots the psychometric functions for a dataset / experiment /criterion,
plotIndividDataAndCurves <- function(dat,iv,factors,psychometricCurves=NULL,
                                     worstCasePsychometricRegion=NULL,threshes=NULL  ) {
  #factors must be a named list including names color, rows, columns
  #rows, columns can be ".", meaning nothing. Color can be absent, meaning dont give different colors
  #draw individual psychometric functions
  #thisExpDat$saccadeDir <- c("leftward","rightward")[ thisExpDat$startLeft + 1 ]
  g=ggplot(data= dat,aes_string(x=iv,y="correct",color=factors["color"]))  
  
  g=g+stat_summary(fun.y=mean,geom="point",alpha=.95) + theme_bw()
  #have to indicate colors when change legend values and name below 
  #colrs = ggplot_build(g)$data[[1]]$colour #returns colors auto-chosen by ggplot http://stackoverflow.com/questions/15130497/changing-ggplot-factor-colors
  #g=g+scale_color_manual(values=colrs[1:2],labels=c("leftward saccade","rightward saccade"),name="")
  if (factors["row"] != "." | factors["columns"] != ".") {
      facetString = paste(factors["rows"],"~",factors["columns"])
      g=g+facet_grid(facetString)
  }
  g=g+theme(panel.grid.minor=element_blank(),panel.grid.major=element_blank())# hide all gridlines.
  show(g)
  #draw individual psychometric functions, for only one experiment
  if (!is.null(psychometricCurves)) {
    psychometricCurves$correct = psychometricCurves$pCorr 
    g=g+geom_line(data=psychometricCurves)
    #g=g+ geom_vline(mapping=aes(xintercept=0),lty=2)  #draw horizontal line for chance performance
  }
  g=g+xlab(iv)+ylab('Rightward')
  #g<- g+ theme(axis.title.y=element_text(size=12,angle=90),axis.text.y=element_text(size=10),axis.title.x=element_text(size=12),axis.text.x=element_text(size=10))
  #g<-g+ scale_x_continuous(breaks=c(0.5,1.0,1.5,2.0,2.5),labels=c("0.5","","1.5","","2.5"))
  g<-g+stat_summary(fun.data="propCiForGgplot",geom="errorbar",conf.int=.685,size=.2, width=.12) 
  if (!is.null(worstCasePsychometricRegion)) {
    worstCasePsychometricRegion$correct=.5 #in this df tp send to geom_ribbon, must have y-variable that was specified in initial call, otherwise ggplot tries to do something funky that results in an error
    g=g+geom_ribbon(data=worstCasePsychometricRegion,aes_string(x=iv,ymin="lower",ymax="upper",
                                                    color=NULL,fill=factors["color"]),alpha=0.2)
    #g=g+scale_fill_manual(values=colrs[1:2],labels=c("leftward saccade","rightward saccade"),name="",
    #                      guide=FALSE)  #actually guide=FALSE doesnt prevent lines from being drawn  
  }
  
  if (!is.null(threshes)) { #plot threshLines
    xMin = min(psychometricCurves[,iv]) #assume that this represents leftmost point of graph. Theres a better
        #way to get xmin out of ggplot but I forget
    criterion = threshes[1,"criterion"] 
    if (length(unique(threshes$criterion)) >1) { warning("More than one criterion provided, dont know which to use")}
    calcThreshLine<- makeMyThreshLine(iv,threshColumnName="threshThisCrit",criterion=criterion,
                                      xMin=xMin, yMin=0) 
    threshLines <- ddply(threshesThis,unname(factors),calcThreshLine)
    g<-g+ geom_line(data=threshLines,lty=1,size=0.9)  #,color="black") #emphasize lines so can see what's going on
  }  
  
  show(g)
  return(g)
}