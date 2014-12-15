from psychopy.tools import filetools
import inspect
import psychopy_ext.stats
import psychopy_ext.plot
import pandas 

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

#test plotting of data
#dataframe aggregate
grouped = df.groupby('tilt')
groupedMeans = grouped.mean()
print "mean at each tilt =", groupedMeans

#have to use psychopy_ext to aggregate
ag = psychopy_ext.stats.aggregate(df, values="respLeftRight", cols="tilt") #, values=None, subplots=None, yerr=None, aggfunc='mean', order='natural')
print "ag = \n", ag
plt = psychopy_ext.plot.Plot()
plt.plot(ag, kind='line')
plt.show()

#test function fitting

