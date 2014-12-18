from psychopy import visual, data, logging, tools
import itertools
from math import log
from copy import deepcopy
import pandas as pd
from pandas import DataFrame
import pylab, scipy
import numpy as np
from calcUnderOvercorrect import calcOverCorrected

def agrestiCoull95CI(x, nTrials):
    #Calculate 95% confidence interval with Agresti-Coull method for x of nTrials
    #http://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval#Agresti-Coull_Interval
    nTilde = nTrials + 1.96**2
    pTilde = 1/nTilde*(x + 0.5*1.96**2)
    plusMinus = 1.96*np.sqrt(1/nTilde*pTilde*(1-pTilde))
    return pTilde - plusMinus, pTilde + plusMinus

def plotDataAndPsychometricCurve(df, dataFileName):
    """
    Plot data, and fit and plot psychometric curve
    If df is not None then get data from dataFileName
    """
    if df is None:
        if type(dataFileName) is not str:
            print 'dataFileName = ', dataFileName
            raise Exception("No df supplied and no string dataFileName supplied")
        if dataFileName.endswith('.pickle'):
            df = tools.filetools.fromFile(dataFileName)
        elif dataFileName.endswith('.txt'):
            df = pandas.read_csv(dataFileName, delimiter='\t')
        #Also need to be able to handle .psydat
        #dat = tools.filetools.fromFile(dataFileName) #<class 'psychopy.data.DataHandler'>
    if not isinstance(df, pd.core.frame.DataFrame):
        raise Exception("Don't have viable DataFrame still")

    if np.all(df.dtypes==object):
        raise Exception("I thought you'd give me some numbers to work with, but everything in this dataframe is an object")
    #Need to convert_
    
    #add overcorrect to cases where tilt==0
    tilt = df.loc[:,'tilt']
    neutralStimIdxs = (tilt==0)
    #print('neutralStimIdxs=\n',neutralStimIdxs)
    if len(neutralStimIdxs)>1:
      if neutralStimIdxs.any(): #Calculate over/under-correction, which is only interpretable when tilt=0
        forCalculatn = df.loc[neutralStimIdxs, ['tilt','startLeft','upDown','respLeftRight']]
        overCorrected = calcOverCorrected( forCalculatn )
        df['overCorrected']= np.nan
        df.loc[neutralStimIdxs, 'overCorrected'] = overCorrected
        
    #test plotting of data
    usePsychopy_ext = False
    if usePsychopy_ext:
        #have to use psychopy_ext to aggregate
        ag = psychopy_ext.stats.aggregate(df, values="respLeftRight", cols="tilt") #, values=None, subplots=None, yerr=None, aggfunc='mean', order='natural')
        print "ag = \n", ag
        plt = psychopy_ext.plot.Plot()
        plt.plot(ag, kind='line')
        print "Showing plot with psychopy_ext.stats.aggregate"
        plt.show()
        
    #dataframe aggregate
    grouped = df.groupby(['startLeft','tilt'])
    dirTilt = grouped.mean() #this is a dataframe, not a DataFrameGroupBy
    print "mean at each dir, tilt =\n", dirTilt
    print "dirTilt.index = ", dirTilt.index #there is no column called 'tilt', instead it's the actual index, kinda like row names
    # MultiIndex [(False, -0.4), (False, 0.0), (False, 0.4), (True, -0.4), (True, 0.0), (True, 0.4)]
    #dirTilt.groups  no groups, maybe because dataframe?
    
    dirTilt = dirTilt.reset_index() #flatten MultiIndex back into columns with rows (simple dataframe)
    leftwardM = dirTilt[ dirTilt['startLeft']==False ]
    rightwardM = dirTilt[ dirTilt['startLeft']==True ]
    
    ax1 = pylab.subplot(121)
    pylab.scatter(leftwardM['tilt'], leftwardM['respLeftRight'],
                          edgecolors=(1,0,0), facecolor=(1,0,0), label='leftward saccade')
    pylab.scatter(rightwardM['tilt'], rightwardM['respLeftRight'],
                          edgecolors=(0,1,0), facecolor=(0,1,0), label='rightward saccade')
    pylab.legend()
    print  str( round( 100*df['overCorrected'].mean(), 2) )
    msg = 'proportn overCorrected at 0 tilt = ' +  str( round( 100*df['overCorrected'].mean(), 2) ) + \
                      '% of ' + str( df['overCorrected'].count() ) + ' trials' 
    msg2= ' 95% Agresti-Coull CI = ' + \
                       str( np.round( agrestiCoull95CI(df['overCorrected'].sum(), df['overCorrected'].count()), 2) )
    pylab.text(0.52, 0.85, msg, horizontalalignment='left', fontsize=12)
    pylab.text(0.52,0.75, msg2, horizontalalignment='left', fontsize=12)
    
    #pylab.ylim([-0.01,1.01])
    pylab.xlabel("tilt")
    pylab.ylabel("proportion respond 'right'")
    
    #psychometric curve basics
    tiltMin = min( df['tilt'] )
    tiltMax = max( df['tilt'] )
    x = np.linspace(tiltMin, tiltMax, 50)
    
    #test function fitting
    #fit curve
    def logistic(x, x0, k):
         y = 1 / (1 + np.exp(-k*(x-x0)))
         return y
    def inverseLogistic(y, x0, k):
        linear = np.log ( y / (1-y) )
        #linear = -k*(x-x0)
        #x-x0 = linear/-k
        #x= linear/-k + x0
        x = linear/-k + x0
        return x
    
    #scipy.stats.logistic.fit
    paramsLeft = None; paramsRight = None
    try:
        paramsLeft, pcov = scipy.optimize.curve_fit(logistic, leftwardM['tilt'], leftwardM['respLeftRight'], p0 = [0, 6])
    except Exception as e:
        print 'leftward fit failed ', e
    try:
        paramsRight, pcov = scipy.optimize.curve_fit(logistic, rightwardM['tilt'], rightwardM['respLeftRight'], p0 = [0, 6])
    except Exception as e:
        print 'rightward fit failed ', e
    
    threshVal = 0.5
    pylab.plot([tiltMin, tiltMax],[threshVal,threshVal],'k--') #horizontal dashed line
    overCorrectAmts = list()
    if paramsLeft is not None:
        pylab.plot(x,  logistic(x, *paramsLeft) , 'r-')
        threshL = inverseLogistic(threshVal, paramsLeft[0], paramsLeft[1])
        print 'threshL = ', np.round(threshL, 2)
        overCorrectAmts.append(threshL)
        pylab.plot([threshL, threshL],[0,threshVal],'g--') #vertical dashed line
    if paramsRight is not None:
        pylab.plot(x,  logistic(x, *paramsRight) , 'g-')
        threshR = inverseLogistic(threshVal, paramsRight[0], paramsRight[1])
        print 'threshR = ', np.round(threshR, 2)
        overCorrectAmts.append(-1*threshR)
        pylab.plot([threshR, threshR],[0,threshVal],'g--') #vertical dashed line
        pylab.title('threshold (%.2f) = %0.3f' %(threshVal, threshR))
    if (paramsLeft is not None) and (paramsRight is not None):
        pylab.title('PSE (%.2f) = %0.3f & %0.3f' %(threshVal, threshL, threshR))
    if len(overCorrectAmts)==0:
        msg3= 'Failed both fits so cant tell you average over/under correction amount'
    else:
        msg3= 'Average tilt needed to compensate overcorrection\n (negative indicates undercorrection)\n = ' + str( np.round( np.mean(overCorrectAmts), 2) )
    pylab.text(0.52,0.55, msg3, horizontalalignment='left', fontsize=12, linespacing=2.0)
    pylab.show() #pauses until window manually closed
    return pylab.gcf() #return current figure
        
def plotStaircaseDataAndPsychometricCurve(fit,IV_name,DV_name,intensities,resps,descendingPsycho,threshCriterion):
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

if __name__=='__main__':  #Running this helper file, must want to test functions in this file
    #dataFileName = "data/Hubert_spatiotopicMotion_03Dec2014_15-49.psydat"
    dataFileName="data/Alex_spatiotopicMotion_15Dec2014_16-25_DataFrame.pickle"
    fig = plotDataAndPsychometricCurve(None, dataFileName)
    pylab.savefig('figures/Alex.jpg') #, bbox_inches='tight')

