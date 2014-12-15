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
dataFileName ="data/Hubert_spatiotopicMotion_15Dec2014_15-18_PSYCHOPY.txt"
if dataFileName.endswith('.pickle'):
    df = filetools.fromFile(dataFileName)
elif dataFileName.endswith('.txt'):
    df = pandas.read_csv(dataFileName, delimiter='\t')

print "type(df)=", type(df) # <class 'pandas.core.frame.DataFrame'>
print "df.dtypes=",df.dtypes #all "objects" for some reason
#strings in pandas pretty much objects. Dont know why can't force it to be a string, this is supposed to work http://stackoverflow.com/questions/22005911/convert-columns-to-string-in-pandas

df= df.convert_objects(convert_numeric=True) #Infers better dtype for object columns, such as float64. Otherwise they will all be "object" type
##Better would be to convert before saving as pickle inside psychopy
#Unfortunately, even strings get converted to numeric and if it cant be converted it becomes NaN 
#http://pandas.pydata.org/pandas-docs/dev/generated/pandas.DataFrame.convert_objects.html
#Actually seems it's not true, the below did not get converted from object
#objects has to be used for heterogeneous data

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
#NEED MORE REALISTIC DATA. RUN MYSELF
#Need more realistic data
plt = psychopy_ext.plot.Plot()
plt.plot(ag, kind='line')
plt.show()

#test function fitting

