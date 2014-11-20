from pandas import DataFrame

stimList=[]
stimList.append({'location': 3, 'startLeft':False, 'upDown': 1, 'tilt': -2, 'jitter': .65})

df= DataFrame({'tilt': [-3], 'respFwdBackslash':[1]}, 
                            columns=['tilt','respFwdBackslash']) #specifying the column names just to specify their order

print(df)

df=df.append(  {'tilt':2,'respFwdBackslash':0}, ignore_index=True )

print(df)