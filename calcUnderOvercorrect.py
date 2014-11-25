from __future__ import print_function
from pandas import DataFrame
import numpy as np
#calculate whether under- or over-correcting
def calcOverCorrected(df):
    #Expect dataframes with fields tilt, startLeft, upDown, respFwdBackslash
    #Actually only can give legitimate answer when tilt is 0, because only that is an ambiguous stimulus
    #canonical case is startLeft, upDown, tilt 0
    #    1
    #A     B
    #    2
    #If you undercorrect, /  fwdSlash
    #startLeft mean target moves to right? So upDown undercorrect would be fwdslash
    startLeft = df['startLeft']
    upDown = df['upDown']
    respFwdBackslash= df['respFwdBackslash']
    overCorrected =  respFwdBackslash #tilde is bitwise NOT have to use it to apply operation to each element
    #for canonical case. backslash means overcorrect, fwdslash means undercorrect
    #any departure from canonical case inverts the answer. Use XOR (^) to invert conditional on another boolean.
    startLeft_not_canonical = ~ startLeft #startLeft = True is canonical case. So, flip otherwise
    overCorrected = overCorrected ^ startLeft_not_canonical
    upDown_not_canonical = ~ upDown #otherwise-canonical case gives backslash
    overCorrected =  overCorrected ^ upDown_not_canonical
    return overCorrected

data = {'tilt': [0,0,-2,-2], 'startLeft':[True, True,True,True], 'upDown':[True, True,True,False], 'respFwdBackslash':[False,True,True,True]}
df = DataFrame(data , #index=[nDone],
                            columns = ['tilt','startLeft','upDown','respFwdBackslash']) #columns included purely to specify their order
#forCalculatn = df.loc[neutralStimIdxs, ['tilt','startLeft','upDown','respFwdBackslash']]

#test with single record
overCorrected = calcOverCorrected(df.loc[0])
print('overCorrected=',overCorrected)
#test with multiple records
overCorrected = calcOverCorrected(df)
print('overCorrected=\n',overCorrected)

print('test with subset of records for which tilt==0')
tilt = df.loc[:,'tilt']
neutralStimIdxs = (tilt==0)
print( df.loc[neutralStimIdxs,:] )
overCorrected = calcOverCorrected( df.loc[neutralStimIdxs, :] )
print('neutralStimIdxs overCorrected=\n',overCorrected)

#add answer to original dataframe
df['overCorrected']=  None
print('dataframe with answer added=\n',df)
df.loc[neutralStimIdxs, ['overCorrected']] = overCorrected
print('dataframe with answer added=\n',df)
#Summarise under over correct
print('For 0 tilt, proportion of overcorrection responses=', df['overCorrected'].mean(skipna=True),
          ' out of ',df['overCorrected'].count(),' trials')

#grouped = df.groupby('intensity')
#groupMeans= grouped.mean() #a groupBy object, kind of like a DataFrame but without column names, only an index?
#intensitiesTested = list(groupMeans.index)
#pCorrect = list(groupMeans['response'])  #x.iloc[:]
#ns = grouped.sum() #want n per trial to scale data point size
#ns = list(ns['response'])
#print('df mean at each intensity\n'); print(  DataFrame({'intensity': intensitiesTested, 'pCorr': pCorrect, 'n': ns })   )
