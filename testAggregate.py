#after taking mean, get out multiindex
#Trying to understand how to access the content of a multiindex dataframe
#Summary, after its grouped you can only access by first dimension, or by entire group, and only with loc? 
import pandas as pd
from numpy.random import randn
df = pd.DataFrame({'A' : ['foo', 'bar', 'foo', 'bar'], #from http://pandas.pydata.org/pandas-docs/stable/groupby.html
                                 'B' : ['one', 'one', 'two', 'two'],
                                 'C' : [6,7,8,9], 
                                 'D' : [10,11,12,13]})
df['bar']
grouped = df.groupby(['A', 'B'])
grouped[('foo','two')]
grouped.loc['foo']
dfM = grouped.mean()
dfM.index.names # ['A','B']
dfM.index #multiIndex (u'bar', u'one'), (u'bar', u'two'), (u'foo', u'one'), (u'foo', u'two')
for x in dfM:
    print x #C, D
dfM[('foo','two')] #error

dfM['A'] #error
dfM.loc['foo'] #works!!
dfM.loc['one'] #doesnt work. apparently cant do it with second dimension of index
dfM.loc['foo','one'] #works!!

