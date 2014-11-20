from pandas import DataFrame

df= DataFrame({'tilt': -3, 'response': 1})
print(df)
df.append(  {'tilt':2,'response':0}, )
print(df)