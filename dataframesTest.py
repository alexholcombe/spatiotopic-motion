from pandas import DataFrame
from psychopy import data

stimList=[]
stimList.append({'location': 3, 'startLeft':False, 'upDown': 1.0, 'tilt': -2.0, 'jitter': .65})
stimList.append({'location': 3, 'startLeft':False, 'upDown': 1.0, 'tilt': 2.0, 'jitter': .65})
blockReps = 2
trials = data.TrialHandler(stimList, blockReps)
thisTrial = trials.next()
print(thisTrial)
print(type(thisTrial)) #psychopy data trialType
fields = list(thisTrial) #column names, but not in the order we necessarily want
print(fields)

#The first trial. Create the DataFrame that will contain all the results
#df = DataFrame(thisTrial)
#df = DataFrame(dict(thisTrial)) 
#df = DataFrame(thisTrial, columns = fields) #doesn't work. have to specify index (rownames)
df = DataFrame(thisTrial, index=[1], #index is rowname
                            columns = ['jitter','location','startLeft','upDown','tilt']) #columns included purely to specify their order
df['resp']=1.0 #adds new column. If you use '1' instead of '1.0', makes it binary, which then can't take mean of 


#add the next trial
thisTrial = trials.next()
df= df.append( thisTrial, ignore_index=True ) #ignore because I got no index
df['resp'][1]=0.0
print(df)

#add the next trial
thisTrial = trials.next()
df= df.append( thisTrial, ignore_index=True )
df['resp'][2]=1.0
print(df)

#Use pandas to calculate proportion correct at each level
#The df.dtypes in my case are  "objects". I don't know what that is and you can't take the mean
df = df.convert_objects(convert_numeric=True) #convert dtypes from object to numeric

#print('df='); print(df) #debug
grouped = df.groupby('tilt')
print('grouped=')
print(grouped)
groupMeans= grouped.mean() #a groupBy object, kind of like a DataFrame but without column names, only an index?
tiltsTested = list(groupMeans.index)
pResp = list(groupMeans['resp'])  #x.iloc[:]
ns = grouped.sum() #want n per trial to scale data point size
ns = list(ns['resp'])
print('df mean at each tilt\n'); print(  DataFrame({'tilt': tiltsTested, 'pResp': pResp, 'n': ns })   )
#data point sizes. One entry in array for each datapoint
    
#def plotDataAndPsychometricCurve(staircase,fit,descendingPsycho,threshVal):
