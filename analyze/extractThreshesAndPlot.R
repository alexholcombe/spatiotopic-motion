#Intended to be called by doAllAnalyses.R, which 
#variables expected:
#factorsPlusSubject
#fitParms
#psychometrics
#function calcPctCorrThisIvVal
#iv
#varyLapseRate, lapseMinMax
infoMsg=paste0(iv,"-fit")

lapseMsg=""
if (!varyLapseRate)
  lapseMsg=paste("lapseRate always",unique(lapseMinMax))
#go point by point to find thresholds for each criterion for each factorsPlusSubject
worstLapseRate <- max(fitParms$lapseRate)
paste("Can't calculate threshold above criterion level of",1-worstLapseRate,"because that's the worst subject")
threshCriteria<- c(0.5) #seq(from=.67,to=maxCriterion,by=.06) #high thresholds
threshCriterion = round(threshCriteria,3) #because otherwise can include invisible 10^-21 diff which will trip you up later
threshes <- data.frame()
threshCriteriaThis = threshCriteria
threshCriteriaNotes = c("nothing special")
for (i in 1:length(threshCriteriaThis)) {
  threshCriterion = threshCriteriaThis[i]
  cat('Extracting thresh for criterion:',threshCriterion)
  #use point by point search to find the threshold. 
  myThreshGetNumeric= makeMyThreshGetNumerically(iv,threshCriterion)
  
  psychometricTemp<- psychometrics #subset(psychometrics,numObjects==numObjectsThis)
  #Don't do it where criterion corresponds to below chance
  
  threshesThisNumeric = ddply(psychometricTemp,factorsPlusSubject,myThreshGetNumeric) 
  threshesThisNumeric$criterion <- threshCriterion
  threshesThisNumeric$criterionNote <- threshCriteriaNotes[i]
  threshesThis<- merge(threshesThisNumeric,fitParms)
  threshes<- rbind(threshes, threshesThis)
}

themeAxisTitleSpaceNoGridLinesLegendBox = theme_classic() + #Remove gridlines, show only axes, not plot enclosing lines
  theme(axis.line = element_line(size=.3, color = "grey"), 
        axis.title.y=element_text(vjust=0.24), #Move y axis label slightly away from axis
        axis.title.x=element_text(vjust=.10), #Move x axis label slightly away from axis
        legend.key = element_blank(), #don't put boxes around legend bits
        legend.background= element_rect(color="grey90"), #put big light grey box around entire legend
        panel.background = element_rect(fill = "transparent",colour = NA),
        plot.background = element_rect(fill = "transparent",colour = NA)   )
##########Plot threshes, exp*subject*startLeft ################
tit=paste("individualSs_threshes_",infoMsg)
dv="thresh"
quartz(title=tit,width=4,height=3) #create graph of thresholds
h<-ggplot(data=subset(threshes,criterionNote=="nothing special"),
          aes(x=startLeft,y=thresh,color=factor(startLeft)))
h<-h+facet_grid(. ~ exp)  #facet_grid(criterion ~ exp)
h<-h+themeAxisTitleSpaceNoGridLinesLegendBox #theme_bw() 
#ylim(1.4,2.5) DO NOT use this command, it will drop some data
#h<-h+ coord_cartesian( xlim=c(xLims[1],xLims[2]), ylim=yLims ) #have to use coord_cartesian here instead of naked ylim()
h<-h+ geom_point() + geom_line() #plot individual lines for each subject
#h<-h+ggtitle("6,9 difft validates t.f. limit. Speed limits vary widely")
show(h)
ggsave( paste('figs/E1_startLeft/',tit,'.png',sep='') )

#Plot the slopes. I'm still getting insanely large slopes. Can I fit with something else?!
###########################################################

cat('I give you threshes')
###################################
#plot thresholds (at only one criterion level) for all 3 experiments at same time
# quartz()
# #tt<-subset(threshes,subject=="AH");  tt<-subset(tt,numTargets=="1")
# #tt$subject<-factor(tt$subject) #in case unused levels were the problem
# #h<-ggplot(data= fake, aes(x=separatnDeg,y=thresh))
# h<-ggplot(data= subset(threshes,numTargets!="2P"), aes(x=separatnDeg,y=thresh,color=numTargets,shape=exp))
# h<-h + facet_grid(exp~., scales="free") # ~criterion
# #h<-h+stat_summary(data=threshesThisNumeric,fun.data="mean_cl_boot",geom="errorbar",conf.int=.95,position=position_dodge(width=.2)) #error bar
# h<-h+stat_summary(fun.data="mean_cl_boot",geom="errorbar",conf.int=.95,position=position_dodge(width=.2)) #error bar
# h<-h+theme_bw() + xlab("Separation (deg)")
# #ylim(1.4,2.5) DO NOT use this command, it will drop some data
# #h<-h+ coord_cartesian( xlim=c(xLims[1],xLims[2]), ylim=yLims ) #have to use coord_cartesian here instead of naked ylim()
# #h<-h+coord_cartesian(ylim=c(1.4,2.6)) #have to use coord_cartesian here instead of naked ylim() to don't lose part of threshline
# h<-h+ stat_summary(fun.y=mean,geom="point") + stat_summary(fun.y=mean,geom="line") 
# h+theme(panel.grid.minor=element_blank(),panel.grid.major=element_blank())# hide all gridlines
# h<-h+ggtitle(paste(tit,lapseMsg))
# h
