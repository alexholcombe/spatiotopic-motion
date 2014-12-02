import numpy as np
from psychopy import visual, data, logging
import itertools
from math import log
from copy import deepcopy
from pandas import DataFrame
import pylab, os
import numpy as np
from matplotlib.ticker import ScalarFormatter

def plotPsychometricCurve(fit,IV_name,DV_name,intensities,resps,descendingPsycho,threshCriterion)
    #Expects staircase, which has intensities and responses in it
    #May or may not be log steps staircase internals
    #Plotting with linear axes
    #Fit is a psychopy data fit object. Assuming that it couldn't handle descendingPsycho so have to invert the values from it
    #IV_name independent variable name
    #DV_name dependent variable name
    intensLinear= intensities
    if fit is not None:
        #generate psychometric curve
        intensitiesForCurve = np.arange(min(intensLinear), max(intensLinear), 0.01)
        thresh = fit.inverse(threshCriterion)
        if descendingPsycho:
            intensitiesForFit = 100-intensitiesForCurve
            thresh = 100 - thresh
        ysForCurve = fit.eval(intensitiesForFit)
        #print('intensitiesForCurve=',intensitiesForCurve)
        #print('ysForCurve=',ysForCurve) #debug
    if descendingPsycho:
        thresh = 100-thresh
    #plot staircase in left hand panel
    pylab.subplot(121)
    #plot psychometric function on the right.
    ax1 = pylab.subplot(122)
    figure_title = "threshold "
    if fit is None:
        figure_title += "unknown because fit was not provided"
    else:
        figure_title += 'threshold (%.2f) = %0.2f' %(threshCriterion, thresh) + '%'
        pylab.plot(intensitiesForCurve, ysForCurve, 'k-') #fitted curve
        pylab.plot([thresh, thresh],[0,threshCriterion],'k--') #vertical dashed line
        pylab.plot([0, thresh],[threshVal,threshCriterion],'k--') #horizontal dashed line
    #print thresh proportion top of plot
    pylab.text(0, 1.11, figure_title, horizontalalignment='center', fontsize=12)
    if fit is None:
        pylab.title('Fit failed')
    
    #Use pandas to calculate proportion correct at each level
    df= DataFrame({IV_name: intensLinear, DV_name: resps})
    #print('df='); print(df) #debug
    grouped = df.groupby(IV_name)
    groupMeans= grouped.mean() #a groupBy object, kind of like a DataFrame but without column names, only an index?
    intensitiesTested = list(groupMeans.index)
    pCorrect = list(groupMeans[DV_name])  #x.iloc[:]
    ns = grouped.sum() #want n per trial to scale data point size
    ns = list(ns[DV_name])
    print('df mean at each intensity\n'); print(  DataFrame({IV_name: intensitiesTested, 'pCorr': pCorrect, 'n': ns })   )
    #data point sizes. One entry in array for each datapoint

    pointSizes = 5+ 40 * np.array(ns) / max(ns) #the more trials, the bigger the datapoint size for maximum of 6
    #print('pointSizes = ',pointSizes)
    points = pylab.scatter(intensitiesTested, pCorrect, s=pointSizes, 
        edgecolors=(0,0,0), facecolors= 'none', linewidths=1,
        zorder=10, #make sure the points plot on top of the line
        )
    pylab.ylim([-0.01,1.01])
    pylab.xlim([-2,102])
    pylab.xlabel("%noise")
    pylab.ylabel("proportion correct")
    #save a vector-graphics format for future
    #outputFile = os.path.join(dataFolder, 'last.pdf')
    #pylab.savefig(outputFile)
    createSecondAxis = False
    if createSecondAxis: #presently not used, if fit to log would need this to also show linear scale
        #create second x-axis to show linear percentNoise instead of log
        ax2 = ax1.twiny()
        ax2.set(xlabel='%noise', xlim=[2, 102]) #not quite right but if go to 0, end up with -infinity? and have error
        #ax2.axis.set_major_formatter(ScalarFormatter()) #Show linear labels, not scientific notation
        #ax2 seems to be the wrong object. Why am I using pylab anyway? Matplotlib documentation seems more clear
        #for programming it is recommended that the namespaces be kept separate, http://matplotlib.org/api/pyplot_api.html
        #http://stackoverflow.com/questions/21920233/matplotlib-log-scale-tick-label-number-formatting
        ax2.set_xscale('log')
        ax2.tick_params(axis='x',which='minor',bottom='off')
        
#    #save figure to file
#    outputFile = os.path.join(dataDir, 'test.pdf')
#    pylab.savefig(outputFile)


#Test staircase functions
threshCriterion = 0.25
staircaseTrials = 5
staircase = data.QuestHandler(startVal = 95, 
                      startValSd = 80,
                      stopInterval= 1, #sd of posterior has to be this small or smaller for staircase to stop, unless nTrials reached
                      nTrials = staircaseTrials,
                      #extraInfo = thisInfo,
                      pThreshold = threshCriterion, #0.25,    
                      gamma = 1./26,
                      delta=0.02, #lapse rate, I suppose for Weibull function fit
                      method = 'quantile', #uses the median of the posterior as the final answer
                      stepType = 'log',  #will home in on the 80% threshold. But stepType = 'log' doesn't usually work
                      minVal=1, maxVal = 100
                      )
print('created QUEST staircase')

descendingPsycho = True
prefaceStaircaseNoise = np.array([5,95]) #will be recycled / not all used, as needed
corrEachTrial = list([1,0])
print('Importing responses ',np.array(corrEachTrial),' and intensities ',prefaceStaircaseNoise)
#Act of importing will cause staircase to log transform
#staircase internal will be i = log(100-x)
#-(10**i)-100
staircase.importData( toStaircase(prefaceStaircaseNoise,descendingPsycho), np.array(corrEachTrial) )
printStaircase(staircase, briefTrialUpdate=False, printInternalVal=True, alsoLog=False)