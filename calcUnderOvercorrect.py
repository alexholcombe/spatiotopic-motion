from __future__ import print_function
from pandas import DataFrame
import numpy as np
#calculate whether under- or over-correcting
def calcOverCorrected(df):
    #Expect dataframes with fields tilt, startLeft, upDown, respLeftRight
    #Actually only can give legitimate answer when tilt is 0, because only that is an ambiguous stimulus
    #canonical case is startLeft, upDown, tilt 0
    #    1
    #A     B
    #    2
    #If you undercorrect, ~respLeftRight
    #    1
    #B     A                  ~startLeft
    #    2
    #If you undercorrect, respLeftRight
    #    2
    #B     A                  ~startLeft, ~upDown
    #    1
    #If you undercorrect, respLeftRight.  upDown does not affect it
    if df.ndim==1:
        anyObjectsInThere = df[['upDown','startLeft']].dtype == 'object' #dtype for series
    elif df.ndim==2:
        anyObjectsInThere = (df[['upDown','startLeft']].dtypes == 'object').any() #dtypes for dataframe
    if anyObjectsInThere:
        print('ERROR: calcOverCorrected expects relevant columns to not be objects but instead something interpretable as boolean')
    startLeft = np.array( df['startLeft'] ) #make it a numpy array so can use its elementwise logical operators
    upDown = np.array( df['upDown'] )
    respLeftRight= np.array( df['respLeftRight'] )
    overCorrected = respLeftRight # np.logical_not( respLeftRight ) #elementwise not
    #for canonical case. backslash means overcorrect, fwdslash means undercorrect
    #any departure from canonical case inverts the answer. Use XOR (^) to invert conditional on another boolean.
    startLeft_not_canonical = np.logical_not( startLeft ) #startLeft = True is canonical case. So, flip otherwise
    overCorrected = np.logical_xor( overCorrected, startLeft_not_canonical )
    return overCorrected

if __name__=='__main__':  #Running this helper file, must want to test functions in this file
    data = {'tilt': [0,0,-2,-2,0], 'startLeft':[True, True,True,True,False], 'upDown':[True, True,True,False,False], 'respLeftRight':[False,True,True,True,False]}
    df = DataFrame(data , #index=[nDone],
                                columns = ['tilt','startLeft','upDown','respLeftRight']) #columns included purely to specify their order
    #forCalculatn = df.loc[neutralStimIdxs, ['tilt','startLeft','upDown','respLeftRight']]
    
    #test with single record
    overCorrected = calcOverCorrected(df.loc[4])
    print('single record\n ',df.loc[4],'overCorrected=',overCorrected)
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
    