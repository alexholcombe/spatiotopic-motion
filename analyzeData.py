from psychopy.tools import filetools
import inspect
import numpy as np
import psychopy_ext.stats
import psychopy_ext.plot
import pandas 
from calcUnderOvercorrect import calcOverCorrected

#grab some data outputted from my program, so I can test some analysis code
##The psydat file format is literally just a pickled copy of the TrialHandler object that saved it. You can open it with:
##dat = tools.filetools.fromFile(dataFileName)
#dataFileName = "data/Hubert_spatiotopicMotion_03Dec2014_15-49.psydat"
#dataFileName="data/Hubert_spatiotopicMotion_11Dec2014_13-00_DataFrame.pickle"
#dataFileName ="data/Hubert_spatiotopicMotion_15Dec2014_15-18_PSYCHOPY.txt"
dataFileName="data/Alex_spatiotopicMotion_15Dec2014_16-25_DataFrame.pickle"

if dataFileName.endswith('.pickle'):
    df = filetools.fromFile(dataFileName)
elif dataFileName.endswith('.txt'):
    df = pandas.read_csv(dataFileName, delimiter='\t')

print "type(df)=", type(df) # <class 'pandas.core.frame.DataFrame'>
print "df.dtypes=",df.dtypes #all "objects" for some reason
#strings in pandas pretty much objects. Dont know why can't force it to be a string, this is supposed to work http://stackoverflow.com/questions/22005911/convert-columns-to-string-in-pandas

#Now I can test aggregate
#dat.data seems to contain the columns I added
print "df.head=\n", df.head()

#add overcorrect to cases where tilt==0
tilt = df.loc[:,'tilt']
neutralStimIdxs = (tilt==0)
#print('neutralStimIdxs=\n',neutralStimIdxs)
if len(neutralStimIdxs)>1:
  if neutralStimIdxs.any(): #Calculate over/under-correction, which is only interpretable when tilt=0
    forCalculatn = df.loc[neutralStimIdxs, ['tilt','startLeft','upDown','respLeftRight']]
    overCorrected = calcOverCorrected( forCalculatn )
    print 'overCorrected=\n', overCorrected
    df['overCorrected']= np.nan
    df.loc[neutralStimIdxs, 'overCorrected'] = overCorrected
    
#test plotting of data
#dataframe aggregate
grouped = df.groupby('tilt')
tiltMeans = grouped.mean()
print "mean at each tilt =\n", tiltMeans
print "tiltMeans.index = ", tiltMeans.index #there is no column called 'tilt', instead it's the actual index, kinda like row names

grouped = df.groupby(['startLeft','tilt'])
for name in grouped: #this works
    print name
grouped.get_group((True, 0.4)) #combo of startLeft and tilt
print 'groups=', grouped.groups #works
dirTilt = grouped.mean() #this is a dataframe, not a DataFrameGroupBy
print "mean at each dir, tilt =\n", dirTilt
print "dirTilt.index = ", dirTilt.index #there is no column called 'tilt', instead it's the actual index, kinda like row names
# MultiIndex [(False, -0.4), (False, 0.0), (False, 0.4), (True, -0.4), (True, 0.0), (True, 0.4)]
#dirTilt.groups  no groups, maybe because dataframe?
#dirTilt = dirTilt.reset_index() #thanks Chris Said, except it *reduces* the number of cases that work below by one
try:
    print "dirTilt.loc[True]=\n", dirTilt.loc[True] #works!!!!
except: pass
try:
    print "dirTilt.loc[0.4]=\n", dirTilt.loc[0.4] #doesnt work I presume because second dimension
except: pass
try:
    print "dirTilt.loc[True, 0.4]=\n", dirTilt.loc[True, 0.4] #works!!!
except: pass
try:
    print "dirTilt.loc['True']=\n", dirTilt.loc['True'] #doesnt work
except: pass
try:
    print "dirTilt.loc['True','0.4']=\n", dirTilt.loc['True','0.4'] #doesnt work
except: pass
#dirTilt.select()
usePsychopy_ext = False
if usePsychopy_ext:
    #have to use psychopy_ext to aggregate
    ag = psychopy_ext.stats.aggregate(df, values="respLeftRight", cols="tilt") #, values=None, subplots=None, yerr=None, aggfunc='mean', order='natural')
    print "ag = \n", ag
    plt = psychopy_ext.plot.Plot()
    plt.plot(ag, kind='line')
    print "Showing plot with psychopy_ext.stats.aggregate"
    plt.show()

dirTilt = dirTilt.reset_index() #back into columns
leftwardM = dirTilt[ dirTilt['startLeft']==False ]
rightwardM = dirTilt[ dirTilt['startLeft']==True ]
print 'dirTilt=\n', dirTilt

import pylab
ax1 = pylab.subplot(121)
pylab.scatter(leftwardM['tilt'], leftwardM['respLeftRight'],
                      edgecolors=(1,0,0), facecolor=(1,0,0), label='leftward saccade')
pylab.scatter(rightwardM['tilt'], rightwardM['respLeftRight'],
                      edgecolors=(0,1,0), facecolor=(0,1,0), label='rightward saccade')
pylab.legend()
print  str( round( 100*df['overCorrected'].mean(), 2) )
msg = 'proportion overCorrected at 0 tilt = ' +  str( round( 100*df['overCorrected'].mean(), 2) ) + \
                  '% of ' + str( df['overCorrected'].count() ) + ' trials'
pylab.text(0.5, 0.55, msg, horizontalalignment='left', fontsize=12)

#pylab.ylim([-0.01,1.01])
#pylab.xlim([-2,102])
pylab.xlabel("tilt")
pylab.ylabel("proportion respond 'right'")

#test function fitting
#fit curve
import scipy
def logistic(x, x0, k):
     y = 1 / (1 + np.exp(-k*(x-x0)))
     return y
#scipy.stats.logistic.fit
popt, pcov = scipy.optimize.curve_fit(logistic, leftwardM['tilt'], leftwardM['respLeftRight'])
print 'parameters found by curve_fit = ', popt
tiltMin = min( df['tilt'] )
tiltMax = max( df['tilt'] )
x = np.linspace(tiltMin, tiltMax, 50)
y = logistic(x, *popt)

#thresh = fit.inverse(threshVal)
#print thresh

#plot curve
pylab.plot(x, y, 'k-')
#pylab.plot([thresh, thresh],[0,threshVal],'k--') #vertical dashed line
#pylab.plot([0, thresh],[threshVal,threshVal],'k--') #horizontal dashed line
#pylab.title('threshold (%.2f) = %0.3f' %(threshVal, thresh))
pylab.show()
