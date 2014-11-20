from pandas import DataFrame
from psychopy import data

stimList=[]
stimList.append({'location': 3, 'startLeft':False, 'upDown': 1, 'tilt': -2, 'jitter': .65})
blockReps = 1
trials = data.TrialHandler(stimList, blockReps)
thisTrial = trials.next()
print(thisTrial)
print(type(thisTrial)) #psychopy data trialType
fields = list(thisTrial)
print(fields)
#df = DataFrame(thisTrial)
#df = DataFrame(dict(thisTrial)) 
#df = DataFrame(thisTrial, columns = fields) #doesn't work. have to specify index (rownames)
df = DataFrame(thisTrial, index=[1],
                            columns = ['jitter','location','startLeft','tilt','upDown']) #columns included purely to specify their order
df['respFwdBackslash']=1 #adds new column


df= DataFrame({'tilt': [-3], 'respFwdBackslash':[1]}, 
                            columns=['tilt','respFwdBackslash']) #specifying the column names just to specify their order

print(df)

df=df.append(  {'tilt':2,'respFwdBackslash':0}, ignore_index=True )

print(df)