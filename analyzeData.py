from psychopy.tools import filetools
import inspect
import psychopy_ext

all_functions = inspect.getmembers(psychopy_ext, inspect.isfunction)
print all_functions
#grab some data outputted from my program, so I can test some analysis code
##The psydat file format is literally just a pickled copy of the TrialHandler object that saved it. You can open it with:
##dat = tools.filetools.fromFile(dataFileName)
#dataFileName = "data/Hubert_spatiotopicMotion_03Dec2014_15-49.psydat"
dataFileName="data/Hubert_spatiotopicMotion_11Dec2014_13-00_DataFrame.pickle"
dat = filetools.fromFile(dataFileName)
print "type(dat)=", type(dat) # <class 'pandas.core.frame.DataFrame'>
#Now I can test aggregate
#dat.data seems to contain the columns I added
dat.printAsText()

d= dat.data #<class 'psychopy.data.DataHandler'>

#test function fitting

#have to use psychopy_ext to aggregate
psychopy_ext.stats.aggregate(df, rows=None, cols=None, values=None, subplots=None, yerr=None, aggfunc='mean', unstacked=False, order='natural')