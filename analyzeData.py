from psychopy.tools import filetools
import inspect
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
dataFileName="data/Hubert_spatiotopicMotion_15Dec2014_16-25_DataFrame.pickle"

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
print df
STOP
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
#dirTilt.groups  no groups, maybe because dataframe?
#dirTilt.select()
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

usePsychopy_ext = False
if usePsychopy_ext:
    #have to use psychopy_ext to aggregate
    ag = psychopy_ext.stats.aggregate(df, values="respLeftRight", cols="tilt") #, values=None, subplots=None, yerr=None, aggfunc='mean', order='natural')
    print "ag = \n", ag
    plt = psychopy_ext.plot.Plot()
    plt.plot(ag, kind='line')
    print "Showing plot with psychopy_ext.stats.aggregate"
    plt.show()

leftwardM = dirTilt.loc[False]
rightwardM = dirTilt.loc[True]
print 'leftwardM.index=', leftwardM.index
STOP
import pylab
#plot psychometric function on the right.
ax1 = pylab.subplot(121)
subplot_title = "leftward saccade"
pylab.text(0, 0.95, subplot_title, horizontalalignment='center', fontsize=12)
pylab.scatter(leftwardM.index, tiltMeans['respLeftRight'])

pylab.scatter(tiltMeans.index, tiltMeans['respLeftRight'])
#points = pylab.scatter(tiltMeans.index, tiltMeans['respLeftRight'], s=2, 
#    edgecolors=(0,0,0), facecolors= 'none', linewidths=1,
#    zorder=10, #make sure the points plot on top of the line
#    )
#pylab.ylim([-0.01,1.01])
#pylab.xlim([-2,102])
pylab.xlabel("tilt")
pylab.ylabel("proportion respond 'right'")
pylab.show()
#test function fitting
#show overcorrect proportion in right hand panel
subplot_title = "rightward saccade"
pylab.subplot(122)

